import urllib.request
import os
import time
import telegram
from telegram.ext import CommandHandler
from telegram.ext import Updater
import threading
import logging
import pickle
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					 level=logging.INFO)
from bs4 import BeautifulSoup

chat_id_list = []


if os.path.exists("users.pk"):
		with open("users.pk", "rb") as f:
				chat_id_list = pickle.load(f)
				
def start_fun(bot, update):
	if update.message.chat_id not in chat_id_list:
		bot.send_message(chat_id=update.message.chat_id, text="Great you will be notified")
		print(update.message.chat_id)
		chat_id_list.append(update.message.chat_id)
		with open("users.pk", "wb") as f:
				pickle.dump(chat_id_list, f)
	else:
		bot.send_message(chat_id=update.message.chat_id, text="You are already in the list")

bot = telegram.Bot('insert_token')

def fetch_response(url):
	response = urllib.request.urlopen(url)
	page = str(response.read())
	soup = BeautifulSoup(page, 'html.parser')
	fetch_list = soup.find_all('span')
	name_list = []
	for item in fetch_list:
		try:
			name_list.append(str(item.contents[0]))
		except:
			pass
	return name_list

def write_content(content):
	with open("original.pkl","wb") as f:
		pickle.dump(content,f)

def get_content():
	with open("original.pkl", "rb") as f:
		return pickle.load(f)

write_content(fetch_response("http://results.unipune.ac.in/")) # initial write

def start_bot():
	updater = Updater(token='insert_token')
	dispatcher = updater.dispatcher
	start_handler = CommandHandler('start', start_fun)
	dispatcher.add_handler(start_handler)
	updater.start_polling()
	updater.idle()
	updater.stop()

def fetcher():
	start = time.time()
	while True:
		while int(time.time()-start) > 60:
			fetch = fetch_response("http://results.unipune.ac.in/")
			original = get_content()
			for row in fetch:
					if not row in original:
						print("New results added")
						for id in chat_id_list:
								bot.sendMessage(chat_id=id, text="New results updated: "+ str(row))
			write_content(fetch)
			start = time.time()

if __name__ == '__main__':
	t1 = threading.Thread(target=fetcher)
	t1.start()
	start_bot()
	t1.join()