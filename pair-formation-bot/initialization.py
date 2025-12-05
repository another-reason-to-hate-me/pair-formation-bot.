import datetime
import subprocess
import schedule
import time

botfile = 'main.py'
process = None

def start_bot():
    global process
    if process and process.poll() is None:
        print('Бот уже запущен.')
        return
    print(f'Запуск бота. {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    process = subprocess.Popen(['python', botfile])

def stop_bot():
    global process
    if process and process.poll() is None:
        print('Остановка бота.')
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print('Бот остановлен.')

def scheduled_restart():
    print(f'Автоматический перезапуск по расписанию.{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    stop_bot()
    start_bot()

schedule.every().hour.do(scheduled_restart)

if __name__ == '__main__':
    start_bot() 
    while True:
        schedule.run_pending() 
        if process.poll() is not None:
            print(f'Бот завершился с кодом {process.poll()}. Перезапуск.')
            start_bot()
            
        time.sleep(1)
