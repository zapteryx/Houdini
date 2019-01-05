from sqlalchemy import func, and_

from Houdini.Handlers import Handlers, XT
from Houdini.Data.Redemption import PenguinRedemption, RedemptionBook

validBookIds = [1,2,4,6,7,8,9,10,11,12,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]

@Handlers.Handle(XT.GetBookQuestion)
@Handlers.Throttle(2)
def handleGetBookQuestion(self, data):
    if data.Book not in validBookIds:
        return self.sendError(710)

    if data.Book in self.redeemedBookIds:
        return self.sendError(711)

    question = self.session.query(RedemptionBook).filter_by(BookID=data.Book).order_by(func.rand()).first()

    self.bookQuestionAttempts = 0

    self.sendXt("rgbq", question.QuestionID, data.Book, question.Page, question.Line, question.WordNumber)

@Handlers.Handle(XT.SendBookAnswer)
@Handlers.Throttle(2)
def handleSendBookAnswer(self, data):
    if data.Book not in validBookIds:
        return self.sendError(710)

    if data.Book in self.redeemedBookIds:
        return self.sendError(711)

    self.bookQuestionAttempts += 1
    if self.bookQuestionAttempts >= 5:
        return self.sendError(713)

    answer = self.session.query(RedemptionBook.Word) \
            .filter(and_(RedemptionBook.BookID == data.Book,RedemptionBook.QuestionID == data.QuestionID)) \
            .scalar()

    if data.Answer == answer:
        if data.Book == 23:
            item = 14608
            self.addItem(14608, sendXt=False)
        elif data.Book == 24:
            item = 13054
            self.addItem(13054, sendXt=False)
        else:
            if 15007 not in self.inventory:
                item = 15007
                self.addItem(15007, sendXt=False)
            else:
                item = ""

        self.user.Coins += 1500
        self.sendXt("rsba", item, 1500)
        self.session.add(PenguinRedemption(PenguinID=self.user.ID, CodeID=data.Book))
        self.redeemedBookIds.append(data.Book)
    else:
        return self.sendError(712)
