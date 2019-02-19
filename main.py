from telegram.ext import *
from privateData import *
import random
import sqlite3
import time



updater = Updater(botToken)
 

"""
def get_message(bot, update) : #echo
	if update.message.chat.id in adminID:
		print(update.message.text)
		update.message.reply_text(update.message.text) #에코 데이터\

	else:
		print("---------Warn---------")
		print(update.message.text)
		print(update.message.chat.id)
		print("---------Warn---------")
		update.message.reply_text(noPermissionWarn)
"""
"""
def getAdmin(bot,update): # admin answer
	update.message.reply_text("adminSay")
"""
def helpCMD(bot,update):
	update.message.reply_text("Private Bot System For NotonAlcyone")
	print(update.message.from_user.first_name)
	logDB(str(update.message.text),"Return",update.message.from_user.id)

def diceCMD(bot,update):
	randNum = random.randrange(1,999)
	print(update.message.from_user.first_name)
	if randNum % 10 in [0,1,3,6,7,8]:
		postPostion = "이"
	else:
		postPostion = "가"
	bot.send_message(update.message.chat_id,update.message.from_user.first_name + "님께서 주사위를 굴려 🎲" +str(randNum)+ postPostion +" 나왔습니다")
	logDB(str(update.message.text),str(randNum),update.message.from_user.id)
	#update.message.reply_text(tmpDef.first_name+" "+tmpDef.last_name+ "님께서 주사위를 굴려 🎲" +str(randNum)+ postPostion +" 나왔습니다") 

def selectCMD(bot, update):
	afterData = update.message.text.split()
	if len(afterData) == 1:
		bot.send_message(update.message.chat_id,"wrongMessage Input")
		logDB(str(update.message.text),"Select Fail",update.message.from_user.id)

	else:
		tmpData = afterData[random.randrange(1,len(afterData))]
		bot.send_message(update.message.chat_id,tmpData)
		logDB(str(update.message.text),tmpData,update.message.from_user.id)

def logCMD(bot,update):
	if update.message.from_user.id in adminID:	
		conn = sqlite3.connect("log.db")
		cursor = conn.cursor()	
		cursor.execute("SELECT * FROM commandLog ORDER BY commandServerTime DESC Limit 10")
		logData = cursor.fetchall()
		logData.reverse()
		lineBreakData = ""
		for i in range(0,10):
			lineBreakData += str(logData[i]) + " \n"
		bot.send_message(update.message.chat_id,lineBreakData)
		logDB(str(update.message.text),"recentLog * 10",update.message.from_user.id)
	else:
		bot.send_message(update.message.chat_id,"You are not admin")
		logDB(str(update.message.text),"log Request rejected",update.message.from_user.id)
	

def logDB(command,answer,commandUser):
	
	conn = sqlite3.connect("log.db")
	cursor = conn.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS commandLog("commandType"TEXT NOT NULL,"commandServerTime"INTEGER NOT NULL,"commandAnswer"TEXT, "commandUser"INTEGER NOT NULL)') #해당DB가 없을경우 삭제
	#print(cursor.fetchall())
	print("-------------------")
	print(command)
	print(answer)

	#print(commandUser)
	#print("INSERT INTO commandLog VALUES('"+str(command)+"'," + str(int(time.time())) + ",'"+str(answer)+"',"+str(commandUser)+")")

	cursor.execute("INSERT INTO commandLog VALUES('"+str(command)+"', " + str(int(time.time())) + ",'"+str(answer)+"', "+str(commandUser)+")")
	#print("dose is on")
	conn.commit()
	conn.close()

#updater.dispatcher.add_handler(MessageHandler(Filters.text, get_message))
#updater.dispatcher.add_handler(MessageHandler(Filters.chat(adminID[0]), getAdmin))
cmdHelp = CommandHandler(["help","HELP"],helpCMD)
cmdDice = CommandHandler(["dice","DICE"],diceCMD)
cmdSelect = CommandHandler(["select","Select"],selectCMD)
cmdLog = CommandHandler(["log","LOG"],logCMD)
updater.dispatcher.add_handler(cmdHelp)
updater.dispatcher.add_handler(cmdDice)
updater.dispatcher.add_handler(cmdSelect)
updater.dispatcher.add_handler(cmdLog)

updater.start_polling(timeout=3, clean=True)
updater.idle()