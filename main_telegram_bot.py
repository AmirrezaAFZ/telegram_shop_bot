
import telebot
from telebot import TeleBot, types
import logging
from telebot.types import ReplyKeyboardMarkup,InlineKeyboardMarkup,InlineKeyboardButton
from telebot.types import InputMediaPhoto
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import mysql.connector
from DDL import *
from DML import *
from DQL import *
from credentials import *
past_users=[]
user_steps={}
shopping_cart={}



logging.basicConfig(filename='shop.log',filemode='a',level=logging.INFO,format='%(asctime)s - %(message)s - %(levelname)s ')

API_TOKEN=token






commands = {
    'start'       : '  starts the bot',
    'options'     : 'options to navigate through the bot',
    'contact'     : 'ways to contact us',
    'about'       : 'about our shop'
}

admin_commands = {
    'add_product': 'add prodcut to the database'
}


def get_user_steps(cid):
    return user_steps.setdefault(cid,0)
bot=telebot.TeleBot(API_TOKEN,num_threads=10)
hideboard=ReplyKeyboardRemove()


def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)
            logging.info(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)


bot = telebot.TeleBot(API_TOKEN)
bot.set_update_listener(listener)  


@bot.message_handler(commands=['start'])
def send_welcome(message):
    cid= message.chat.id
    if cid not in past_users:
        cid=message.chat.id
        first_name=message.chat.first_name
        last_name=message.chat.last_name
        username=message.chat.username
        insert_user_info(cid=cid, first_name=first_name, last_name=last_name, phone_number=None, username=username, email=None, privilage='user')
    bot.send_message(cid , '***welcome to our shop***\n\n for more information pull up the menu (at the bottom left)')



@bot.message_handler(commands=['add_product'])
def add_product_command(message):
    cid=message.chat.id
    if cid not in admins:
        echo(message)
        return
    cid=message.chat.id
    text= '''please send the product's photo with the following caption (the caption should be in the same order):
        product_name/brand/description/price/inventory/category'''
    bot.send_message(cid,text)
    user_steps[cid]=1000


@bot.message_handler (content_types= ['photo'])
def add_product_2 (message) : 
    cid = message.chat.id
    if cid in admins and user_steps[cid] == 1000: 
        caption = message.caption
        file_id = message.photo[-1].file_id
        name,brand ,description, price, inventory, category= caption.split ('/')
        insert_product_info(name=name,brand=brand ,description=description, image_file_id=file_id, price=float(price), inventory=int(inventory), category=category)
        print ( 'product info inserted')
        user_steps[cid] = 0
    else :
        echo(message)


# help page
@bot.message_handler(commands=['help'])
def command_help(message):
    cid = message.chat.id 
    help_text = "The following commands are available: \n"
    for key in commands:  
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    if cid in admins:
        help_text += "admin commands: \n"
        for key in admin_commands: 
            help_text += "/" + key + ": "
            help_text += admin_commands[key] + "\n"
    bot.send_message(cid, help_text)  



@bot.message_handler(commands=['options'])
def options(message):
    cid=message.chat.id
    markup=ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)
    markup.add('cpu','gpu','basket','/contact','/about')
    bot.send_message(cid,'please choose one of the options',reply_markup=markup)


#__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________        
@bot.message_handler(func=lambda message: message.text == 'basket')
def show_cart(message):
    cid = message.chat.id
    user_cart = shopping_cart.get(cid, [])
    if not user_cart:
        bot.send_message(cid, "your basket is empty, add a product to it")
        return
    
    cart_message = "products that you added to basket :\n"
    total_price = 0
    markup = InlineKeyboardMarkup(row_width = 1) 
    for i, item in enumerate(user_cart):
        cart_message += f"{i + 1}. {item['name']} - {item['price']} $ \n"
        total_price += int(item['price'])
        markup.add(InlineKeyboardButton(f" delete  {item['name']} from cart", callback_data=f'delete_{i}'))
    
    cart_message += f"\n total price: {total_price} $"
    markup.add(InlineKeyboardButton('empty your cart', callback_data='empty_cart') , InlineKeyboardButton('checkout', callback_data='checkout_basket'))
    bot.send_message(cid, cart_message, reply_markup=markup)



@bot.callback_query_handler(func=lambda call: call.data == 'empty_cart')
def empty_cart(call):
    cid = call.message.chat.id
    shopping_cart[cid] = []
    message_id=call.message.message_id
    chat_id = cid
    bot.answer_callback_query(call.id, text="all products were removed from your basket" )
    bot.edit_message_text("add products to your basket and they will show up here", chat_id, message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete'))
def remove_from_cart(call):
    cid = call.message.chat.id
    i = int(call.data.split('_')[1])
    user_cart = shopping_cart.get(cid, [])
    if 0 <= i < len(user_cart):
        removed_item = user_cart.pop(i)
        shopping_cart[cid] = user_cart
        bot.answer_callback_query(call.id, text=f"{removed_item['name']} was removed from  your basket")
        show_cart(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'checkout_basket')
def pay_cart(call):
    cid = call.message.chat.id
    username = call.from_user.username or call.from_user.first_name
    user_cart = shopping_cart.get(cid, [])
    if not user_cart:
        bot.send_message(cid, "your basket is empty, add products to it")
        return
    sale_id = create_sale(cid)
    if sale_id is None:
        bot.send_message(cid, "there was error with the bot, pleae try again")
        return
    for item in user_cart:
        create_or_update_sale_row(sale_id, item['id'], item.get('quantity', 1))
        update_product_inventory(item['id'], item.get('quantity', 1))

    shopping_cart[cid] = []
    
    bot.send_message(cid, f'{username} you will be redirected to the www.google.com')

#__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________



@bot.message_handler(func=lambda message: message.text == 'gpu')
def gpu_brands(message):
    cid = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('amd radeon', callback_data='get_gpu_amdradeon'),types.InlineKeyboardButton('nvidia', callback_data='get_gpu_nvidia'),)
    bot.send_message(cid, 'which brand are you intrested in', reply_markup=markup)

 
def gpu_products_markup(brand, number , total):
    markup = InlineKeyboardMarkup()
    markup.add(    InlineKeyboardButton('<', callback_data=f'previous_gpu_{brand}_{number}'), types.InlineKeyboardButton(f'{number + 1}/{total}', callback_data='cancel'),     InlineKeyboardButton('>', callback_data=f'next_gpu_{brand}_{number}'))
    markup.add(InlineKeyboardButton(' add to the basket  ', callback_data=f'add_gpu_{brand}_{number}'))
    return markup
def show_gpus(call, brand, number, is_new_message=True):
    products = get_products_by_brand(brand)
    if products:
        product = products[number]
        cid = call.message.chat.id
        if is_new_message:
            bot.send_photo(cid, product['image_file_id'], caption=f"{product['name']}\n\n{product['description']}\nprice: {product['price']} $", reply_markup=gpu_products_markup(brand, number, len(products)))
        else:
            bot.edit_message_media(media=types.InputMediaPhoto(product['image_file_id']), chat_id=cid, message_id=call.message.message_id)
            bot.edit_message_caption(caption=f"{product['name']}\n\n{product['description']}\n price: {product['price']}", chat_id=cid, message_id=call.message.message_id, reply_markup=gpu_products_markup(brand, number, len(products)))

@bot.callback_query_handler(func=lambda call: call.data.startswith('get_gpu'))
def show_specific_gpu_brand_products(call):
    print(call.data)
    brand = call.data.split('_')[-1]
    print(brand)
    show_gpus(call, brand, 0)

@bot.callback_query_handler(func=lambda call: call.data.startswith('next_gpu') or call.data.startswith('previous_gpu'))
def gpu_products_navigator(call):
    parts = call.data.split('_')
    brand, number = parts[2], int(parts[3])
    products = get_products_by_brand(brand)
    if call.data.startswith('previous_gpu'):
        number = (number - 1) % len(products)
    elif call.data.startswith('next_gpu'):
        number = (number + 1) % len(products)
    show_gpus(call, brand, number, is_new_message=False)

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_gpu'))
def add_phone_to_cart(call):
    parts = call.data.split('_')
    print(parts)
    brand, number = parts[2], int(parts[3])
    products = get_products_by_brand(brand)
    product = products[number]
    cid = call.message.chat.id
    user_cart = shopping_cart.get(cid, [])
    user_cart.append(product)
    shopping_cart[cid] = user_cart
    conn = mysql.connector.connect(user='root', password='password', host='localhost', database='shop')
    cursor = conn.cursor()
    cursor.execute("update product set inventory = inventory - 1 where id = %s", (product['id'],))
    conn.commit()
    cursor.close()
    conn.close()
    bot.answer_callback_query(call.id, text=f"{product['name']} the product was added to your basket successfully")

#__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@bot.message_handler(func=lambda message: message.text == 'cpu')
def cpu_brands(message):
    cid = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('amd', callback_data='get_cpu_amd'),types.InlineKeyboardButton('intel', callback_data='get_cpu_intel'),)
    bot.send_message(cid, 'which brand are you intrested in', reply_markup=markup)

 
def cpu_products_markup(brand, number , total):
    markup = InlineKeyboardMarkup()
    markup.add(    InlineKeyboardButton('<', callback_data=f'previous_cpu_{brand}_{number}'), types.InlineKeyboardButton(f'{number + 1}/{total}', callback_data='cancel'),     InlineKeyboardButton('>', callback_data=f'next_cpu_{brand}_{number}'))
    markup.add(InlineKeyboardButton(' add to the basket  ', callback_data=f'add_cpu_{brand}_{number}'))
    return markup
def show_cpus(call, brand, number, is_new_message=True):
    products = get_products_by_brand(brand)
    if products:
        product = products[number]
        cid = call.message.chat.id
        if is_new_message:
            bot.send_photo(cid, product['image_file_id'], caption=f"{product['name']}\n\n{product['description']}\nprice: {product['price']} $", reply_markup=cpu_products_markup(brand, number, len(products)))
        else:
            bot.edit_message_media(media=types.InputMediaPhoto(product['image_file_id']), chat_id=cid, message_id=call.message.message_id)
            bot.edit_message_caption(caption=f"{product['name']}\n\n{product['description']}\n price: {product['price']}", chat_id=cid, message_id=call.message.message_id, reply_markup=cpu_products_markup(brand, number, len(products)))

@bot.callback_query_handler(func=lambda call: call.data.startswith('get_cpu'))
def show_specific_cpu_brand_products(call):
    brand = call.data.split('_')[-1]
    show_cpus(call, brand, 0)

@bot.callback_query_handler(func=lambda call: call.data.startswith('next_cpu') or call.data.startswith('previous_cpu'))
def cpu_products_navigator(call):
    parts = call.data.split('_')
    brand, number = parts[2], int(parts[3])
    products = get_products_by_brand(brand)
    if call.data.startswith('previous_cpu'):
        number = (number - 1) % len(products)
    elif call.data.startswith('next_cpu'):
        number = (number + 1) % len(products)
    show_cpus(call, brand, number, is_new_message=False)

@bot.callback_query_handler(func=lambda call: call.data.startswith('add_cpu'))
def add_phone_to_cart(call):
    parts = call.data.split('_')
    brand, number = parts[2], int(parts[3])
    products = get_products_by_brand(brand)
    product = products[number]
    cid = call.message.chat.id
    user_cart = shopping_cart.get(cid, [])
    user_cart.append(product)
    shopping_cart[cid] = user_cart
    conn = mysql.connector.connect(user='root', password='password', host='localhost', database='shop')
    cursor = conn.cursor()
    cursor.execute("update product set inventory = inventory - 1 where id = %s", (product['id'],))
    conn.commit()
    cursor.close()
    conn.close()
    bot.answer_callback_query(call.id, text=f"{product['name']} the product was added to your basket successfully")



#__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________
@bot.message_handler(commands=['contact'])
def contact (message) :
    cid = message.chat.id
    text = """
telegram : 09191720094
whatsapp : 093481283610
email    : amirrezaafzalinia20@gmail.com

"""
    bot.send_message(cid , text )
#__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@bot.message_handler(commands=['about'])
def about (message) :
    cid = message.chat.id
    text = """we founded this shop to let people to choose from products of their desire and to make a safe place for people to purchase their products fast and easy and without any hastle
"""
    bot.send_message (cid , text)
#__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________

@bot.message_handler(func=lambda message: True)
def echo(message):
    cid=message.chat.id
    text=message.text
    bot.send_message(cid,text,reply_to_message_id=message.message_id)

bot.infinity_polling()
#__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________
