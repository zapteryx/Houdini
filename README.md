# Houdini
A Club Penguin private server written in Python for the AS2 protocol.

### Not ready for production.

## Prerequisites
* Python 2.7+
* Twisted
* SQLAlchemy
* MySQL driver
* Redis
	* MacOS and Linux users can use a package manager (e.g. Homebrew or apt) to install the Redis service.
	* If you're on Windows, you can download the Redis installer [here](https://github.com/MicrosoftArchive/redis/releases).
* Watchdog
* bcrypt

## Installation
After you've installed the latest version of Python 2, navigate to the Houdini directory and run `pip install -r requirements.txt` in your command prompt or terminal.

### Windows
If you're on Windows you'll need to download and install MySQL Connector C 6.0.2 from [here](http://dev.mysql.com/downloads/connector/c/6.0.html#downloads) prior to installing the mysql module. __Be sure to check the extra binaries option through the custom installation.__

## Configuration
All configuration settings are located in Houdini.conf.

## Status
The server is currently incomplete and likely to be unstable **as well as buggy**. More handlers and bug fixes will be implemented as development continues.

You can find a comprehensive to-do list [here](https://trello.com/b/IM8STj1S).
