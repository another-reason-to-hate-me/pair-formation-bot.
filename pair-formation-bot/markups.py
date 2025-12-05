from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton 
import utilities
import json
import cfg

def confirmation_btns(func_name):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = '<< Вернуться в главное меню',
            callback_data = 'go_to_the_main_menu'
            ),
        InlineKeyboardButton(
            text = 'Отклонить изменения',
            callback_data = f'denied {func_name}'
            )
    )
    return markup

def new_member_confirmation_btns():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = 'Подтвердить изменения',
            callback_data = 'accepted new_member_confirmation_btns'
            )
    )
    markup.row(
        InlineKeyboardButton(
            text = 'Отклонить изменения',
            callback_data = 'denied new_member_confirmation_btns'
            )
    )
    return markup

def go_to_the_main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = '<< Вернуться в главное меню',
            callback_data = 'go_to_the_main_menu'
            )
    )
    return markup

def after_auth_btns():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = 'Перейти в главное меню',
            callback_data = 'go_to_the_main_menu'
            )
    )
    return markup

def auth_confirmation1():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = 'Отправить запрос разработчику',
            callback_data = 'auth_send_to_dev'
            )
    )
    return markup

def auth_confirmation_btns():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = 'Да',
            callback_data = 'auth_confirmed'
            ),
        InlineKeyboardButton(
            text = 'Нет',
            callback_data = 'auth_not_confirmed'
            )
    )
    return markup

def adm_add_member_gender_markup():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = 'Мужской',
            callback_data = 'adm_add_member_g_m'
            ),
        InlineKeyboardButton(
            text = 'Женский',
            callback_data = 'adm_add_member_g_f'
            )
    )
    return markup

def adm_add_member_rights_markup(new_member):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = 'Стандартные права',
            callback_data = f'adm_add_member_rights_0/{new_member}'
            ),
        InlineKeyboardButton(
            text = 'Расширенные права',
            callback_data = f'adm_add_member_rights_1/{new_member}'
            ),
        InlineKeyboardButton(
            text ='Права администратора',
            callback_data = f'adm_add_member_rights_2/{new_member}'
            )
    )
    return markup

def main_menu_acts(chat_id):
    with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
        participants_list = json.load(file_import)
    i = utilities.get_index(chat_id, 0)
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = 'Руководство (n/a)',
            callback_data = 'user_manual'
            )
    )
    if participants_list[i][6] == 'available' and participants_list[i][-2] == 'y':
        if len(participants_list[i][10]) > 0:
            markup.row(
                InlineKeyboardButton(
                    text = 'Принять запрос на формировние пары',
                    callback_data = 'accept_pairing_req'
                    )
            )
            markup.row(
                InlineKeyboardButton(
                    text = 'Отклонить запрос на формировние пары',
                    callback_data = 'deny_pairing_req'
                    )
            )
        markup.row(
            InlineKeyboardButton(
                text = 'Отправить новый запрос на формирование пары',
                callback_data = 'sent_new_req'
                )
        )
        if len(participants_list[i][9]) > 0:
            markup.row(
                InlineKeyboardButton(
                    text = 'Отозвать запрос на формирование пары',
                    callback_data = 'revoke_excisting_sent_req'
                    )
            )
    elif participants_list[i][6] == 'formed' and participants_list[i][-2] == 'y':
        markup.row(
            InlineKeyboardButton(
                text = 'Разорвать пару',
                callback_data = 'pair_break'
                )
        )
    if participants_list[i][-2] == 'y':
        markup.row(
            InlineKeyboardButton(
                text = 'Отменить участие в вальсе',
                callback_data = 'participation_status_change'
                )
        )
    elif participants_list[i][-2] == 'n':
        markup.row(
            InlineKeyboardButton(
                text = 'Вступить в участие в вальсе',
                callback_data = 'participation_status_change'
                )
        )
    if participants_list[i][-1] > 0:
        markup.row(
            InlineKeyboardButton(
                text = 'Просмотреть список сформированных пар',
                callback_data = 'ext_dbimport'
                )
        )
        if participants_list[i][-1] > 1:
            markup.row(
                InlineKeyboardButton(
                    text = 'Удалить участника (n/a)',
                    callback_data = 'adm_delete_member'
                    ),
                InlineKeyboardButton(
                    text = 'Добавить участника (n/a)',
                    callback_data = 'adm_add_member'
                    )
            )
            if participants_list[i][-1] > 2:
                markup.row(
                    InlineKeyboardButton(
                        text = 'Импорт дб',
                        callback_data = 'devdbimport'
                        ),
                    InlineKeyboardButton(
                        text = 'Импорт баг репортов',
                        callback_data = 'devbugreportimport'
                        )
                )
                markup.row(
                    InlineKeyboardButton(
                        text = 'Отправить сообщение(n/a)',
                        callback_data = 'devsend'
                        ),
                    InlineKeyboardButton(
                        text = 'Импорт логов (n/a)',
                        callback_data = 'devlogsimport'
                        )
                )
                markup.row(
                    InlineKeyboardButton(
                        text = 'Завершить работу бота',
                        callback_data = 'devkys'
                        ),
                    InlineKeyboardButton(
                        text = 'Возврат данных до исходных',
                        callback_data = 'devdata_wipe'
                        )
                )
    markup.row(
        InlineKeyboardButton(
            text = 'Обновить данные',
            callback_data = 'go_to_the_main_menu'
            )
    )
    return markup

def sent_new_req_form_choice():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = '11А',
            callback_data = 'sent_req_partner_choice 11А'
            ),
        InlineKeyboardButton(
            text = '11Б',
            callback_data = 'sent_req_partner_choice 11Б'
            )
    )
    return markup

def pair_break_confirmation_btns():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = 'Подтвердить расформирование',
            callback_data = 'confirmed pair_break'
            )
    )
    markup.row(
        InlineKeyboardButton(
            text = 'Отменить расформирование',
            callback_data = 'denied pair_break'
            )
    )
    return markup

def dev_markups():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = 'db import',
            callback_data = 'devdbimport'
            ),
        InlineKeyboardButton(
            text = 'bugreports import',
            callback_data = 'devbugreportimport'
            )
    )
    markup.row(
        InlineKeyboardButton(
            text = 'import logs(n/a)',
            callback_data = 'devlogsimport'
            ),
        InlineKeyboardButton(
            text = 'import issues(n/a)',
            callback_data = 'devimportissues'
            )
    )
    markup.row(
        InlineKeyboardButton(
            text = 'data wipe',
            callback_data = 'devdata_wipe'
            ),
        InlineKeyboardButton(
            text = 'data edit',
            callback_data = 'devdataedit'
        )
    )
    markup.row(
        InlineKeyboardButton(
            text = 'restart bot',
            callback_data = 'devkys'
            )
    )
    return markup

def redirection_to_user_manual():
    markup = InlineKeyboardMarkup()
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
            text = '<< Вернуться в главное меню',
            callback_data = 'go_to_the_main_menu'
            )
    )
    return markup

def devdataedit(i):
    with open('data/db.json', 'r', encoding = 'utf-8') as file_import:
        participants_list = json.load(file_import)
    markup = InlineKeyboardMarkup()
    print(len(participants_list[i]))
    print(*range(len(participants_list[i])))
    for ii in range(len(participants_list[i])):
        if ii == 0:
            markup.row(
                InlineKeyboardButton(
                text = 'chat_id',
                callback_data = f'dataeditselected {i} {ii}'
                )
            )
        if ii == 1:
            markup.row(
                InlineKeyboardButton(
                text = 'user agreement status',
                callback_data = f'dataeditselected {i} {ii}'
                )
            )
        if ii == 2:
            markup.row(
                InlineKeyboardButton(
                text = 'surname',
                callback_data = f'dataeditselected {i} {ii}'
                )
            )
        if ii == 3:
            markup.row(
                InlineKeyboardButton(
                text = 'name',
                callback_data = f'dataeditselected {i} {ii}'
                )
            )
        if ii == 4:
            markup.row(
                InlineKeyboardButton(
                    text = 'username',
                    callback_data = f'dataeditselected {i} {ii}'
                )
            )
        if ii == 5:
            markup.row(
                InlineKeyboardButton(
                text = 'gender',
                callback_data = f'dataeditselected {i} {ii}'
                )
            )
        if ii == 6:
            markup.row(
                InlineKeyboardButton(
                text = 'pair status',
                callback_data = f'dataeditselected {i} {ii}'
                )
            )
        if ii == 7:
            markup.row(
                InlineKeyboardButton(
                    text = 'partner surname',
                    callback_data = f'dataeditselected {i} {ii}'
                )
            )
        if ii == 8:
            markup.row(
                InlineKeyboardButton(
                    text = 'partner name',
                    callback_data = f'dataeditselected {i} {ii}'
                )
            )
        if ii == 9:
            markup.row(
                InlineKeyboardButton(
                text = 'sent request',
                callback_data = f'dataeditselected {i} {ii}'
                )
            )
        if ii == 10:
            markup.row(
                InlineKeyboardButton(
                text = 'recieved request',
                callback_data = f'dataeditselected {i} {ii}'
                )
            )
        if ii == -4:
            markup.row(
                InlineKeyboardButton(
                text = 'form',
                callback_data = f'dataeditselected {i} {ii}'
                )
            )
        if ii == -3:
            markup.row(
                InlineKeyboardButton(
                text = 'auth status',
                callback_data = f'dataeditselected {i} {ii}'
                )
            )
        if ii == -2:
            markup.row(
                InlineKeyboardButton(
                text = 'participation status',
                callback_data = f'dataeditselected {i} {ii}'
                )
            )
        if ii == -1:
            markup.row(
                InlineKeyboardButton(
                text = 'rights',
                callback_data = f'dataeditselected {i} {ii}'
                )
            )
        return markup
    
def editing_data_confirmation(new_value, i, ii):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text = 'confirm changes',
            callback_data = f'editing_data_confirmed {i} {ii} {new_value}'
        ),
        InlineKeyboardButton(
            text = 'deny changes',
            callback_data = 'editing_data_denied'
        )
    )
    return markup