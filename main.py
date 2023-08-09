import telebot,sqlite3
from telebot import types
from matplotlib.colors import is_color_like
import random,os,qrcode,sys

class QR:  #Create class for get Qr code in binary
    def getrand(self):
        return f'i{random.randint(1000000,10000000)}.png' 
    def get(self,text,data):
        f = self.getrand()
        qr = qrcode.QRCode(
        version=data[3],
        error_correction=qrcode.constants.ERROR_CORRECT_L,
         box_size=10,
        border=data[4],
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color=data[1], back_color=data[2])
        img.save(f)
        with open(f,'rb') as b:
            os.remove(f)
            return b.read()

token = "<BOT - TOKEN>" # Place Your Bot Token Here
bot = telebot.TeleBot(token) #create object for Telebot 
img = QR() # Create object for class Qr 
default = ("black","white",1,4)  # This is the default tuple which contain (color,background color, version,border) respectively.

class Database: #create class Database to manage gettind data from database , inserting data to database and reset data
    def __init__(self):
        with sqlite3.connect("database.db") as db: # open database.db
            db.execute("""
                CREATE TABLE IF NOT EXISTS USERS( 
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                USERID INTEGER,
                COLOR TEXT,
                BACKGROUND TEXT,
                VERSION INTEGER,
                BORDER  INTEGER
            )""") # Create table if not table exists in database.db 
            db.commit()
    def get_data(self,id): #Method to get data from database
        with sqlite3.connect("database.db") as db:
            usernames = db.execute("SELECT USERID FROM USERS").fetchall()
            for i in usernames:
                if id == i[0]:
                    data =  db.execute("SELECT * FROM USERS WHERE USERID = ?",(id,)).fetchone()
                    return(id,data[2],data[3],data[4],data[5])
            db.execute(f"INSERT INTO USERS (USERID,COLOR,BACKGROUND,VERSION,BORDER) VALUES ({id},?,?,?,?)",default)
            db.commit()
            return (id,default[0],default[1],default[2],default[3])
    def update(self,id,column,changes): # Method to update data to database
        with sqlite3.connect("database.db") as db:
            db.execute(f"UPDATE USERS SET {column} = ? WHERE USERID = ?",(changes,id))
            db.commit()
    def reset(self,id): #metjod to reset data to database
        with sqlite3.connect("database.db") as db:
            db.execute(f"UPDATE USERS SET COLOR = ? , BACKGROUND = ? , VERSION = ? , BORDER = ? WHERE USERID = {id}",default)
            db.commit()

database = Database() #create 

"""
Code for Creating Keyboard (Home Keyboard):
=========================================
Keyboard will appear in th bot like :
---------------------------------------

            👤 DashBoard

🎨 Color    🧩 Background   🆚 Version

🖼 Border   🏭 Reset    🐞 Report Bug"

---------------------------------------
                ||
              --||--
               \  /
                \/
"""

button =  types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=False)
button.add("👤 DashBoard")
button.add("🎨 Color","🧩 Background","🆚 Version")
button.add("🖼 Border","🏭 Reset","🐞 Report Bug")

"""
Code for Creating Keyboard (Cancel Operation) :
==============================================
Keyboard will appear in th bot like :
---------------------------------------
            ❌ Cancel
---------------------------------------
                ||
              --||--
               \  /
                \/
"""
cancel = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=False)
cancel.add("❌ Cancel")

"""
Code for Creating Keyboard (Yes or No Operation) :
==============================================
Keyboard will appear in th bot like :
---------------------------------------
        Yes             No
---------------------------------------
                ||
              --||--
               \  /
                \/
"""

yon = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=False)
yon.add("yes","No")

"""
Code for Dashboard :
==============================================
---------------------------------------
 👤 DashBoard

Name     : 'userfirstname userlastname'
UserName : 'Username'
UserId   : 'userid'

📷 QRcode 
🎨 Color      : 'color of requested user'
🧩 Background : 'background color of requested user'
🆚 Version    : 'version of requested user'
🖼 Border     : 'Border of Requested user'

---------------------------------------
                ||
              --||--
               \  /
                \/
"""


def dashboard(m):
    global button
    data = database.get_data(m.chat.id)
    mess = f'''
<b>👤 DashBoard</b>
<code>
Name     : {m.chat.first_name} {m.chat.last_name}
UserName : {m.chat.username}
UserId   : {m.chat.id}
</code>

<b>📷 QRcode </b>
<code>
🎨 Color      : {data[1]}
🧩 Background : {data[2]}
🆚 Version    : {data[3]}
🖼 Border     : {data[4]}
</code>
    '''
    bot.send_message(m.chat.id,mess,parse_mode="html",reply_markup=button)

"--------------------- starting to code with handlers ---------------------"

"""
This Handler will work when user send '/start' command to the Bot.
You can also add any command and work with then using following Syntax.
"""
@bot.message_handler(commands=['start'])
def start(m):
    database.get_data(m.chat.id)
    bot.send_message(m.chat.id,"welcome! dear {m.chat.first_name},\nSend me any text i will send qrcode.",reply_markup=button)

"------------------- Creating response For 👤 DashBoard Button----------------------"

@bot.message_handler(func = lambda message : message.text == "👤 DashBoard")
def dash_board(m):
    dashboard(m)

"------------------- Creating response For 🎨 Color Button------------------------"

@bot.message_handler(func = lambda message : message.text == "🎨 Color")
def change_color(m):
    msg = bot.send_message(m.chat.id,"Please Enter the Color to change the color of qrcode : \nEg:(red,black,white)",reply_markup=cancel)
    bot.register_next_step_handler(msg,change_color_submit)

def change_color_submit(m):
    if is_color_like(m.text.lower()):
        database.get_data(m.chat.id)
        database.update(m.chat.id,"COLOR",m.text.lower())
        bot.send_message(m.chat.id,"Your Color has been changes ✅Successfully. Thank You :).",reply_markup=button)
    elif m.text.lower() == 'cancel' or m.text == "❌ Cancel":
        bot.send_message(m.chat.id,"Color Change ❌Cancelled!.",reply_markup=button)
    else:
        msg = bot.send_message(m.chat.id,"Invalid Color !.\nPlease Enter Valid Color : \nEg:(red,black,white).",reply_markup=cancel)
        bot.register_next_step_handler(msg,change_color_submit)


"------------------- Creating response For 🧩 Background Button-------------------------"

@bot.message_handler(func = lambda message : message.text == "🧩 Background")
def change_color(m):
    msg = bot.send_message(m.chat.id,"Please Enter the Color to change the background of qrcode : \nEg:(red,black,white).",reply_markup=cancel)
    bot.register_next_step_handler(msg,change_background_color_submit)

def change_background_color_submit(m):
    if is_color_like(m.text.lower()):
        database.get_data(m.chat.id)
        database.update(m.chat.id,"BACKGROUND",m.text.lower())
        bot.send_message(m.chat.id,"Your Background Color has been changes ✅Successfully. Thank You :).",reply_markup=button)
    elif m.text.lower() == 'cancel' or m.text == "❌ Cancel":
        bot.send_message(m.chat.id,"Color Change ❌Cancelled!.",reply_markup=button)
    else:
        msg = bot.send_message(m.chat.id,"Invalid Color !.\nPlease Enter Valid Color : \nEg:(red,black,white).",reply_markup=cancel)
        bot.register_next_step_handler(msg,change_background_color_submit)

"------------------- Creating response For 🆚 Version Button-------------------------"

@bot.message_handler(func = lambda message : message.text == "🆚 Version")
def change_version(m):
    msg = bot.send_message(m.chat.id,"Please Enter version from 1 to 40 qrcode : \n(Type Cancel to cancel version change)",reply_markup=cancel)
    bot.register_next_step_handler(msg,change_version_submit)

def change_version_submit(m):
    try:
        v = int(m.text)
        if v <= 40 and v >= 1:
            database.get_data(m.chat.id)
            database.update(m.chat.id,"VERSION",v)
            bot.send_message(m.chat.id,"Your Version has been changes ✅Successfully. Thank You :).",reply_markup=button)
        else :
            raise Exception
    except:
        if m.text.lower() == "cancel" or m.text == "❌ Cancel":
            bot.send_message(m.chat.id,"Version Change ❌Cancelled!.",reply_markup=button)
        else:
            msg = bot.send_message(m.chat.id,"Please Enter Valid Number from 1 to 40 : \n(Type Cancel to cancel version change)",reply_markup=cancel)
            bot.register_next_step_handler(msg,change_version_submit)

"------------------- Creating response For 🖼 Border Button----------------------"

@bot.message_handler(func = lambda message : message.text == "🖼 Border")
def change_border(m):
    msg = bot.send_message(m.chat.id,"Please Enter Border in between 1 to 200 : \n(Type Cancel to cancel border change)",reply_markup=cancel)
    bot.register_next_step_handler(msg,change_border_submit)

def change_border_submit(m):
    try:
        b = int(m.text)
        if b <=200 and b >= 1: 
            database.get_data(m.chat.id)
            database.update(m.chat.id,"BORDER",b)
            bot.send_message(m.chat.id,"Your border has been changes ✅Successfully. Thank You :).",reply_markup=button)
        else:
            raise Exception
    except:
        if m.text.lower() == "cancel" or m.text == "❌ Cancel":
            bot.send_message(m.chat.id,"Border Change ❌Cancelled!.",reply_markup=button)
        else:
            msg = bot.send_message(m.chat.id,"Please Enter Valid Border Number : \n(Type Cancel to cancel version change)",reply_markup=cancel)
            bot.register_next_step_handler(msg,change_border_submit)

"------------------- Creating response For 🏭 Reset Button----------------------"

@bot.message_handler(func = lambda message : message.text == "🏭 Reset")
def reset(m):
    msg = bot.send_message(m.chat.id,"Please Type 'yes' to reset or click yes button below : \n(click 'No to cancel Reset.)",reply_markup=yon)
    bot.register_next_step_handler(msg,reset_submit)

def reset_submit(m):
    if m.text.lower() == "yes":
        database.get_data(m.chat.id)
        database.reset(m.chat.id)
        bot.send_message(m.chat.id,"Reset has been executed ✅Successfully!.",reply_markup=button)
    else :
        bot.send_message(m.chat.id,"Reset has been ❌Cancelled.",reply_markup=button)

"------------------- Creating response For 🐞 Report Bug Button----------------------"

@bot.message_handler(func = lambda message : message.text == "🐞 Report Bug")
def report_bug(m):
    msg = '''
<code>
🥰 Thank You for using our bot.
If you like our bot kindly share to your friends and family and report problems and bugs at @codesperfect.
</code>
Thank You!.    
    '''
    bot.send_message(m.chat.id,msg,parse_mode="html")

@bot.message_handler(content_types=['text'])  #Sending Qr code for Text Messages
def send_qr(m): 
    data = database.get_data(m.chat.id)
    bot.send_photo(m.chat.id,img.get(m.text,data),caption=m.text,reply_markup=button)


bot.polling()  # by calling this method your bot continuosly watch and will check for messages from telegram.org .
