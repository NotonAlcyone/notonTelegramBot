from telegram.ext import *
from privateData import *
from bs4 import BeautifulSoup
import random
import sqlite3
import time
import requests
import json
import threading
import datetime

updater = Updater(botToken)  # 업데이트 함수에 봇 토큰 저장
tempData = ""
dustData = ""
jobQueue = None

# bot = telegram.Bot(token = botToken)

"""
def get_message(bot, update) : #echo
	if update.message.chat.id in adminID:
		print(update.message.text)
		update.message.reply_text(update.message.text) #에코 데이터

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


def db_init():
	con = sqlite3.connect("player.db")
	cursor = con.cursor()
	cursor.execute(
		'CREATE TABLE IF NOT EXISTS chatMorningCallList'
		'("callIndex" INTEGER NOT NULL PRIMARY KEY ,"chatNumber"INTEGER NOT NULL,"morningCallTime"TEXT,"morningCallText"TEXT)'
	)
	cursor.execute('CREATE TABLE IF NOT EXISTS chatUTCData("chatID" INTEGER NOT NULL PRIMARY KEY, "utcData" INTEGER)')
	con.close()


def cmd_help(bot, update):  # /help 명령어 입력시 작동되는 함수
	update.message.reply_text("Private Bot System For NotonAlcyone")
	print(update.message.from_user.first_name)
	db_logger(str(update.message.text), "Return", update.message.from_user.id)


def cmd_dice(bot, update):  # /dice 명령어 입력시 작동되는 함수
	rand_num = random.randrange(1, 999)  # 1~999까지 랜덤 작동
	print(update.message.from_user.first_name)
	if rand_num % 10 in [0, 1, 3, 6, 7, 8]:  # 랜덤값의 마지막 자리에 따라서 조사 이,가 를 결정해줌
		post_position = "이"
	else:
		post_position = "가"
	bot.send_message(
		update.message.chat_id,
		update.message.from_user.first_name + "님께서 주사위를 굴려 🎲" + str(rand_num) + post_position + " 나왔습니다"
	)
	db_logger(str(update.message.text), str(rand_num), update.message.from_user.id)  # 로그 저장


def cmd_select(bot, update):  # /select 명령어 입력시 작동되는 함수
	input_text = update.message.text.split()  # 입력된 데이터 분리
	if len(input_text) == 1:  # argument 입력이 없는 경우
		bot.send_message(update.message.chat_id, "잘못된 메시지 입력입니다.")
		db_logger(str(update.message.text), "Select Fail", update.message.from_user.id)

	else:  # argument 입력이 있는 경우 해당 중 1개 선택
		chosen_data = input_text[random.randrange(1, len(input_text))]
		bot.send_message(update.message.chat_id, chosen_data)
		db_logger(str(update.message.text), chosen_data, update.message.from_user.id)


def cmd_log(bot, update):  # /log 명렁어 입력시 작동되는 함수
	if update.message.from_user.id in adminID:  # 입력자가 어드민일 경우에만 출력
		conn = sqlite3.connect("log.db")
		cursor = conn.cursor()	
		cursor.execute("SELECT * FROM commandLog ORDER BY commandServerTime DESC Limit 10")
		# 로그 기록 시간 기준으로 내림차순 정렬해서 10개를 출력
		log_data = cursor.fetchall()
		log_data.reverse()  # 가장 최근데이터가 상위에 있으므로, 보기 편하게 리버스
		line_break_data = ""
		for i in range(0, 10):
			line_break_data += str(log_data[i]) + " \n"
		bot.send_message(update.message.chat_id, line_break_data)
		db_logger(str(update.message.text), "recentLog * 10", update.message.from_user.id)
	else:  # 요청자가 어드민이 아닐 경우 출력
		bot.send_message(update.message.chat_id, "You are not admin")
		db_logger(str(update.message.text), "log Request rejected", update.message.from_user.id)
	

def cmd_weather(bot, update):
	try:
		weatherAnswer = cash_weather(False)  # weatherData에 데이터 요청
		bot.send_message(
			update.message.chat_id,
			"현재 서울 기온은 " + weatherAnswer[0] + "℃ 입니다.\n" +
			"미세먼지: " + weatherAnswer[1] + " 입니다." +
			"\n초미세먼지: " + weatherAnswer[2] + " 입니다."
		)
		db_logger(str(update.message.text), "날씨 데이터 조회 ", update.message.from_user.id)
	except:
		# 파싱중 오류 발생시 출력
		bot.send_message(update.message.chat_id, "날씨 데이터 조회 중 에러 발생")
		db_logger(str(update.message.text), "날씨 데이터 조회 실패", update.message.from_user.id)


def db_logger(command, answer, commandUser):
	
	conn = sqlite3.connect("log.db")
	cursor = conn.cursor()
	cursor.execute(
		'CREATE TABLE IF NOT EXISTS commandLog'
		'("commandType"TEXT NOT NULL,"commandServerTime"INTEGER NOT NULL,"commandAnswer"TEXT, "commandUser"INTEGER NOT NULL)'
	) # 해당 DB가 없을경우 삭제
	# print(cursor.fetchall())
	print("-------------------")
	print(command)
	print(answer)
	
	input_log = (command, int(time.time()), answer, commandUser)
	cursor.execute("INSERT INTO commandLog VALUES(?,?,?,?)", input_log)
	conn.commit()
	conn.close()


def cash_weather(is_init):
	global tempData
	global dustData
	if is_init is False:
		if tempData == "" or dustData == "": # 초기화 콜이 아니고, 데이터가 비어있을때 파싱
			tmp = parser_weather()
			tempData = tmp[0]
			dustData = tmp[1]
			threading.Timer(dataCashingTime, cash_weather, [True]).start()  # 캐싱 타임 이후 캐싱데이터 초기화
			return tempData[0].text, dustData[0].text, dustData[1].text

		else:
			return tempData[0].text, dustData[0].text, dustData[1].text

	else:  # 캐싱 데이터 초기화
		tempData = ""
		dustData = ""


def parser_weather():  # 네이버 날씨 파싱
	naver_weather_response = requests.get(naverWeatherURL)
	naver_weather_data = BeautifulSoup(naver_weather_response.text,'html.parser')
	temp_data = naver_weather_data.select("span.todaytemp")
	dust_data = naver_weather_data.select("dl.indicator dd")
	return temp_data, dust_data


def db_get_data(is_where, db_name, query, data_insert=None):
	con = sqlite3.connect(db_name)
	cursor = con.cursor()
	if is_where is True:
		cursor.execute(query, data_insert)
		return_data = cursor.fetchall()
	else:
		cursor.execute(query)
		return_data = cursor.fetchall()
	con.close()
	return return_data


def db_edit_data(db_name, query, data_insert):
	con = sqlite3.connect(db_name)
	cursor = con.cursor()
	cursor.execute(query, data_insert)
	con.commit()
	con.close()


def cmd_add_daily_call(bot, update):
	try:
		input_text = update.message.text.split()
		input_time = datetime.datetime.strptime(input_text[1], '%H:%M') # 1차 변환 시도
		call_text = ""
		for i in range(2, len(input_text)):
			call_text += str(input_text[i]) + " "
		db_edit_data(
			"player.db", "INSERT INTO chatMorningCallList  VALUES(?,?,?,?)",
			(update.update_id, update.message.chat.id, input_text[1], call_text)
		)
		db_edit_data("player.db", "INSERT OR IGNORE INTO chatUTCData VALUES(?,?)", (update.message.chat.id, 0))  # UTC db 전송
		# print(
		# getDBData(False,"player.db","SELECT callIndex FROM chatMorningCallList order by callIndex desc limit 1")[0][0]
		# )
		job_add(update.update_id)

		bot.send_message(update.message.chat_id, "정상적으로 Call이 등록되었습니다.")
		db_logger(str(update.message.text), "Call 등록 성공", update.message.from_user.id)
	except:
		bot.send_message(update.message.chat_id, "Call 등록 실패")
		db_logger(str(update.message.text), "Call 등록 실패", update.message.from_user.id)


def job_add(job_index):
	global jobQueue
	insert_data = (job_index,)
	db_data = db_get_data(
		True,
		"player.db", "SELECT chatNumber, morningCallTime  FROM chatMorningCallList WHERE callIndex = ? ",
		insert_data
	)
	chat_number = (db_data[0][0],)
	call_time = datetime.datetime.strptime(db_data[0][1], '%H:%M')
	print(call_time)
	chat_utc = db_get_data(True, "player.db", "SELECT utcData FROM chatUTCData where chatID = ?", chat_number)
	message_time = call_time - datetime.timedelta(hours= chat_utc[0][0])

	print(message_time.time())
	jobQueue = updater.job_queue.run_daily(job_exe, time=message_time.time(), name=str(job_index))


def delete_job(job_name, is_hard_delete):
	global jobQueue
	try:
		if is_hard_delete is True:
			db_edit_data("player.db", "DELETE FROM chatMorningCallList where callIndex = ?", (job_name,))
		jobQueue.job_queue.get_jobs_by_name(str(job_name))[0].schedule_removal()
	except:
		print("삭제 실패")
		print(job_name)


def job_exe(bot, job):
	insert_data = (job.name,)
	call_data = db_get_data(True, "player.db", "SELECT chatNumber,morningCallText FROM chatMorningCallList WHERE callIndex = ? ", insert_data)
	call_text = call_data[0][1]
	call_id = call_data[0][0]
	print("job call")
	print(job.name)
	bot.send_message(call_id, call_text)


def cmd_del_call(bot, update):
	del_list = db_get_data(
		True,
		"player.db", "SELECT callIndex From chatMorningCallList where chatNumber = ?",
		(update.message.chat_id,)
	)
	for i in range(0, len(del_list)):
		delete_job(del_list[i][0], True)


def cmd_set_utc(bot, update):
	utc_set_data = update.message.text.split()
	print(utc_set_data[1])
	try:
		if int(utc_set_data[1]) in range(-12,14):
			utc_update = (update.message.chat.id,utc_set_data[1])
			db_edit_data("player.db", "INSERT OR REPLACE INTO chatUTCData VALUES(?,?)", utc_update)
			# delList = getDBData(
			# True,"player.db","SELECT callIndex From chatMorningCallList where chatNumber = ?",
			# (update.message.chat_id,)
			# )
			# for i in range(0,len(delList)):
			# delete_job(delList[i][0],False)
			# for i in range(0,len(delList)):
			# addJob(delList[i][0])

		else:
			bot.send_message(update.message.chat_id,"UTC 범위(-12~14) 의 숫자가 아닙니다.")
	except:
		bot.send_message(update.message.chat_id,"잘못된 입력입니다.")


# call 목록 불러오기
# call 삭제 (DB 삭제 + 현재 액티브 삭제)
# UTC 세팅
# 콜 이니셜라이저
#
"""
def callBackDaily(bot, job):
	print("am i call?")
	print(job.name)
	#job.schedule_removal()
	#test(job)
	#bot.send_message(adminID[0],"좋은 아침입니다. 결핵약 챙겨드시고, 하루 일과를 확인해주세요.")

def test(bot, job):
	job.job_queue.get_jobs_by_name("15151")[0].schedule_removal()

	print("jobjob")
"""
# def addMorningCall():

# def deleteMorningCall():

# def loadMorningCall(isAll):
# 시작할때 전체 로드랑, ADD 모닝콜에서 왔을때 맨 마지막거 로드

# j = updater.job_queue.run_daily(callBackDaily, time = datetime.datetime.strptime('23:00', '%H:%M').time() )
# 서버시간 UTC 임 아아아아아아ㅏ악
# j = updater.job_queue.run_repeating(callBackDaily, interval = 3, name = "15151")
# j = updater.job_queue.run_repeating(test, interval = 3, name = "131313")


# updater.dispatcher.add_handler(MessageHandler(Filters.text, get_message))
# updater.dispatcher.add_handler(MessageHandler(Filters.chat(adminID[0]), getAdmin))
db_init()
cmdHelp = CommandHandler(["help", "HELP"], cmd_help)
cmdDice = CommandHandler(["dice", "DICE"], cmd_dice)
cmdSelect = CommandHandler(["select", "Select"], cmd_select)
cmdWeather = CommandHandler(["weather", "Weather"], cmd_weather)
cmdLog = CommandHandler(["log", "LOG"], cmd_log)
cmdAddCall = CommandHandler("addCall", cmd_add_daily_call)
cmdSetUtc = CommandHandler("setUTC", cmd_set_utc)
cmdDelJob = CommandHandler("delCall", cmd_del_call)
updater.dispatcher.add_handler(cmdHelp)
updater.dispatcher.add_handler(cmdDice)
updater.dispatcher.add_handler(cmdSelect)
updater.dispatcher.add_handler(cmdLog)
updater.dispatcher.add_handler(cmdWeather)
updater.dispatcher.add_handler(cmdAddCall)
updater.dispatcher.add_handler(cmdSetUtc)
updater.dispatcher.add_handler(cmdDelJob)

updater.start_polling(timeout=3, clean=True)
updater.idle()