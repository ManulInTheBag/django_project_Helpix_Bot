from django.core.management.base import BaseCommand
from django.conf import settings
from ...models import Profile
from ...models import Message
import telebot
import requests
from requests.auth import HTTPBasicAuth
from base64 import b64encode
import xml.etree.ElementTree as ET

def request_device(devname, what, page):
	response = ''
	count = 0
	all_prs = requests.get('https://helpix.ru/cgi/tgbot/tg.pl?devname={}&what={}&page={}'.format(devname, what, page), auth = ('tgbot', 'mQYtIW_cc2w'))
	tree = ET.fromstring(all_prs.text)
	if what == 'getspecs':
		for child in tree:
			if not 'error' in child.tag:
				response = response + child.tag + ': ' + child.text.split('[')[2].split(']')[0] + '\n'
	for child in tree:
		if 'num' in child.tag:
			count = int(int(child.text)/10)
			response = response + "Page Count:" + str(count) + '\n'
		if 'video' in child.tag:
			response = response + child[0].text.split('[')[2].split(']')[0] + ' : ' + child[1].text.split('[')[2].split(']')[0] + '\n'
		if 'review' in child.tag:
			response = response + child[0].text.split('[')[2].split(']')[0] + ' : ' + child[1].text.split('[')[2].split(']')[0] + '\n'
	return response

def log_errors(f):

	def inner(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except Exception as e:

			error_message = f'Ошибка: {e}'
			print(error_message)
			raise e
	return inner

class Command(BaseCommand):
	help = 'Телеграм-бот'

	def handle(self, *args, **options):
		bot = telebot.TeleBot('1731097238:AAEoCdAjqNqI4enBpGAgWPjeL51Oxn5VGzY')

		@bot.message_handler(commands=['start'])
		def start_message(message):
			p, _ = Profile.objects.get_or_create(
				external_id=message.chat.id,
				defaults = {
					'name': message.from_user.username,
				}
				)
			m = Message(
				profile=p,
				text=message.text,
			)
			m.save()
			bot.send_message(message.chat.id, 'Привет. Напишите, что хотите найти: технические характеристики, список обзоров, список видео-обзоров, список цен. Формат запроса: первым словом пишете, что вам нужно (getvideos, getspecs, getreviews, цены пока недоступны, извините), вторым - номер страницы, третьим и далее - точное название модели.')

		@bot.message_handler(content_types=['text'])
		def send_text(message):
			p, _ = Profile.objects.get_or_create(
				external_id=message.chat.id,
				defaults = {
					'name': message.from_user.username,
				}
				)
			m = Message(
				profile=p,
				text=message.text,
			)
			m.save()
			if len(message.text.split(' ')) < 3:
				bot.send_message(message.chat.id, 'Похоже, формат запроса неверен. Давайте повторим: первым словом пишете, что вам нужно (getvideos, getspecs, getreviews, цены пока недоступны, извините), вторым - номер страницы, третьим и далее - точное название модели.')
				return
			for i in range(len(message.text.split(' '))):
				if i == 0:
					what = message.text.split(' ')[i]
				elif i == 1:
					page = message.text.split(' ')[i]
					try:
						test = int(page)
					except ValueError:
						bot.send_message(message.chat.id, 'Вместо числа для страницы ввели дичь. Не надо так.')
						return
				elif i == 2:
					requ = message.text.split(' ')[i]
				else:
					requ = requ + '+' + message.text.split(' ')[i]
			res = request_device(requ, what, page)
			if not res:
				res = 'Мы ничего не нашли. Используйте, пожалуйста, точные команды и названия моделей.'
			bot.send_message(message.chat.id, res)

		bot.polling()