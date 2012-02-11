#!/bin/python3

import socket
import os
import time
import sys
import threading
#from os import fork
from Connection import ircServer

server     = [ "irc.freenode.net", [ "#raspberrypi-bots" ]]
bot_nick   = "dragonBot"
pluginList = [ "Plugin", "QnAPlugin" ]
execList   = [ ]
connection = ircServer( server[0], server[1], bot_nick )
running    = True

def close():
        print("Closing connections...")
        connection.close()
        if pid:
                exit(0)
        else:
                exit(0)

for plug in pluginList:
	try:
		plugins = __import__(plug, globals(), locals(), [], -1)
		execList.append(plugins)
	except ImportError as ie:
		print("Module " + plug  + " does not exist. Error: " , ie)

class recieveThread( threading.Thread ):
	def run(self):
		while running == True:
			response = connection.server_response()
			if response:
				message = connection.parse_message( response[0] )
				messageArgs = message.split(" ")
				nick = messageArgs[0]
				channel = response[1][2]
				if channel != bot_nick:
					for plug in execList:
						#print(execList)
						if plug.Plugin.handeler in message[len(messageArgs[0])+1:]:
							if plug.Plugin.method == "string":
								connection.send_message(plug.Plugin.ircPlug(nick, message, "13:31", channel), channel)
							elif plug.Plugin.method == "args":
								connection.send_message(plug.Plugin.ircPlug(nick, messageArgs, "13:31", channel), channel)
						else:
							print("%s" % message[len(messageArgs[0])+1:])
class shellThread( threading.Thread ):
	def run(self):
		running = True
		while running == True:
			userInput = input(bot_nick + "Shellv0.2 > ")
			userArgs = userInput.split(" ")
			if userArgs[0] == "load" and len(userArgs) > 1:
				try:
					plugin = __import__(userArgs[1], globals(), locals(), [], -1)
					execList.append(plugin)
					print("Successfully loaded")
				except ImportError:
					print("Module does not exist.")
			elif userArgs[0] == "unload" and len(userArgs) > 1:
				try:
					execList.pop(int(userArgs[1]))
					print("Unloaded.")
				except Exception as e:
					print("Module not loaded. Error type: ", e)
			elif userArgs[0] == "modules":
				counter = 0
				for item in execList:
					print( "%3s | %s " % ( counter, item ))
					counter += 1
			elif userArgs[0] == "help":
				print("Help.")
			elif userArgs[0] == "post" and len(userArgs) > 1:
				connection.send_message(userInput[len(userArgs[1])+6:], userArgs[1])
				print("Sent message.")
			elif userArgs[0] == "quit":
				running = False
			elif len(userInput) > 0: 
				print("Unknown command. ('help' maybe?)")

try:
	running = True
	shell    = shellThread()
	getStuff = recieveThread()

	shell.setName( bot_nick + "Shell" )
	getStuff.setName( bot_nick + "Recieve" )

	getStuff.start()
	shell.start()

except KeyboardInterrupt as e:
	connection.raw_message("QUIT :wtfisthiscrap982374")
	print("\nError: ", e)
	running = False