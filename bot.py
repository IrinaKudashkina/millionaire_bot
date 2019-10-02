import telebot
import requests
import random
import re
import os
from telebot import types
from my_const import *
from score_functions import *

api_url = 'https://stepik.akentev.com/api/millionaire'
token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)
states = {}
level = {}
correct_answers = {} 
answers = {}

@bot.message_handler(func=lambda message:states.get(message.from_user.id, MAIN_STATE) == MAIN_STATE)
def main_handler(message):
    if message.from_user.id not in level:
        level[message.from_user.id] = '1'
    if message.from_user.id not in score:
        score[message.from_user.id] = {'victories': 0, 'defeats': 0}  
    if 'вопрос' in message.text.lower():
        response = requests.get(
            api_url,
                params={'complexity': level[message.from_user.id]}
        ).json()
        correct_answers[message.from_user.id] = response['answers'][0]
        answers[message.from_user.id] = response['answers']
        random.shuffle(answers[message.from_user.id])
        random.shuffle(answers[message.from_user.id])
        question = str(response['question']) + ': '
        for i in answers[message.from_user.id]:
            question += str(i)+'; '
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True, selective=True)
        buttons = []
        for answer in answers[message.from_user.id]:
            buttons.append(types.KeyboardButton(answer))
        markup.add(*buttons)
        bot.send_message(message.from_user.id, question[:-2], reply_markup=markup)
        states[message.from_user.id] = QUESTION_STATE
    elif message.text == '/start':
        bot.send_message(message.from_user.id, 'Это бот-игра в "Кто хочет стать миллионером"')
        bot.send_message(message.from_user.id, 'Я умею задавать интересные вопросы, менять уровень сложности игры и показывать счёт')
        score[message.from_user.id] = {'victories': 0, 'defeats': 0}
    elif 'привет' in message.text.lower():
        bot.send_message(message.from_user.id, 'Ну привет, ' + message.from_user.first_name + '!')
    elif ('уровень' in message.text.lower()) or ('сложност' in message.text.lower()):
        markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True, selective=True)
        kb1 = types.KeyboardButton('уровень 1')
        kb2 = types.KeyboardButton('уровень 2')
        kb3 = types.KeyboardButton('уровень 3')
        markup.add(kb1, kb2, kb3)
        bot.send_message(message.from_user.id, 'Текущий уровень сложности ' + level[message.from_user.id] + '. Выберите новый уровень сложности: уровень 1; уровень 2; уровень 3', reply_markup=markup)
        states[message.from_user.id] = COMPLEXITY_STATE
    elif re.search(r'сч\wт', message.text.lower()):
        bot.send_message(message.from_user.id, 'victories: ' + str(score[message.from_user.id]['victories']) + ' / ' + 'defeats: '  + str(score[message.from_user.id]['defeats']))
    else:
        bot.reply_to(message, 'Я тебя не понял')

@bot.message_handler(func=lambda message:states.get(message.from_user.id, MAIN_STATE) == QUESTION_STATE)
def question(message):
    if message.text == correct_answers[message.from_user.id]:
        bot.send_message(message.from_user.id, 'Правильно!')
        victories(message.from_user.id, int(level[message.from_user.id]))
        states[message.from_user.id] = MAIN_STATE
    elif message.text in answers[message.from_user.id] and message.text != correct_answers[message.from_user.id]:
        bot.send_message(message.from_user.id, 'Неправильно:( Правильный ответ: ' + correct_answers[message.from_user.id])
        defeats(message.from_user.id, 1)
        states[message.from_user.id] = MAIN_STATE
    else:
        bot.reply_to(message, 'Я тебя не понял')

@bot.message_handler(func=lambda message:states.get(message.from_user.id, MAIN_STATE) == COMPLEXITY_STATE)
def complexity(message):
    if message.text == 'уровень 1':
        bot.send_message(message.from_user.id, 'Ok! Будут лёгкие вопросы:)')
        level[message.from_user.id] = '1'
        states[message.from_user.id] = MAIN_STATE
    elif message.text == 'уровень 2':
        bot.send_message(message.from_user.id, 'Будут вопросы средней сложности и двойные очки за победу!')
        level[message.from_user.id] = '2'
        states[message.from_user.id] = MAIN_STATE
    elif message.text == 'уровень 3':
        bot.send_message(message.from_user.id, 'Будут сложные вопросы и тройные очки за победу!')
        level[message.from_user.id] = '3'
        states[message.from_user.id] = MAIN_STATE
    else:
        bot.reply_to(message, 'Я тебя не понял')
   
bot.polling()
