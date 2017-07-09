#!/usr/bin/python3

import praw
import os
import logging.handlers
import time
import sys
import configparser
import signal
import discord
import asyncio

### Config ###
LOG_FOLDER_NAME = "logs"
SUBREDDIT = "default"
USER_AGENT = "default (by /u/Watchful1)"
LOOP_TIME = 15
CONFIG_FILE_NAME = "config.ini"
DISCORD_OWNER = "Watchful1#8126"
REDDIT_OWNER = "Watchful1"

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


async def close_bot(source):
	await send_message("Bot closed: "+source)
	quit()


def signal_handler(signal, frame):
	log.info("Handling interupt")
	close_bot("sigint")

signal.signal(signal.SIGINT, signal_handler)

log.debug("Connecting to reddit")

once = False
debug = False
user = None
if len(sys.argv) >= 2:
	user = sys.argv[1]
	for arg in sys.argv:
		if arg == 'once':
			once = True
		elif arg == 'debug':
			debug = True
else:
	log.error("No user specified, aborting")
	sys.exit(0)


try:
	r = praw.Reddit(
		user
		,user_agent=USER_AGENT)
except configparser.NoSectionError:
	log.error("User "+user+" not in praw.ini, aborting")
	sys.exit(0)


async def main():
	while True:
		startTime = time.perf_counter()
		log.debug("Starting run")

		log.info("Logged into reddit as /u/" + str(r.user.me()))

		log.debug("Run complete after: %d", int(time.perf_counter() - startTime))
		if once:
			break

		await asyncio.sleep(LOOP_TIME)


client = discord.Client()
botname = "default"
channel = -1
config = configparser.ConfigParser()
config.read(CONFIG_FILE_NAME)
if "discord" not in config:
	config.add_section("discord")
if not config.has_option("discord", "token"):
	token = input("Enter discord token: ")
	config.set("discord", "token", token)
	cfgfile = open(CONFIG_FILE_NAME, 'w')
	config.write(cfgfile)
	cfgfile.close()
	log.debug("Saved bot token")


@client.event
async def on_ready():
	global botname
	global channel
	botname = client.user.name
	log.debug("Logged into discord as "+botname)

	if "discord" in config and config.has_option("discord", "channel"):
		channel = client.get_channel(config.get("discord", "channel"))
		await client.send_message(channel, 'Bot started')

		class DiscordHandler(logging.Handler):
			def __init__(self):
				logging.Handler.__init__(self)

			def emit(self, record):
				asyncio.ensure_future(send_message(record.message), loop=asyncio.get_event_loop())

		logging.handlers.DiscordHandler = DiscordHandler
		discord_stderrHandler = logging.handlers.DiscordHandler()
		discord_formatter = logging.Formatter('%(levelname)s: %(message)s')
		discord_stderrHandler.setFormatter(discord_formatter)
		log.addHandler(discord_stderrHandler)


@client.event
async def on_message(message):
	if str(message.author) == DISCORD_OWNER:
		log.debug(message.content)
		if message.content == "!activate "+botname:
			config.set("discord", "channel", str(message.channel.id))
			cfgfile = open(CONFIG_FILE_NAME, 'w')
			config.write(cfgfile)
			cfgfile.close()

			await client.send_message(message.channel, "Activated in channel: "+str(message.channel))

		elif message.content == "!status":
			await client.send_message(message.channel, "Running")

		elif message.content == "!stop":
			await close_bot("discord")


async def send_message(message):
	await client.send_message(channel, message)


client.loop.create_task(main())
client.run(config.get("discord","token"))

