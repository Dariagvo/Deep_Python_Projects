from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import datetime
import re
from bs4 import BeautifulSoup

TOKEN = '5886309452:AAGl6FcZw4ZAI_Mq11eta-F2kQ1Jpr1u5XE'
bot = Bot(TOKEN)
dp = Dispatcher(bot)

help_text = "Привет! Добавь бота в чат и он сможет выполнить указанные ниже действия.\n" \
            "Статистика предоставляется по количеству пользователей и количеству админов"

comments_help_text = "Нажмите /data и введите две даты в формате\n\n" \
                     "DD MM YEAR DD MM YEAR\n" \
                     "одним сообщением"

com_list = ["start", "site", "разБАн", "тише!", "БАн", "Повысить его!"]


async def add_to_dict(res, rating):
    for elem in res:
        if elem in rating:
            new_c = int(rating.pop(elem))
            rating[elem] = new_c + 1
        else:
            rating[elem] = 1
    return rating


async def comments_info_by_time(date_1, date_2) -> list:
    rating = {}
    date_3 = date_1
    while date_3 <= date_2:
        info = requests.get(
            'https://panorama.pub/news/' + str(date_3.day) + '-' + str(date_3.month) + '-' + str(date_3.year)).text
        soup_info = BeautifulSoup(info, 'html.parser')
        root = soup_info.find("body")
        for a in root.find_all('a'):
            link = a.get('href')
            pattern = re.compile(r'\d{2}-\d{2}-\d{4}')
            if a.get('href') is not None and 'http' not in a.get('href') and 'news/' in a.get('href') and not re.search(
                    pattern, link):
                link_2 = 'https://panorama.pub' + link
                news_link_now = requests.get(link_2).text
                soup_news_now = BeautifulSoup(news_link_now, 'html.parser')
                for k in soup_news_now.find_all('div', class_=["mt-4 py-4 px-2"]):
                    res = set()
                    for comment in k.find_all('strong', itemprop=["author"]):
                        try:
                            if len(next(comment.stripped_strings)) > 2:
                                name = next(comment.stripped_strings)
                                res.add(name)
                        except StopIteration:
                            break
                    if res != set():
                        rating = await add_to_dict(res, rating)
        date_3 += datetime.timedelta(days=1)
    rating = dict(sorted(rating.items(), key=lambda item: item[1], reverse=True))

    if len(rating) <= 10:
        ans = rating.keys()
    else:
        ans = list(rating.keys())[:5]
    return ans


@dp.message_handler(commands=['site'])
async def button_message(message):
    markup = InlineKeyboardMarkup(row_width=2)
    item_1 = InlineKeyboardButton('Держи сайт', url='https://vk.com/daria_gvo')
    markup.add(item_1)
    await bot.send_message(message.chat.id, 'Возьмите ссылочку, пожалуйста!', reply_markup=markup)


@dp.message_handler(commands=['data'])
async def button_message(message):
    await bot.send_message(message.chat.id, 'Введите дату(будет долго думать)')


@dp.message_handler(commands=['start'])
async def button_message(message: types.Message):
    username = message.from_user.username
    markup = InlineKeyboardMarkup(row_width=2)
    item_1 = InlineKeyboardButton('Помощник для чата', callback_data='want_admin')
    item_2 = InlineKeyboardButton('Новости Панорамы', callback_data='panorama')
    markup.add(item_1, item_2)
    await message.reply(f"Привет, {username}!", reply_markup=markup)


@dp.callback_query_handler()
async def callback(call):
    if __name__ == '__main__':
        if call.message:
            if call.data == 'want_admin':
                markup = InlineKeyboardMarkup(row_width=2)
                item_1 = InlineKeyboardButton('Сделать админом', callback_data='promote')
                item_2 = InlineKeyboardButton('Получить статистику', callback_data='stata')
                item_3 = InlineKeyboardButton('Забанить пользователя', callback_data='ban')
                item_4 = InlineKeyboardButton('Разбанить пользователя', callback_data='unban')
                item_5 = InlineKeyboardButton('Заставить бота уйти :( ', callback_data='leave')
                item_6 = InlineKeyboardButton('Замьютить коллегу', callback_data='mute')
                markup.add(item_1, item_2, item_6, item_3, item_4, item_5)
                await bot.send_message(call.message.chat.id, text=help_text, reply_markup=markup)

            if call.data == 'panorama':
                panorama_markup = InlineKeyboardMarkup(row_width=2)
                item_1 = InlineKeyboardButton('Топ-5 комментаторов', callback_data='comments')
                item_2 = InlineKeyboardButton('Моя любимая новость', callback_data='fav_news')
                panorama_markup.add(item_1, item_2)
                await bot.send_message(call.message.chat.id, text=help_text, reply_markup=panorama_markup)

            if call.data == 'comments':
                await bot.send_message(call.message.chat.id, text=comments_help_text)

            if call.data == 'fav_news':
                markup = InlineKeyboardMarkup(row_width=2)
                item_1 = InlineKeyboardButton('Моя любимая новость',
                                              url='https://panorama.pub/news/'
                                                  'deputaty-gosudarstvennoj-dumy-budut-podtverzdat')
                markup.add(item_1)
                await bot.send_message(call.message.chat.id, 'Возьмите ссылочку, пожалуйста!', reply_markup=markup)

            if call.data == 'stata':
                admins_count, members_count = 0, 0
                for each in await bot.get_chat_administrators(call.message.chat.id):
                    admins_count += 1
                members_count = bot.get_chat_members_count(call.message.chat.id)
                await bot.send_message(call.message.chat.id, f"Вот вам статистика: \n "
                                                             f"администраторов в чате {admins_count} "
                                                             f"\n участников чата {members_count}")
            if call.data == 'promote':
                await bot.send_message(call.message.chat.id, 'Ответьте на сообщение будущего администратора фразой\n'
                                                             '"Повысить его!"')
            if call.data == 'ban':
                await bot.send_message(call.message.chat.id, 'Ответьте на сообщение того, кого мы баним фразой\n'
                                                             '"БАн"')
            if call.data == 'unban':
                await bot.send_message(call.message.chat.id, 'Ответьте на сообщение того, кого мы разбаним фразой\n'
                                                             '"разБАн"')

            if call.data == 'mute':
                await bot.send_message(call.message.chat.id, 'Много болтает.... Ответьте на его сообщение\n'
                                                             '"тише!"')

            if call.data == 'leave':
                await bot.send_message(call.message.chat.id, 'why..........://')
                await bot.leave_chat(call.message.chat.id)


@dp.message_handler(content_types=['text'])
async def message_reply(message):
    if message.text == "Повысить его!":
        await bot.promote_chat_member(message.chat.id, message.from_user.id, )
        await bot.send_message(message.chat.id, 'user is now an admin')

    if message.text == "БАн":
        await bot.ban_chat_member(message.chat.id, message.from_user.id)
        await bot.send_message(message.chat.id, f'User {message.from_user.id} was banned')

    if message.text == "тише!":
        await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id,
                                       types.ChatPermissions(False), until_date=(datetime.now() + timedelta(days=1)))
        await bot.send_message(message.chat.id, 'Помолчит сутки, а там посмотрим')

    if message.text == "разБАн":
        await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        link = bot.create_chat_invite_link(message.chat.id)
        await bot.send_message(message.chat.id, f'User was unbanned. He can now come back via invitation link: {link}')

    else:
        date = message.text
        if len(date) > 1:
            pattern = re.compile(r'\d{2} \d{2} \d{4} \d{2} \d{2} \d{4}')
            if re.fullmatch(pattern, message.text):
                date = message.text.split(' ')
                date_1 = datetime.date(int(date[2]), int(date[1]), int(date[0]))
                date_2 = datetime.date(int(date[5]), int(date[4]), int(date[3]))
                res = await comments_info_by_time(date_1, date_2)
                c_1 = res[0]
                c_2 = res[1]
                c_3 = res[2]
                c_4 = res[3]
                c_5 = res[4]
                await bot.send_message(message.chat.id, text=f"Вот ТОП-5 комментаторов:\n {c_1} \n {c_2} \n "
                                            f"{c_3} \n, {c_4} \n, {c_5} \n")
        else:
            panorama_markup = InlineKeyboardMarkup(row_width=2)
            item_1 = InlineKeyboardButton('Топ-5 комментаторов', callback_data='comments')
            item_2 = InlineKeyboardButton('Моя любимая новость', callback_data='fav_news')
            panorama_markup.add(item_1, item_2)
            await bot.send_message(message.chat.id, text=f"Ничего вам не скажу, вы дату неверно пишете",
                                   reply_markup=panorama_markup)


@dp.message_handler(content_types=["new_chat_members"])
async def user_joined(message: types.Message):
    await message.answer("Как называют невысокого человека, который волнуется?")


if __name__ == '__main__':
    executor.start_polling(dp)
