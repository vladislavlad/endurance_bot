import telebot, uuid, datetime, re, sympy, random
import subprocess, os
import urllib.request, json, yaml
from subprocess import Popen, PIPE

with open("config.yaml", "r") as yml_c:
    config = yaml.load(yml_c)

with open('secret.yaml', 'r') as yml_s:
    secret = yaml.load(yml_s)

bot = telebot.TeleBot(secret['api_token'])

stack = {}

photo_location = 'p.jpeg'
htop_html = 'htop.html'
htop_png = 'htop.png'
pipe_path = 'pipe'

answers = [
    'Да', 'Нет', 'Каво', 'Что?',
    'Не понял', 'ща подумаю', 'кек',
    'конечно', 'неа', 'да', 'ага', 'хм'
]

ha_replies = [
    'ха', 'и мне смешно', 'мне тоже понравилось',
    'я рад', 'спасибо', 'приколюха', 'Xa xa = new Xa()'
]

board = telebot.types.ReplyKeyboardMarkup()
board.row('UUID 🔤', 'Time ⏰', 'Photo 📷')
board.row('Random 🔢', 'Cube 🎲', 'Ping 🏓')
board.row('Meme 😀')


def push_msg(chat_id, msg):
    stack.update({chat_id: msg})
    bot.send_message(chat_id, "Ok")


def pop_msg(chat_id):
    msg = stack.pop(chat_id, None)

    if msg is None:
        bot.send_message(chat_id, "Nothing to pop")
    else:
        bot.send_message(chat_id, msg)


def send_photo(chat_id):
    if chat_id == secret['master_user_id']:
        bot.send_message(chat_id, "Yes, my master.")
        subprocess.run(["streamer", "-o", photo_location])
        bot.send_photo(chat_id, photo=open(photo_location, 'rb'))
    else:
        bot.send_message(chat_id, "These aren't the Photos you're looking for...")


def send_meme(chat_id):
    with urllib.request.urlopen(config['meme_api_url']) as url:
        data = json.loads(url.read().decode())
        length = len(data)

        if length < 1:
            bot.send_message(chat_id, "Сегодня нет мемов 😔")

        else:
            i = random.randint(0, length - 1)
            photoUrl = data[i].get("url")
            bot.send_photo(chat_id, photoUrl)



@bot.message_handler(commands=['kavo'])
def kavo(message):
    bot.reply_to(message, '/kavo')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, f'Hello, I\'m bot Endurance', reply_markup=board)


@bot.message_handler(commands=['htop'])
def send_htop(message):
    try:
        file = open(htop_html, 'w+')
        pipe = open(pipe_path, 'w+')

        Popen(['echo', 'q'], stdout=pipe, shell=True)
        Popen(['htop'], stdin=pipe, stdout=pipe, shell=True).wait()

        pipe.close()
        p3 = Popen(['aha', '--black', '--line-fix', '-f', pipe_path], stdout=file)

        p3.wait()
        file.close()

        # p1 = subprocess.call('(sleep 0.5; echo q)', stdout=pipe, shell=True)
        # p2 = subprocess.check_output(['htop'], stdin=pipe, shell=True)
        # p2.wait()

        # pipe.close()
        # p3 = Popen(['aha', '--black', '--line-fix'], stdout=file)
        # p3.wait()

        bot.send_message(message.chat.id, 'zzz')

        Popen(['wkhtmltoimage', '--width', '600', htop_html, htop_png]).wait()
        bot.send_photo(message.chat.id, open(htop_png, 'rb'))

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "htop сейчас недоступен")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    text = message.text.lower()
    chat_id = message.chat.id

    if "hello" in text or "привет" in text:
        bot.send_message(chat_id, f"Привет, {message.from_user.first_name}")

    elif "bye" in text or "пока" in text:
        bot.send_message(chat_id, f"Пока!")

    elif "uuid 🔤" in text:
        bot.send_message(chat_id, uuid.uuid4())

    elif "random 🔢" in text:
        bot.send_message(chat_id, random.randint(0, 100))

    elif "cube 🎲" in text:
        bot.send_message(chat_id, random.randint(1, 6))

    elif "ping 🏓" in text:
        bot.send_message(chat_id, "pong")

    elif "time ⏰" in text:
        bot.send_message(chat_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

    elif ("photo" in text) or ("фото" in text):
        send_photo(chat_id)

    elif re.match(r"(.*\s+)?(мем|meme)(.*\s+)?", text):
        send_meme(chat_id)

    elif re.match(r'а?(х{1,4}а{1,4})+|.*😀.*|.*😂.*', text):
        a = ha_replies[random.randint(0, len(ha_replies) - 1)]
        bot.send_message(chat_id, a)

    elif "дела" in text:
        bot.send_message(chat_id, "Учу python")

    elif text.startswith("push "):
        push_msg(chat_id, re.sub("^push ", "", message.text, flags=re.I))

    elif "pop" == text.strip():
        pop_msg(chat_id)

    elif "что дальше" in text:
        bot.send_message(chat_id, "Дальше - больше")

    elif "да" in text:
        bot.send_message(chat_id, "И что дальше?")

    elif "?" in text:
        a = answers[random.randint(0, len(answers) - 1)]
        bot.send_message(chat_id, a)

    elif re.match(r".*(\+|\*|\-|\\).*", text):  # and (re.search(r"[A-Za-z]+", text) == None):
        try:
            res = sympy.sympify(text)
            bot.send_message(chat_id, res)
        except:
            bot.send_message(chat_id, "Неверное выражение")

    else:
        bot.send_message(chat_id, "Хм...")


bot.polling()
