
import json
import datetime 

def get_index(value, index_in_child_list):
    with open('data/db.json', 'r', encoding = 'utf-8') as get_index_file:
        participants_list = json.load(get_index_file)
    get_index_list = []
    for i in range(len(participants_list)):
        if isinstance(participants_list[i][index_in_child_list], str):
            value = str.lower(value)
            get_index_list.append(str.lower(participants_list[i][index_in_child_list]))
        else:
            get_index_list.append(participants_list[i][index_in_child_list])
    index = get_index_list.index(value)
    get_index_list.clear()
    return index

def logscreate(chat_id, username, function_name):
    try:
        with open('data/logs.json', 'r', encoding = 'utf-8') as logs_import:
            logs_list = json.load(logs_import)
    except (FileNotFoundError, json.JSONDecodeError):
        logs_list = []
    with open('data/db.json', 'r', encoding = 'utf-8' ) as file_import:
        participants_list = json.load(file_import)
    log_datetime = datetime.datetime.now()
    log_datetime = log_datetime.strftime("%Y-%m-%d %H:%M:%S:%f")
    try:
        full_name = get_index(chat_id, 2)
        full_name = f'{participants_list[full_name][2]} {participants_list[full_name][3]}'
        new_log = [username, full_name, function_name, log_datetime, chat_id]
    except:
        new_log = [username, function_name, log_datetime, chat_id]
        logs_list.append(new_log)
    try:
        with open('data/logs.json', 'w', encoding = 'utf-8') as logs_export:
            json.dump(logs_list, logs_export, ensure_ascii = False, indent = 4)
            new_log.clear()
    except:
        print(f'log was not created, {chat_id} {username} {function_name}')

def get_partner_name(chat_id, alg_num):
    with open('data/db.json', 'r', encoding = 'utf-8' ) as file_import:
        participants_list = json.load(file_import)
    partner_name_string = ''
    i = get_index(chat_id, 0)
    if alg_num == 0:
        partner_name_string = f'{participants_list[i][7]} {participants_list[i][8]}'
    if alg_num == 1:
        for l in range(len(participants_list[i][9])):
            last_partner_name = get_full_name(participants_list[i][9][l], 2)
            partner_name_string = partner_name_string + ' ' + ''.join(last_partner_name) + '\n '
    if alg_num == 2:
        for l in range(len(participants_list[i][10])):
            last_partner_name = get_full_name(participants_list[i][10][l], 2)
            partner_name_string = partner_name_string + ' ' + ''.join(last_partner_name) + '\n '
    return partner_name_string
            

def get_full_name(value, index_in_child_list):
    with open('data/db.json', 'r', encoding = 'utf-8' ) as file_import:
        participants_list = json.load(file_import)
    full_name = ''
    i = get_index(value, index_in_child_list)
    full_name = f'{participants_list[i][2]} {participants_list[i][3]}' 
    return full_name

def auto_bugreport(chat_id, username, err):
    try:
        with open('data/autobugreports.json', 'r', encoding = 'utf-8') as auto_bugreports_file:
            auto_bugreports_list = json.load(auto_bugreports_file)
    except (FileNotFoundError, json.JSONDecodeError):
        auto_bugreports_list = []
    try:
        full_name = get_full_name(chat_id, 0)
    except:
        full_name = 'name not defined'
        auto_bugreport_datetime = datetime.datetime.now()
        auto_bugreport_datetime = auto_bugreport_datetime.strftime('%Y-%m-%d %H:%M:%S:%f')
        new_auto_bugreport = [username, full_name, err, auto_bugreport_datetime, chat_id]
        auto_bugreports_list.append(new_auto_bugreport)
        with open('data/autobugreports.json', 'w', encoding = 'utf-8') as auto_bugreports_file:
            json.dump(auto_bugreports_list, auto_bugreports_file, ensure_ascii = False, indent = 4)
            logscreate(chat_id, username, 'autobugreport')
