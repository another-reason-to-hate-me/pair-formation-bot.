import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton 
import cfg
import json
import datetime
import os
import signal
import subprocess
import utilities
import markups

bot = telebot.TeleBot(cfg.token)

with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
    participants_list = json.load(file_import)

usernames_list = []
chat_id_username_dict = {}
get_index_list = []
sent_req_dict = {}
first_message_id_dict = {}
chat_id_surname_dict = {}
chat_id_list = []
user_agreement_status_dict = {}
chat_id_dict = {}
surnames_list = []

@bot.message_handler(commands = ['start']) 
def start(message):
    response_text = 'Перед использованием бота, пожалуйста, прочтите пользовательское соглашение.'
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = 'Пользовательское соглашение',
            url = cfg.user_agreement_url
            )
    )
    markup.row(
        InlineKeyboardButton(
            text = 'Руководство (n/a)',
            url = cfg.user_manual_url
            )
    )
    markup.row(
        InlineKeyboardButton(
            text = 'Исходный код (n/a)',
            url = cfg.source_code_url
            )
    )
    markup.row(
        InlineKeyboardButton(
            text = 'Я прочитал(-а) и согласен(-сна) с Пользовательским соглашением',
            callback_data = 'agree'
            )
    )
    bot.send_message(
        message.chat.id,
        text = response_text,
        reply_markup = markup
    )

@bot.callback_query_handler(func = lambda call: call.data == 'agree')
def username_check(call):
    with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
        participants_list = json.load(file_import)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    username = call.from_user.username
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = 'Пользовательское соглашение',
            url = cfg.user_agreement_url
            )
    )
    markup.row(
        InlineKeyboardButton(
            text = 'Руководство',
            url = cfg.user_manual_url
            )
    )
    markup.row(
        InlineKeyboardButton(
            text = 'Исходный код (n/a)',
            url = cfg.source_code_url
            )
    )
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = markup
    )
    try:
        user_agreement_status_dict.update({chat_id: 'agree'})
        try:
            i = utilities.get_index(chat_id, 0)
            response_text = f'Вы {participants_list[i][2]} {participants_list[i][3]}?'
            bot.send_message(
                chat_id,
                response_text = response_text,
                reply_markup = markups.auth_confirmation_btns()
            )
        except:
            i = utilities.get_index(username, 4)
            response_text = f'Вы {participants_list[i][2]} {participants_list[i][3]}?'
            bot.send_message(
                chat_id,
                text = response_text,
                reply_markup = markups.auth_confirmation_btns()
            )
    except:
        for i in range(len(participants_list)):
            usernames_list.append(participants_list[i][4])
        response_text = f'username {username} не найден.'
        bot.send_message(
            chat_id,
            text = response_text,
            reply_markup = markups.auth_confirmation1()
        )

@bot.callback_query_handler(func = lambda call: call.data == 'auth_send_to_dev')
def auth_manual_bugreport(call):
    chat_id = call.message.chat.id
    username = call.from_user.username
    message_id = call.message.message_id
    auth_send_br = bot.send_message(
        chat_id,
        text = 'Укажите свою фамилию, чтобы вас могли внести в список. Вам ответят, когда внесут в список участников.'
    )
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    utilities.logscreate(chat_id, username, 'auth_manual_bugreport')
    bot.register_next_step_handler(auth_send_br, sending_message_to_admin)

@bot.callback_query_handler(func = lambda call: call.data == 'auth_confirmed')
def auth_confirm(call):
    with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
        participants_list = json.load(file_import)
    chat_id = call.message.chat.id
    username = call.from_user.username
    message_id = call.message.message_id
    i = utilities.get_index(username, 4)
    participants_list[i][0] = chat_id
    participants_list[i][1] = user_agreement_status_dict[chat_id]
    with open('data/db.json', 'w', encoding = 'utf-8') as file_export:
        json.dump(participants_list, file_export, ensure_ascii = False, indent = 4)
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    bot.edit_message_text(
        chat_id = chat_id,
        message_id = message_id,
        text = f'Вы {participants_list[i][2]} {participants_list[i][3]}.'
    )
    bot.send_message(
        chat_id,
        text = 'Авторизация завершена.',
        reply_markup = markups.after_auth_btns()
    )

@bot.callback_query_handler(func = lambda call: call.data == 'auth_not_confirmed')
def auth_not_confirmed(call):
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    username = call.message.from_user.username
    response_text = 'Авторизация прервана. вы можете повторить попытку авторизации с помощью команды /start или отправить запрос разработчику.'
    bot.edit_message_text(
        chat_id = chat_id,
        message_id = message_id,
        text = response_text
    )
    bot.edit_message_reply_markup(
        chat_id = chat_id,
        message_id = message_id,
        reply_markup = markups.auth_confirmation1()
    )
    utilities.logscreate(chat_id, username, 'auth_not_confirmed')

@bot.callback_query_handler(func = lambda call: call.data == 'go_to_the_main_menu')
def main_menu(call):
    with open('data/db.json', 'r', encoding = 'utf-8') as participants_file:
        participants_list = json.load(participants_file)
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    i = utilities.get_index(chat_id, 0)
    for x in range(len(participants_list[i][9])):
        for xx in range(len(participants_list[i][10])):
            if participants_list[i][9][x] == participants_list[i][10][xx]:
                ii = utilities.get_index(participants_list[i][9][x], 2)
                participants_list[i][6] = 'formed'
                participants_list[ii][6] = 'formed'
                participants_list[i][7] = participants_list[ii][2]
                participants_list[i][8] = participants_list[ii][3]
                participants_list[ii][7] = participants_list[i][2]
                participants_list[ii][8] = participants_list[i][3]
                participants_list[i][9] = []
                participants_list[ii][9] = []
                participants_list[i][10] = []
                participants_list[ii][10] = []
    for x in range(len(participants_list)):
        if participants_list[x][7] == participants_list[i][2]:
            participants_list[i][6] = 'formed'
            participants_list[i][9] = []
            participants_list[i][10] = []
            participants_list[i][7] = participants_list[x][2]
            participants_list[i][8] = participants_list[x][3]
    local_data = f'Ваши фамилия и имя: \n {participants_list[i][2]} {participants_list[i][3]} \n'
    if participants_list[i][-2] == 'y':
        local_data = local_data + 'Вы учавствуете в вальсе. \n'
        if participants_list[i][6] == 'formed':
            ii = utilities.get_index(participants_list[i][7], 2)
            local_data = local_data + 'Пара сформирована. \n Фамилия и имя партнера:\n'
            local_data = local_data + utilities.get_partner_name(chat_id, 0) + '\n Телеграм аккаунт партнера:\n' + participants_list[ii][4]
        elif participants_list[i][6] == 'available':
            local_data = local_data + 'Пара не сформирована \n'
            if len(participants_list[i][9]) == 0:
                local_data = local_data + 'Отправленных запросов на формироание пар нет.\n'
            elif len(participants_list[i][9]) > 0:
                local_data = local_data + f'Количество отправленных запросов на формирование пар: {len(participants_list[i][9])}\n'
                local_data = local_data + 'Фамилии и имена получателей:\n' + utilities.get_partner_name(chat_id, 1)
            if len(participants_list[i][10]) == 0:
                local_data = local_data + 'Входящих запросов на формирование пар нет.\n'
            elif len(participants_list[i][10]) > 0:
                local_data = local_data + f'Количество входящих запросов на формирование пар: {len(participants_list[i][10])}\n'
                local_data = local_data + utilities.get_partner_name(chat_id, 2)
    else:
        local_data = local_data + 'Вы не учавствуете в вальсе.\n'
    with open('data/db.json', 'w', encoding = 'utf-8') as file_export:
        json.dump(participants_list, file_export, ensure_ascii = False, indent = 4)
    bot.send_message(
        chat_id,
        text = local_data,
        reply_markup = markups.main_menu_acts(chat_id)
    )

@bot.callback_query_handler(func = lambda call: call.data == 'participation_status_change')
def participation_status_change(call):
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    with open('data/db.json', 'r', encoding = 'utf-8') as participants_file:
        participants_list = json.load(participants_file)
    i = utilities.get_index(chat_id, 0)
    if participants_list[i][-2] == 'y':
        participants_list[i][-2] = 'n'
        response_text = 'Вы больше не учавствуете в вальсе.'
    elif participants_list[i][-2] == 'n':
        participants_list[i][-2] = 'y'
        response_text = 'Теперь Вы учавствуете в вальсе.'
    with open('data/db.json', 'w', encoding = 'utf-8') as file_export:
        json.dump(participants_list, file_export, ensure_ascii = False, indent = 4)
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markups.go_to_the_main_menu()
    )

@bot.callback_query_handler(func = lambda call: call.data == 'confirmed pair_break')
def pair_break(call):
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    with open('data/db.json', 'r', encoding = 'utf-8') as participants_file:
        participants_list = json.load(participants_file)
    i = utilities.get_index(chat_id, 0)
    ii = utilities.get_index(participants_list[i][7], 2)
    participants_list[i][6] = 'available'
    participants_list[ii][6] = 'available'
    participants_list[i][7] = ''
    participants_list[i][8] = ''
    participants_list[ii][7] = ''
    participants_list[ii][8] = ''
    participants_list[i][9] = []
    participants_list[i][10] = []
    participants_list[ii][9] = []
    participants_list[ii][10] = []
    with open('data/db.json', 'w', encoding = 'utf-8') as file_export:
        json.dump(participants_list, file_export, ensure_ascii = False, indent = 4)
    bot.send_message(
        chat_id,
        text = 'Пара расформирована.',
        reply_markup = markups.go_to_the_main_menu()
    )
@bot.callback_query_handler(func = lambda call: call.data == 'denied pair_break')
def denied_pair_break(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    response_text = 'Расформирование пары отменено.'
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markups.go_to_the_main_menu()
    )
@bot.callback_query_handler(func = lambda call: call.data == 'pair_break')
def pair_break_confirmation(call):
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    response_text = 'Подтвердите расформирование пары.'
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markups.pair_break_confirmation_btns()
    )

@bot.callback_query_handler(func = lambda call: call.data == 'revoke_excisting_sent_req')
def revoke_excisting_sent_req(call):
    with open('data/db.json', 'r', encoding = 'utf-8') as participants_file:
        participants_list = json.load(participants_file)
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    username = call.from_user.username
    i = utilities.get_index(chat_id, 0)
    markup = InlineKeyboardMarkup()
    response_text = 'Отправленных запросов на формирование пар нет.'
    for partner in participants_list[i][9]:
        if len(participants_list[i][9]) > 0:
            full_partner_name = utilities.get_full_name(partner, 2)
            response_text = 'Выберите человека, запрос к которому вы хотите отозвать.'
            markup.row(
                InlineKeyboardButton(
                    text = f'{full_partner_name}',
                    callback_data = f'revoked_pairing_req {partner}'
                    ) 
            )
        else:
            response_text = 'Отправленных запросов на формирование пар нет.'
        
    markup.row(
        InlineKeyboardButton(
            text = '<< Вернуться в главное меню.',
            callback_data = 'go_to_the_main_menu'
            )
    )
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markup
    )
    utilities.logscreate(chat_id, username, 'revoke_excisting_sent_req')

@bot.callback_query_handler(func = lambda call: call.data.startswith('revoked_pairing_req'))
def revoke_excisting_sent_req_surname_imput(call):
    with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
        participants_list = json.load(file_import)
    surnames_list = []
    for x in range(len(participants_list)):
        surnames_list.append(str.lower(participants_list[x][2]))
    chat_id = call.message.chat.id
    username = call.message.from_user.username
    message_id = call.message.message_id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    partner_name = call.data.split()
    partner_name = partner_name[-1]
    i = utilities.get_index(partner_name, 2)
    ii = utilities.get_index(chat_id, 0)
    if participants_list[ii][2] in participants_list[i][10] and participants_list[i][2] in participants_list[ii][9]:
        participants_list[i][10].remove(participants_list[ii][2])
        participants_list[ii][9].remove(participants_list[i][2])
        response_text = 'Запрос удален.'
    else:
        response_text = 'Нету фамилии, удовлетворяющей условиям поиска.'
    with open('data/db.json', 'w', encoding = 'utf-8') as file_export:
        json.dump(participants_list, file_export, ensure_ascii = False, indent = 4)
    utilities.logscreate(chat_id, username, 'revoke_excisting_sent_req_surname_imput')
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markups.go_to_the_main_menu()
    )

@bot.callback_query_handler(func = lambda call: call.data == 'sent_new_req')
def sent_new_req(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    response_text = 'Выберите класс партнера, которому вы хотите отправить запрос на формирование пары.'
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markups.sent_new_req_form_choice()
    )

@bot.callback_query_handler(func = lambda call: call.data.startswith('sent_req_partner_choice'))
def sent_new_req_choice(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    form = call.data.split()
    form = call.data[-3:]
    print(form)
    with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
        participants_list = json.load(file_import)
    markup = InlineKeyboardMarkup()
    i = utilities.get_index(chat_id, 0)
    response_text = 'Нет доступных партнеров для формирования пары.'
    for ii in range(len(participants_list)):
        print(participants_list[ii][-4])
        if participants_list[i][5] != participants_list[ii][5] and participants_list[ii][6] == 'available' and participants_list[ii][-4] == form and participants_list[ii][-2] == 'y' and participants_list[i][2] not in participants_list[ii][10]:
            partner = participants_list[ii][2]
            markup.row(
                InlineKeyboardButton(
                    text = f'{participants_list[ii][2]} {participants_list[ii][3]}',
                    callback_data = f'confirmed_sending {partner}'
                    )
            )
            response_text = 'Выберите партнера, которому отправите заявку.'
    
    markup.row(
        InlineKeyboardButton(
            text = '<< Вернуться в главное меню',
            callback_data = 'go_to_the_main_menu'
            )
    )
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markup
    )

@bot.callback_query_handler(func = lambda call: call.data.startswith('confirmed_sending '))
def confirmed_sending(call):
    with open('data/db.json', 'r', encoding = 'utf-8') as participants_file:
        participants_list = json.load(participants_file)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    partner = call.data.split(sep = ' ')
    partner = partner[-1]
    ii = utilities.get_index(partner, 2)
    i = utilities.get_index(chat_id, 0)
    participants_list[ii][10].append(participants_list[i][2])
    participants_list[i][9].append(participants_list[ii][2])
    with open('data/db.json', 'w', encoding = 'utf-8') as file_export:
        json.dump(participants_list, file_export, ensure_ascii = False, indent = 4)
    bot.send_message(
        chat_id,
        text = f'запрос на формирование пары с {participants_list[ii][2]} {participants_list[ii][3]}',
        reply_markup = markups.go_to_the_main_menu()
    )

@bot.callback_query_handler(func = lambda call: call.data == 'accept_pairing_req')
def accept_pairing_req(call):
    with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
        participants_list = json.load(file_import)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    i = utilities.get_index(chat_id, 0)
    markup = InlineKeyboardMarkup()
    response_text = 'Входящих запросов на формирование пар нет.'
    for partner in participants_list[i][10]:
        if len(participants_list[i][10]) > 0:
            full_partner_name = utilities.get_full_name(partner, 2)
            response_text = 'Выберите партнера, запрос которого вы примете.'
            markup.row(
                InlineKeyboardButton(
                    text = f'{full_partner_name}',
                    callback_data = f'accepted_pairing_req {partner}'
                    ) 
            )
        else:
            response_text = 'Входящих запросов на формирование пар нет.'
    markup.row(
        InlineKeyboardButton(
            text = '<< Вернуться в главное меню.',
            callback_data = 'go_to_the_main_menu'
            )
    )
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markup
    )

@bot.callback_query_handler(func = lambda call: call.data == 'deny_pairing_req')
def deny_pairing_req(call):
    with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
        participants_list = json.load(file_import)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    i = utilities.get_index(chat_id, 0)
    markup = InlineKeyboardMarkup()
    response_text = 'Входящих запросов на формирование пар нет.'
    for partner in participants_list[i][10]:
        if len(participants_list[i][10]) > 0:
            full_partner_name = utilities.get_full_name(partner, 2)
            response_text = 'Выберите партнера, запрос которого вы отклоните.'
            markup.row(
                InlineKeyboardButton(
                    text = f'{full_partner_name}',
                    callback_data = f'denied_pairing_req {partner}'
                    ) 
            )
        else:
            response_text = 'Входящих запросов на формирование пар нет.'
    markup.row(
        InlineKeyboardButton(
            text = '<< Вернуться в главное меню.',
            callback_data = 'go_to_the_main_menu'
            )
    )
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markup
    )

@bot.callback_query_handler(func = lambda call: call.data.startswith('denied_pairing_req'))
def revoke_excisting_sent_req(call):
    with open('data/db.json', 'r', encoding = 'utf-8') as participants_file:
        participants_list = json.load(participants_file)
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    username = call.from_user.username
    partner = call.data.split()
    i = utilities.get_index(chat_id, 0)
    for partner in participants_list[i][9]:
        if len(participants_list[i][9]) > 0:
            full_partner_name = utilities.get_full_name(partner, 2)
            response_text = 'Выберите человека, запрос которого вы хотите отклонить.'
            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton(
                    text = f'{full_partner_name}',
                    callback_data = f'revoked_pairing_req {partner}'
                    ) 
            )
        else:
            response_text = 'Отправленных запросов на формирование пар нет.'
        
    markup.row(
        InlineKeyboardButton(
            text = '<< Вернуться в главное меню.',
            callback_data = 'go_to_the_main_menu'
            )
    )
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markup
    )
    utilities.logscreate(chat_id, username, '')

@bot.callback_query_handler(func = lambda call: call.data.startswith('accepted_pairing_req'))
def accepted_pairing_req(call):
    with open('data/db.json', 'r', encoding = 'utf-8') as participants_file:
        participants_list = json.load(participants_file)
    partner = call.data.split()
    partner = partner[-1]
    chat_id = call.message.chat.id
    username = call.from_user.username
    message_id = call.message.message_id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    i = utilities.get_index(chat_id, 0)
    ii = utilities.get_index(partner, 2)
    utilities.logscreate(chat_id, username, f'accepted_pairing_req partner: {partner}')
    participants_list[i][6] = 'formed'
    participants_list[i][9] = []
    participants_list[i][10] = []
    participants_list[i][7] = participants_list[ii][2]
    participants_list[i][8] = participants_list[ii][3]
    participants_list[ii][6] = 'formed'
    participants_list[ii][9] = []
    participants_list[ii][10] = []
    participants_list[ii][7] = participants_list[i][2]
    participants_list[ii][8] = participants_list[i][3]
    with open('data/db.json', 'w', encoding = 'utf-8') as file_export:
        json.dump(participants_list, file_export, ensure_ascii = False, indent = 4)
    bot.send_message(
        chat_id = participants_list[i][0],
        text = f'Пара c {participants_list[ii][2]} {participants_list[ii][3]} сформирована.',
        reply_markup = markups.go_to_the_main_menu()
    )
    bot.send_message(
        chat_id = participants_list[ii][0],
        text = f'Пара c {participants_list[i][2]} {participants_list[i][3]} сформирована.',
    )

@bot.callback_query_handler(func = lambda call: call.data == 'user_manual')
def user_manual(call):
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    response_text = 'По кнопке "Руководство" вы будете перенаправлены на страницу onedrive с полным описанием способов формирования и расформирования пар. \n По кнопке "Исходный код" вы будете перенаправлены на страницу с исходным кодом бота.'
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markups.redirection_to_user_manual()
    )

@bot.callback_query_handler(func = lambda call: call.data == 'adm_add_member')
def adm_add_member(call):
    message_id = call.message.message_id
    chat_id = call.message.chat.id
    response_text = 'Выберите пол нового пользователя.'
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markups.adm_add_member_gender_markup()
    )

@bot.callback_query_handler(func = lambda call: call.data.startswith('adm_add_member_g_'))
def adm_add_member_gender(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    new_member = []
    if call.data == 'adm_add_member_g_m':
        new_member.append('male')
        response_text = 'Задан мужской пол для пользователя.'
    elif call.data == 'adm_add_member_g_f':
        new_member.append('female')
        response_text = 'Задан женский пол для пользователя.'
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markups.adm_add_member_rights_markup(new_member)
    )
@bot.callback_query_handler(func = lambda call: call.data.startswith('adm_add_member_rights_'))
def adm_add_member_rights(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    new_member = call.data.split(sep = '/')
    if call.data.startswith('adm_add_member_rights_0'):
        new_member.append(0)
        rights_str = 'Заданы стандартные права пользователя.'
    elif call.data.startswith('adm_add_member_rights_1'):
        new_member.append(1)
        rights_str = 'Заданы расширенные права пользователя.'
    elif call.data.startswith('adm_add_member_rights_2'):
        new_member.append(2)
        rights_str = 'Заданы права администратора.'
    response_text = rights_str + '\n Введите фамилию пользователя.'
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    new_mem_surname_imput = bot.send_message(
        chat_id,
        text = response_text
    )
    bot.register_next_step_handler(new_mem_surname_imput, new_member_surname_imput, new_member)

def new_member_surname_imput(message, new_member):
    chat_id = message.chat.id
    surname = str.lower(message.text)
    surname = surname.split(sep = ' ')
    surname = surname[0]
    surname = surname.capitalize()
    new_member.insert(2, surname)
    response_text = f'Фамилия пользователя {surname} задана. \n Введите имя пользователя.'
    new_memb_name_imput = bot.send_message(
        chat_id,
        text = response_text
    )
    bot.register_next_step_handler(new_memb_name_imput, new_member_name_imput, new_member)

def new_member_name_imput(message, new_member):
    with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
        participants_list = json.load(file_import)
    chat_id = message.chat.id
    name = str.lower(message.text)
    name = name.split(sep = ' ')
    name = name[0]
    name = name.capitalize()
    response_text = f'Имя пользователя {name} задано. \n'
    if new_member[0] == 'male':
        response_text = response_text + 'Пол нового пользователя: мужской \n'
    elif new_member[0] == 'female':
        response_text = response_text + 'Пол нового пользователя: женский \n'
    if new_member[1] == 0:
        response_text = response_text + 'Заданы стандартные права для нового пользователя. \n'
    elif new_member[1] == 1:
        response_text = response_text + 'Заданы расширенные права для нового пользователя. \n'
    elif new_member[1] == 3:
        response_text = response_text + 'Для нового пользователя заданы расширенные права. \n'
    response_text = 'Фамилия и имя нового пользователя:' + new_member[2] + new_member[3]
    with open('data/db.json', 'w', encoding = 'utf-8') as file_export:
        json.dump(participants_list, file_export, ensure_ascii = False, indent = 4)
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markups.new_member_confirmation_btns()
    )

@bot.callback_query_handler(func = lambda call: call.data == 'accepted adm_add_new_member')
def accepted_add_new_member(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    response_text = 'Изменения сохранены.'
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markups.go_to_the_main_menu()
    )


@bot.callback_query_handler(func = lambda call: call.data == 'denied adm_add_new_member')
def denied_add_new_member(call):
    with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
        participants_list = json.load(file_import)
    del participants_list[-1]
    with open('data/db.json', 'w', encoding = 'utf-8') as file_export:
        json.dump(participants_list, file_export, ensure_ascii = True, indent = 4)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    response_text = 'Изменения отклонены.'
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    bot.send_message(
        chat_id,
        message_id,
        text = response_text,
        reply_markup = markups.go_to_the_main_menu()
    )

@bot.message_handler(commands = ['issue']) 
def issue(message):
    response_text = 'Введите сообщение для отправки администрации.'
    msg = bot.send_message(
        message.chat.id,
        text = response_text
    )
    bot.register_next_step_handler(msg, sending_message_to_admin)

def sending_message_to_admin(message):
    chat_id = message.chat.id
    username = message.from_user.username
    msg = message.text
    bot.send_message(
        1100060491,
        text = msg
    )
    bot.send_message(
        chat_id,
        text = 'Ваше обращение отправлено.'
    )
    utilities.logscreate(chat_id, username, 'issue')

@bot.message_handler(commands = ['bugreport'])
def bugreport(message):
    response_text = 'Опишите ошибку, которую вы встретили, а также условия её появления.'
    awaiting_b_r = bot.send_message(
        message.chat.id,
        text = response_text
    )
    bot.register_next_step_handler(awaiting_b_r, newbugreport)

def newbugreport(message):
    try:
        with open('data/bugreports.json', 'r', encoding='utf-8') as f:
            bugreports_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        bugreports_list = []
    chat_id = message.chat.id
    username = message.from_user.username
    full_name = utilities.get_full_name(chat_id, 0)
    bugreport_datetime = datetime.datetime.now()
    bugreport_datetime = bugreport_datetime.strftime("%Y-%m-%d %H:%M:%S:%f")
    new_bugreport = [username, full_name, message.text, bugreport_datetime, chat_id]
    bugreports_list.append(new_bugreport)
    with open('data/bugreports.json', 'w', encoding='utf-8') as f:
        json.dump(bugreports_list, f, ensure_ascii=False, indent=4)
    response_text = 'Отчет об ошибке записан.'
    bot.send_message(
        message.chat.id,
        text = response_text, 
    )
    utilities.logscreate(chat_id, username, 'bugreport')
    new_bugreport.clear()


@bot.callback_query_handler(func = lambda call: call.data == 'ext_dbimport')
def dbimport(call):
    chat_id = call.message.chat.id
    username = call.message.from_user.id
    message_id = call.message.message_id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
        participants_list = json.load(file_import)
    x = utilities.get_index(chat_id, 0)
    if participants_list[x][-1] > 0: 
        participants_string = ''
        for i in range(len(participants_list)):
            for ii in range(len(participants_list[i])):
                if ii == 2 or ii == 7:
                    if participants_list[i][6] == 'formed' and participants_list[i][5] == 'male':
                        if ii == 2:
                            participants_string = participants_string + 'Фамилия и имя участника: ' + str(participants_list[i][ii]) + ' ' + str(participants_list[i][ii + 1]) + '\n '
                        if ii == 7:
                            participants_string = participants_string + 'Фамилия и имя партнера: ' + str(participants_list[i][ii]) + ' ' + str(participants_list[i][ii + 1]) + '\n \n '
        response_text = participants_string
        bot.send_message(
            chat_id,
            text = response_text,
            reply_markup = markups.go_to_the_main_menu()
        )
        utilities.logscreate(chat_id, username, 'dbimport')
    else:
        response_text = 'У вас недостаточно прав для выполнения этой команды.'
        bot.send_message(
            chat_id,
            text = response_text,
            reply_markup = markups.go_to_the_main_menu()
        )

@bot.message_handler(commands = ['dev'])
def devcmdchoice(message):
    if message.chat.id in cfg.adm_chat_id:
        bot.send_message(
            message.chat.id,
            text = 'Выберите действие.',
            reply_markup = markups.dev_markups()
        )
    else:
        bot.send_message(
            message.chat.id,
            text = 'у вас нет прав использовать эту команду'
        )

@bot.callback_query_handler(func = lambda call: call.data.startswith('dev'))
def devredirection(call):
    with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
        participants_list = json.load(file_import)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    if call.data == 'devdbimport':
        participants_string = ''
        first_part = len(participants_list)//3
        second_part = 2 * len(participants_list)//3
        for i in range(first_part):
            for ii in range(len(participants_list[i])):
                participants_string = participants_string + ' ' + str(participants_list[i][ii])
                if ii == len(participants_list[i]) - 1:
                    participants_string = participants_string + '\n \n'
        response_text = participants_string
        bot.send_message(
            call.message.chat.id,
            text = response_text
        )
        response_text = ''
        participants_string = ''
        for i in range(first_part, second_part):
            for ii in range(len(participants_list[i])):
                participants_string = participants_string + ' ' + str(participants_list[i][ii])
                if ii == len(participants_list[i]) - 1:
                    participants_string = participants_string + '\n \n'
        response_text = participants_string
        bot.send_message(
            chat_id,
            text = response_text,
        )
        response_text = ''
        participants_string = ''
        for i in range(second_part, len(participants_list)):
            for ii in range(len(participants_list[i])):
                participants_string = participants_string + ' ' + str(participants_list[i][ii])
                if ii == len(participants_list[i]) - 1:
                    participants_string = participants_string + '\n \n'
        response_text = participants_string
        bot.send_message(
            call.message.chat.id,
            text = response_text
        )
        bot.send_message(
            call.message.chat.id,
            text = 'chat id [0]\n user agreement status [1]\n irl first name [2]\n irl second name[3]\n tg username[4]\n gender[5]\n pair status[6]\n partner surname[7]\n partner name[8]\n sent request to(surname)[9]\n recieved request from(surname)[10]\n auth status[-3]\n participation[-2]\n rights[-1]',
            reply_markup = markups.go_to_the_main_menu()
        )
    elif call.data == 'devbugreportimport':
        with open('data/bugreports.json', 'r', encoding='utf-8') as bugreports_import:
            bugreports_list = json.load(bugreports_import)
        bugreport_import_string = 'description of the manualy written bugreport`s structure: \n -username \n -bugreport text \n -date and time of writing bugreport \n -chat id \n \n' 
        for i in range(len(bugreports_list)):
            for ii in range(len(bugreports_list[i])):
                bugreport_import_string = bugreport_import_string + '\n' + str(bugreports_list[i][ii])
                if ii == len(bugreports_list[i]) - 1:
                    bugreport_import_string = bugreport_import_string + '\n \n'
        response_text = bugreport_import_string
        bot.send_message(
            call.message.chat.id,
            text = response_text
        )
        with open('data/autobugreports.json', 'r', encoding='utf-8') as auto_bugreports_import:
            auto_bugreports_list = json.load(auto_bugreports_import)
        auto_bugreport_import_string = 'for description of the auto written bugreports: \n -auto_bugreport_index,\n -auto_bugreport_datetime,\n -call.message.chat.id,\n -local_username,\n -error type' 
        for i in range(len(auto_bugreports_list)):
            for ii in range(len(auto_bugreports_list[i])):
                auto_bugreport_import_string = auto_bugreport_import_string + '\n' + str(auto_bugreports_list[i][ii])
                if ii == len(auto_bugreports_list[i]) - 1:
                    auto_bugreport_import_string = auto_bugreport_import_string + '\n \n'
        response_text = auto_bugreport_import_string
        bot.send_message(
            call.message.chat.id,
            text = response_text,
            reply_markup = markups.go_to_the_main_menu()
        )
    elif call.data == 'devkys':
        response_text = 'Завершение работы бота.'
        bot.send_message(
            call.message.chat.id,
            text = response_text
        )
        os.kill(os.getpid(), signal.SIGINT)
    elif call.data == 'devlogsimport':
        try:
            with open('data.logs.json', 'r', encoding='utf-8') as logs_import:
                logs_list = json.load(logs_import)
        except (FileNotFoundError, json.JSONDecodeError):
            logs_list = []
            logs_string = ''
        logs_string = 'logs structure describtion: \n username[0] \n name of used function[1] \n date and time[2] \n chat id [3]' 
        for i in range(len(logs_list)):
            logs_string = logs_list[i] + ' \n \n '
        bot.send_message(
            1100060491,
            text = logs_string,
            reply_markup = markups.go_to_the_main_menu()
        )
    elif call.data == 'devdata_wipe':
        chat_id = call.message.chat.id
        username = call.from_user.username
        process = subprocess.Popen(['python', 'wipe_data.py'])
        bot.send_message(
            chat_id = call.message.chat.id,
            text = 'Данные удалены.'
        )
        utilities.logscreate(chat_id, username, 'devdeta_wipe / data was wiped')
    elif call.data == 'devdataedit':
        chat_id = call.message.chat.id
        response_text = 'select the participant whose details u wna change'
        markup = InlineKeyboardMarkup()
        for i in range(len(participants_list)):
            markup.row(
                InlineKeyboardButton(
                    text = f'{participants_list[i][2]} {participants_list[i][3]}',
                    callback_data = f'dataeditselect {participants_list[i][2]}'
                    )
            )
        bot.send_message(
            chat_id,
            text = response_text,
            reply_markup = markup
        )

@bot.callback_query_handler(func = lambda call: call.data.startswith('dataeditselect '))
def devdataedit(call):
    chat_id = call.message.chat.id
    editing_participant = call.data.split()
    editing_participant = editing_participant[-1]
    i = utilities.get_index(editing_participant, 2)
    response_text = 'select editing field of '
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markups.devdataedit(i)
    )

@bot.callback_query_handler(func = lambda call: call.data.startswith('dataeditselected '))
def dataeditselected(call):
    with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
        participants_list = json.load(file_import)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    i = call.data.split()
    ii = int(i[-1])
    i = int(i[-2])
    response_text = f'old value: {participants_list[i][ii]} \n imput new value.'
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    message = bot.send_message(
        chat_id,
        text = response_text
    )
    bot.register_next_step_handler(message, editing_data, i, ii)

def editing_data(message, i, ii):
    chat_id = message.chat.id
    new_value = message.text
    old_value = participants_list[i][ii]
    bot.send_message(
        chat_id,
        text = f'old value: {old_value} \n new value: {new_value}',
        reply_markup = markups.editing_data_confirmation(new_value, i, ii)
    )

@bot.callback_query_handler(func = lambda call: call.data.startswith('editing_data_confirmed'))
def editing_data_confirmed(call):
    with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
        participants_list = json.load(file_import)
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    new_value = call.data.split()
    i = int(new_value[-3])
    ii = int(new_value[-2])
    new_value = new_value[-1]
    participants_list[i][ii] = new_value
    with open('data/db.json', 'w', encoding = 'utf-8') as file_export:
        json.dump(participants_list, file_export, ensure_ascii = False, indent = 4)
    response_text = f'changed field: {i} {ii} \n new value: {participants_list[i][ii]}'
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markups.go_to_the_main_menu()
    )

@bot.callback_query_handler(func = lambda call: call.data == 'editing_data_denied')
def editing_data_denied(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    response_text = 'changes denied.'
    bot.edit_message_reply_markup(
        chat_id,
        message_id,
        reply_markup = None
    )
    bot.send_message(
        chat_id,
        text = response_text,
        reply_markup = markups.go_to_the_main_menu()
    )

if __name__ == '__main__':
    bot.infinity_polling()