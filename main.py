#!/usr/bin/python3

import praw
import os
import logging.handlers
import time
import sys
import configparser
import signal

### Config ###
LOG_FOLDER_NAME = "logs"
SUBREDDIT = "default"
USER_AGENT = "default (by /u/Watchful1)"
LOOP_TIME = 15*60

### Logging setup ###
LOG_LEVEL = logging.DEBUG
if not os.path.exists(LOG_FOLDER_NAME):
    os.makedirs(LOG_FOLDER_NAME)
LOG_FILENAME = LOG_FOLDER_NAME+"/"+"bot.log"
LOG_FILE_BACKUPCOUNT = 5
LOG_FILE_MAXSIZE = 1024 * 256

log = logging.getLogger("bot")
log.setLevel(LOG_LEVEL)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
log_stderrHandler = logging.StreamHandler()
log_stderrHandler.setFormatter(log_formatter)
log.addHandler(log_stderrHandler)
if LOG_FILENAME is not None:
	log_fileHandler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=LOG_FILE_MAXSIZE, backupCount=LOG_FILE_BACKUPCOUNT)
	log_formatter_file = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	log_fileHandler.setFormatter(log_formatter_file)
	log.addHandler(log_fileHandler)


def signal_handler(signal, frame):
	log.info("Handling interupt")
	sys.exit(0)

log.debug("Connecting to reddit")

once = False
debug = False
if len(sys.argv) > 1 and sys.argv[1] == 'once':
	for arg in sys.argv:
		if arg == 'once':
			once = True
		elif arg == 'debug':
			debug = True

config = configparser.ConfigParser()
config.read('oauth.ini')

r = praw.Reddit(
	'Watchful1BotTest'
	,user_agent=USER_AGENT)

signal.signal(signal.SIGINT, signal_handler)

while True:
	startTime = time.perf_counter()
	log.debug("Starting run")

	log.info("Logged into reddit as /u/"+str(r.user.me()))

	log.debug("Run complete after: %d", int(time.perf_counter() - startTime))
	if once:
		break
	time.sleep(LOOP_TIME)
