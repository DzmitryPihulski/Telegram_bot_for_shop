#importintg libraries
import telebot
import telebot.types as types
import pyodbc
import datetime

#importing other files
import passwords
import functions_for_db
import keyboards

#TOKEN Of My Telegram Bot
BOT_TOKEN = passwords.BOT_TOKEN
bot = telebot.TeleBot(BOT_TOKEN)


#BOT COMMANDS

#Start the bot(this command add every user to SQL Users table)
@bot.message_handler(commands = ['start'])
def send_welcome(message) -> None:
    try:
        get_user__first_name = message.from_user.first_name
        get_user_last_name = message.from_user.last_name
        get_user_username = message.from_user.username
        user_id = message.from_user.id

        connection = functions_for_db.make_connection_todb('ShopDB')
        cursor = connection.cursor()
        querry = f"""SELECT user_id FROM Users WHERE user_id={user_id};"""

        if cursor.execute(querry).fetchone() is None:  
            cursor.execute(f"INSERT INTO Users VALUES ({user_id}, '{get_user_username}', '{get_user__first_name}', '{get_user_last_name}');")
            bot.send_message(
                message.chat.id ,
                f"🛒 | Hey {get_user__first_name}, how are you doing? It's shop-bot here!\n Say \help and I will tell you about the commands.",
                reply_markup = keyboards.start_keyboard
            )
        else:
            bot.send_message(
                message.chat.id,
                f"⛔️ | You have already registrated. Say \help and I will tell you about the commands.",
                reply_markup = keyboards.start_keyboard
            )
    except pyodbc.Error as ex:
        bot.send_message(
            message.chat.id,
            f'🚫 | Error in command',
            reply_markup = keyboards.start_keyboard
        )
        bot.send_message(
            functions_for_db.admin_chat('dimapiggy'),
            f"Hi! We have a problem in /start command with user\n Details:\n User username @{get_user_username}\n User first and last names {get_user__first_name} {get_user_last_name}\n The error: {ex}",
            reply_markup = keyboards.admin_keyboard
        )

#Say help
@bot.message_handler(commands = ['help'])
def greetings(message) -> None:
    text = """✋Hello, My name is ShopBot. I am the project of @dimapiggy . I was written on python🐍 with the help of MS SQL server. This are my commands:\n \n

    /id - 🪪you can get information about yourself. I am using this information in my Database.\n \n

    /all_awailable_products - 🛍you can get information about all awailable now products i am selling.\n \n
    
    /make_order - 🛒you can make order."""
    bot.send_message(
        message.chat.id,
        text,reply_markup = keyboards.start_keyboard
    )

#Check my data
@bot.message_handler(commands = ['id'])
def id(message) -> None:
    bot.send_message(
        message.chat.id,
        'Your username: '+str(message.from_user.username)+'.\nYour user id: '+str(message.from_user.id)+'.\nYour chat id: '+str(message.chat.id),
        reply_markup = keyboards.start_keyboard
    )

#View awailable products from SQL Products table
@bot.message_handler(commands = ['all_awailable_products'])
def view_all_products(message) -> None:
    all_awail_prod = functions_for_db.all_awailable_products()
    for i in all_awail_prod:
        bot.send_message(
            message.chat.id,
            i[0],
            parse_mode = 'Markdown'
        )

#Command for making orders in shop
@bot.message_handler(commands = ['make_order'])
def make_orderer(message) -> None:
    text = "Choose item for order."
    bot.send_message(
        message.chat.id,
        text,
        reply_markup = gen_markup(functions_for_db.get_names_of_awailable_products())
    )

@bot.callback_query_handler(func = lambda call: True)
def process_callback_1(querry) -> None:
    make_order(querry)

#Get admin status(Everyone could get admin status with password)
@bot.message_handler(commands = ['admin'])
def get_admin(message) -> None:
    if is_admin(message) == False:
        sent_msg = bot.send_message(
            message.chat.id,
            f'Wooo {message.from_user.username}👻. I see you want to get access to admins!\n It is not so easy. Firstly I want you to give password.🛂'
        )
        bot.register_next_step_handler(sent_msg, get_admin_status)
    else:
        bot.send_message(
            message.chat.id,
            f"⛔️ | You have already registrated. Say \help and I will tell you about the commands.",
            reply_markup = keyboards.admin_keyboard
        )

def get_admin_status(message) -> None:
    if message.text == passwords.PASSWORDS:
        connection = functions_for_db.make_connection_todb('ShopDB')
        cursor = connection.cursor() 
        cursor.execute(f"INSERT INTO Admins VALUES ({message.from_user.id}, '{message.from_user.username}', '{message.from_user.first_name}', '{message.from_user.last_name}');")
        bot.send_message(
            message.chat.id,
            f'Congratulations {message.from_user.username}. You are now admin!',
            reply_markup=keyboards.admin_keyboard
        )
    else:
        bot.send_message(
            message.chat.id,
            f'Sorry {message.from_user.username}. It is not an aceptable answer!',
            reply_markup = keyboards.start_keyboard
        )

###ADMIN COMMANDS ONLY

##Functions for first set up
#make database
@bot.message_handler(commands = ['make_db'])
def make_db(message) -> None:
    bot.send_message(
        message.chat.id, 
        functions_for_db.make_db('ShopDB'),
        reply_markup=keyboards.start_keyboard
    )

#make tables
@bot.message_handler(commands = ['make_tables'])
def make_db(message) -> None:
    bot.send_message(
        message.chat.id,
        functions_for_db.make_tables(functions_for_db.make_connection_todb('ShopDB')),
        reply_markup=keyboards.start_keyboard
    )

#View all products from SQL Products table
@bot.message_handler(commands = ['all_products'])
def view_all_products(message) -> None:
    if is_admin(message) == True:
        all_products = functions_for_db.all_products()
        for i in all_products:
            bot.send_message(
                message.chat.id,
                i[0],
                parse_mode='Markdown'
            )

#View all orders from SQL Orders table
@bot.message_handler(commands = ['all_orders'])
def view_all_products(message) -> None:
    if is_admin(message) == True:
        all_orders=functions_for_db.all_orders()
        for i in all_orders:
            bot.send_message(
                message.chat.id,
                i[0],
                parse_mode='Markdown'
            )

#Add new product to SQL Products table
@bot.message_handler(commands = ['add_product'])
def add_product(message) -> None:
    if is_admin(message) == True:
        text="""Give me the product information in format:  (product_name,description,product_price,foto,amount,Awailable)\nFor example:\n  Blue mask,blue mask for swimming,20,https://bishopsport.co.uk/cdn/shop/products/SW3620.jpg,20,1"""

        sent_msg=bot.send_message(
            message.chat.id,
            text
        )
        bot.register_next_step_handler(
            sent_msg,
            functions_for_db.insert_into_table_Products
        )

#Change price of certain product in SQL Products table
@bot.message_handler(commands = ['change_product_price'])
def change_price_of_prt(message) -> None:
    if is_admin(message) == True:
        sent_msg = bot.send_message(
            message.chat.id,
            f'Give me product id and new price in like that: product_id newprice'
        )
        bot.register_next_step_handler(
            sent_msg,
            change_price_of_product
        )

#Change awailable status(awailable or not) of certain product in SQL Products table
@bot.message_handler(commands = ['change_product_awailable'])
def change_awailable_of_prt(message) -> None:
    if is_admin(message) == True:
        sent_msg=bot.send_message(
            message.chat.id,
            f'Give me product id and new status(0=False, 1=True) in like that: product_id newstatus. For example: 3 0'
        )
        bot.register_next_step_handler(
            sent_msg,
            change_awailable_of_product
        )

#delete from SQL Products table
@bot.message_handler(commands = ['delete_product'])
def add_product(message) -> None:
    if is_admin(message) == True:
        text="""Give me the product id """

        sent_msg=bot.send_message(
            message.chat.id,
            text
        )
        bot.register_next_step_handler(
            sent_msg,
            functions_for_db.delete_from_table_Products
        )

#View all users of our bot from SQL Users table
@bot.message_handler(commands = ['all_users'])
def view_all_users(message) -> None:
    if is_admin(message) == True:
        all_users=functions_for_db.all_users()
        bot.send_message(
            message.chat.id,
            all_users,
            parse_mode='Markdown',
            reply_markup=keyboards.admin_keyboard
        )

#If it is not a command, then just return the input(echo bot for any other inputs, not commands)
@bot.message_handler(func = lambda msg: True)
def echo_all(message)all_users:
    bot.reply_to(
        message,
        message.text,
        reply_markup=keyboards.start_keyboard
    )

##FUNCTIONS FOR COMMANDS(That are the function, which are helping in commands operations)

#Check admin status(is user an admin or not)
def is_admin(message) -> bool:
    connection=functions_for_db.make_connection_todb('ShopDB')
    cursor=connection.cursor()
    querry=f"""SELECT user_id FROM Admins WHERE user_id={message.from_user.id};"""

    if cursor.execute(querry).fetchone() is None:
        return False
    else:
        return True

#For changing data in SQL Products table
def change_price_of_product(message) -> None:
    arguments=list(message.text.split(" "))
    connection=functions_for_db.make_connection_todb('ShopDB')
    querry="""UPDATE Products SET product_price = {} WHERE product_id={};""".format(int(arguments[1]), int(arguments[0]))
    try:
        cursor=connection.cursor()
        cursor.execute(querry)
        bot.send_message(
            message.chat.id,
            'Done!',
            parse_mode='Markdown'
        )
    except pyodbc.Error as ex:
        bot.send_message(
            message.chat.id,
            f"The error '{ex}' occurred"
        )

def change_awailable_of_product(message) -> None:
    arguments=list(message.text.split(" "))
    connection=functions_for_db.make_connection_todb('ShopDB')
    querry="""UPDATE Products SET Awailable = {} WHERE product_id={};""".format(int(arguments[1]), int(arguments[0]))
    try:
        cursor=connection.cursor()
        cursor.execute(querry)
        bot.send_message(
            message.chat.id,
            'Done!',
            parse_mode='Markdown'
        )
    except pyodbc.Error as ex:
        bot.send_message(
            message.chat.id,
            f"The error '{ex}' occurred"
        )

#Orders(to help customers make new orders)
def make_order(message) -> None:
    product_name = message.data
    text = "How many of these do you want? Give me the answer in that format: number. For example: 10"
    sent_msg = bot.send_message(
        message.from_user.id, 
        text,
        parse_mode="Markdown"
    )
    #Register the answer and going to the next function
    bot.register_next_step_handler(
        sent_msg,
        make_order_2,
        str(product_name)
    )
    
def make_order_2(amount, product_name) -> None:
    amount_data = amount.text
    text = "Where you want me to ship it"
    sent_msg = bot.send_message(
        amount.from_user.id,
        text,
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(
        sent_msg,
        make_order_3,
        [product_name,int(amount_data)]
    )
def make_order_3(adress, product_name_and_amount) -> None:
    functions_for_db.insert_into_table_Orders(
        [int(adress.from_user.id),
         adress.from_user.username,
         functions_for_db.get_id_of_product(product_name_and_amount[0]),
         int(product_name_and_amount[1]),
         str(adress.text),datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    )
    bot.send_message(
        adress.chat.id,
        f'Your order is placed',
        reply_markup = keyboards.start_keyboard
    )
    bot.send_message(
        functions_for_db.admin_chat('dimapiggy'),
        f"Hi!\n We have new order!\n Details:\n Username @{adress.from_user.username}\n Product name {product_name_and_amount[0]}\n Amount {product_name_and_amount[1]}\n Adress {str(adress.text)}\n Date {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

#InlineButtons(to generate inline buttons below the messages)
def gen_markup(args):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    for i in args:
        markup.add(types.InlineKeyboardButton(str(i), callback_data=i))
    return markup

bot.infinity_polling()
