import telebot
from telebot import types
from PIL import Image, ImageDraw, ImageFont
import io

bot = telebot.TeleBot('token')

def generate_id_card(name, id_number, nation, address, issuing_authority, expiration_date, user_photo):

    if len(id_number) < 18:
        raise ValueError("身份证号码格式不正确，必须至少18位.")
    
    birth_date = id_number[6:14]

    gender_code = int(id_number[-2]) 
    gender = '女' if gender_code % 2 == 0 else '男'  
    
    id_card_template = Image.open('empty.png')

    name_font = ImageFont.truetype('fonts/hei.ttf', 72)
    other_font = ImageFont.truetype('fonts/hei.ttf', 64)
    birth_date_font = ImageFont.truetype('fonts/fzhei.ttf', 60)
    id_font = ImageFont.truetype('fonts/ocrb10bt.ttf', 90)

    draw = ImageDraw.Draw(id_card_template)
    draw.text((630, 690), name, font=name_font, fill='black') 
    draw.text((630, 840), gender, font=other_font, fill='black') 
    draw.text((1030, 840), nation, font=other_font, fill='black')
    draw.text((630, 975), birth_date[:4], font=birth_date_font, fill='black')  
    draw.text((950, 975), birth_date[4:6], font=birth_date_font, fill='black') 
    draw.text((1150, 975), birth_date[6:], font=birth_date_font, fill='black') 
    draw.text((630, 1115), address, fill=(0, 0, 0), font=other_font)
    draw.text((900, 1475), id_number, fill=(0, 0, 0), font=id_font)
    draw.text((1050, 2750), issuing_authority, fill=(0, 0, 0), font=other_font)
    draw.text((1050, 2895), expiration_date, fill=(0, 0, 0), font=other_font)

    user_photo_resized = user_photo.resize((500, 670))
    id_card_template.paste(user_photo_resized, (1500, 690))

    img_buffer = io.BytesIO()
    id_card_template.save(img_buffer, format='PNG')
    img_buffer.seek(0) 
    return img_buffer

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    welcome_message = "欢迎使用sfz加工机器人！点击下面的按钮开始制作身份证。发送 /sfz 开始加工\n有事联系 @love_521_bot"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = types.KeyboardButton("/start")
    sfz_button = types.KeyboardButton("/sfz")
    markup.add(start_button, sfz_button)
    
    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)

@bot.message_handler(commands=['sfz'])
def handle_sfz_command(message):
    try:
        bot.reply_to(message, "输入姓名、身份证号码、民族、地址、签发机关和有效期，每项之间用空格分隔。")
        bot.register_next_step_handler(message, process_sf_info)
    
    except Exception as e:
        bot.reply_to(message, f"发生错误：{e}")

def process_sf_info(message):
    try:
        command_args = message.text.split()
        if len(command_args) != 6:
            raise ValueError("格式为：姓名 身份证号码 民族 地址 签发机关 有效期")
        
        name = command_args[0]
        id_number = command_args[1]
        nation = command_args[2]
        address = command_args[3]
        issuing_authority = command_args[4]
        expiration_date = command_args[5]
        
        # 提示用户发送照片
        bot.reply_to(message, "请发送一张照片作为身份证照片。")
        bot.register_next_step_handler(message, process_photo, name, id_number, nation, address, issuing_authority, expiration_date)
    
    except Exception as e:
        bot.reply_to(message, f"发生错误：{e}")

def process_photo(message, name, id_number, nation, address, issuing_authority, expiration_date):
    try:
        if message.photo:
            # 发送正在制作的提示信息
            bot.reply_to(message, "正在制作！请稍后...有问题联系\n @love_521_bot \n您也可以选择加入我们的群组 https://t.me/Love_baby_Group 以此来询问群友")

            photo = message.photo[-1].file_id
            file_info = bot.get_file(photo)
            downloaded_file = bot.download_file(file_info.file_path)

            # 将照片加载为Image对象
            user_photo = Image.open(io.BytesIO(downloaded_file))

            # 生成身份证图片
            img_buffer = generate_id_card(name, id_number, nation, address, issuing_authority, expiration_date, user_photo)

            # 发送生成的图片给用户
            bot.send_photo(message.chat.id, img_buffer)

        else:
            bot.reply_to(message, "请发送一张有效的照片作为身份证照片。")

    except Exception as e:
        bot.reply_to(message, f"发生错误：{e}")

# 启动机器人
bot.polling()
