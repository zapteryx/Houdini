import sys
config = {
	"Database": {
		"Address": "localhost",
		"Username": "root",
		"Password": "",
		"Name": "Houdini",
		"Driver": "PyMySQL" if sys.platform == "win32" else "MySQLdb"
	},
	"Redis": {
		"Address": "127.0.0.1",
		"Port": 6379
	},
	"Servers": {
		"Login": {
			"Address": "127.0.0.1",
			"Port": 6112,
			"World": False,
			"Plugins": [
			    "Example"
			],
			"Logging": {
				"General": "logs/login.log",
				"Errors": "logs/login-errors.log",
				"Level": "INFO"
			},
			"LoginFailureLimit": 5,
			"LoginFailureTimer": 3600
		},
		"Wind": {
		    "Id": "100",
			"Address": "127.0.0.1",
			"Port": 9875,
			"World": True,
			"Capacity": 200,
			"CacheExpiry": 3600,
			"Plugins": [
				"Commands",
				"Bot",
				"Rank"
			],
			"Logging": {
				"General": "logs/wind.log",
				"Errors": "logs/wind-errors.log",
				"Level": "DEBUG"
			}
		}
	},
	"Tables": {
	    "Four": [
	        { "RoomId": 220, "Tables": [205, 206, 207] },
	        { "RoomId": 221, "Tables": [200, 201, 202, 203, 204] }
	    ],
	    "Mancala": [
	        { "RoomId": 111, "Tables": [100, 101, 102, 103, 104] }
	    ],
	    "Treasure": [
	        { "RoomId": 422, "Tables": [300, 301, 302, 303, 304, 305, 306, 307] }
	    ]
	},
	"Waddles": {
	    "Sled": [
	        { "RoomId": 230, "Waddles": [
                { "Id": 100, "Seats": 4 },
                { "Id": 101, "Seats": 3 },
                { "Id": 102, "Seats": 2 },
                { "Id": 103, "Seats": 2 }
            ]}
	    ],
	    "Card": [
	        { "RoomId": 320, "Waddles": [
                { "Id": 200, "Seats": 2 },
                { "Id": 201, "Seats": 2 },
                { "Id": 202, "Seats": 2 },
                { "Id": 203, "Seats": 2 }
            ]}
	    ],
	    "CardFire": [
	        { "RoomId": 812, "Waddles": [
                { "Id": 300, "Seats": 2 },
                { "Id": 301, "Seats": 2 },
                { "Id": 302, "Seats": 3 },
                { "Id": 303, "Seats": 4 }
            ]}
	    ]
	},
	"Treasure": {
		"Food": [115, 114, 109, 112, 110, 105, 113, 106, 108, 107, 111, 128],
		"Furniture": [305, 313, 504, 506, 500, 503, 501, 507, 505, 502, 616, 542, 340, 150, 149, 369, 370, 300],
		"Clothing": [3028, 232, 412, 112, 184, 1056, 6012, 118, 774, 366, 103, 498, 469, 1082,
                     5196, 790, 4039, 326, 105, 122, 5080, 111],
		"Gold": {
			"Clothing": [2139, 2137, 5385, 3185, 5384, 5386, 6209, 2138, 1735, 3186, 1734, 2136, 4994, 4993, 3187],
			"Furniture": [2132, 2131, 2130, 2129]
		},
		"BorderTabby": {
			"Clothing": [24073, 24075, 24078, 24074, 24080, 24076, 24081,
						 24071, 24072, 24077, 24079, 24070, 4414, 122],
			"Furniture": [2180, 2182, 2183]
		},
		"Dinosaur": {
			"Clothing": [24031, 24030, 24033, 24029],
			"Furniture": [2180, 2182, 2183]
		}
	}
}