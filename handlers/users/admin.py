import asyncio
import os
import random
from telethon import TelegramClient, Button, events 
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.exceptions import Unauthorized

from keyboards.inline.menu import back_admin, admin_menu, choose_menu
from loader import dp, bot
from states.states import BroadcastState, GiveTime, TakeTime
from utils.db_api.db_commands import select_all_users, del_user, update_date
from calendar import c
from email import message
import random
from telethon.tl.custom import Button
from datetime import datetime
import asyncio
from keyboards.inline.menu import back_to_main_menu,  api_hash, api_id, code_menu, \
    main_menu, proxy_menu, start_spam_menu, accept_spam_menu, STOP
import socks
from telethon.tl.functions.channels import JoinChannelRequest
from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import InputChannel
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import os, sys
import configparser
import csv
import time
import random
#from data.config import api_id, api_hash
#from loader import scheduler
import os

from datetime import datetime, timedelta

@dp.callback_query_handler(text="give_time")
async def edit_commission(call: CallbackQuery, state: FSMContext):
    msg_to_edit = await call.message.edit_text("<b>🆔Введите ID человека:</b>",
                                               reply_markup=back_admin)
    await GiveTime.GT1.set()
    await state.update_data(msg_to_edit=msg_to_edit)


@dp.message_handler(state=GiveTime.GT1)
async def receive_com(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    user_id = message.text
    await message.delete()
    await GiveTime.next()
    await state.update_data(user_id=user_id)
    await msg_to_edit.edit_text("<b>⏰Введите время в часах которое выдать человеку:</b>", reply_markup=back_admin)


@dp.message_handler(state=GiveTime.GT2)
async def receive_com(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit, user_id = data.get("msg_to_edit"), data.get("user_id")
    try:
        hours = int(message.text)
        await message.delete()
        date_when_expires = datetime.now() + timedelta(hours=hours)
        date_to_db = str(date_when_expires).split(".")[0].replace("-", " ").split(":")
        date_to_db = " ".join(date_to_db[:-1])
        await update_date(user_id, date_to_db)
        await state.finish()
        await msg_to_edit.edit_text("<b>Доступ выдан.</b>", reply_markup=back_admin)
    except ValueError:
        await msg_to_edit.edit_text("<b>⏰Не верный формат, попробуйте еще раз.</b>")


@dp.callback_query_handler(text="take_time")
async def edit_commission(call: CallbackQuery, state: FSMContext):
    msg_to_edit = await call.message.edit_text("<b>🆔Введите ID человека:</b>",
                                               reply_markup=back_admin)
    await TakeTime.T1.set()
    await state.update_data(msg_to_edit=msg_to_edit)


@dp.message_handler(state=TakeTime.T1)
async def receive_com(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    user_id = message.text
    await message.delete()
    await update_date(user_id, None)
    await state.finish()
    await msg_to_edit.edit_text("<b>У юзера больше нет доступа.</b>", reply_markup=back_admin)


# ========================BROADCAST========================
# ASK FOR PHOTO AND TEXT
@dp.callback_query_handler(text="broadcast")
async def broadcast2(call: CallbackQuery):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer("<b>Отправь фото  которое будут рассылаться по юзерам</b>", reply_markup=back_to_main_menu)
    await BroadcastState.BS1.set()


# RECEIVE PHOTO OR TEXT
@dp.message_handler(content_types=['photo'], state=BroadcastState.BS1)
async def broadcast4(message: Message, state: FSMContext):
    await message.delete()
    easy_chars = 'abcdefghijklnopqrstuvwxyz1234567890'
    name = 'cicada'
    photo_name = name + ".jpg"
    await message.photo[-1].download(f"pics/broadcast/{photo_name}")
    await state.update_data(photo=photo_name, text=message.caption)
    await asyncio.sleep(2)
    await message.answer("Фото успешно загруженно", reply_markup=back_to_main_menu)



@dp.callback_query_handler(text="fdel")
async def fdel(call: CallbackQuery):
    try:
        path = f'pics/broadcast/cicada.jpg'
        os.remove(path)
        await call.message.answer("Фото Удаленно", reply_markup=back_to_main_menu)
    except:
        await call.message.answer("Фото Удаленно", reply_markup=back_to_main_menu)


@dp.callback_query_handler(text="go_start")
async def broadcast_text_post(call: CallbackQuery):
    try:
        kart = os.listdir("pics/broadcast")
        if kart[0] == 'cicada.jpg':
            path = f'pics/broadcast/cicada.jpg'
            with open(path, 'rb') as f:
                photo = f.read()
            ssm = open('sms.txt', 'r').read()
            zz = ssm.split('|')
            sms = random.choice(zz)
            await call.message.answer_photo(photo=photo, caption=f"{ssm}\n\n"
                                                            f"<b>Все правильно? Отправляем?</b>",
                                    reply_markup=choose_menu)
    except:
        ssm = open('sms.txt', 'r').read()
        zz = ssm.split('|')
        sms = random.choice(zz)
        await call.message.answer(ssm + "\n\n<b>Все правильно? Отправляем?</b>", reply_markup=choose_menu)


@dp.callback_query_handler(text="STOP")
async def st(call: CallbackQuery):
    with open("status.txt", "w") as f:
        f.write("1")

# START BROADCAST
@dp.callback_query_handler(text="yes")
async def broadcast_text_post(call: CallbackQuery):
    users = open('ussers.txt', 'r').readlines()
    msg_to_delete = await call.message.answer("<b>Рассылка начата</b>")
    path = f'pics/broadcast/cicada.jpg'
    try:
        with open(path, 'rb') as f:
            photo = f.read()
    except:pass
    tt = open('time.txt', 'r')
    ti = int(tt.read())
    tt.close()
    api_id = 7265064
    api_hash = "9ec54c3437a4b240456f08dd3276f5c3"
    with open("status.txt", "w") as f:
        f.write("0")
    
    file_list = os.listdir('sessions')
    xx = len(file_list)
    i = 1
    t = 0
    m = 0
    mx = 40
    msm = 0
    while i <= xx:
        mm = 0
        try:
            stat = open("status.txt", "r").read()
            if stat == 1:
                break
            file_list = os.listdir('sessions')
            acaunt = file_list[i]
            client = TelegramClient(f"sessions/{acaunt}", api_id, api_hash)
            await client.connect()
            me = await client.get_me()
        except:
            await client.disconnect()
            os.remove(f"sessions/{acaunt}")
            
        try:
            ss = open('ussers.txt', 'r').readlines()
            z = len(ss)
            count = int(z)
        except:
            await call.message.answer('Список получателей пуст !')
            await client.disconnect() 
            break
        for x in range(count):
            try:
                if mm <= 5:
                    stat = open("status.txt", "r").read()
                    if stat == 1:
                        await call.message.answer("STOP")
                        i = xx
                    try:
                        ssm = open('sms.txt', 'r').read()
                        zz = ssm.split('|')
                        sms = random.choice(zz)
                        await client.send_file(ss[x][:-1], file=photo, caption=sms)
                    except:
                        ssm = open('sms.txt', 'r').read()
                        zz = ssm.split('|')
                        sms = random.choice(zz)
                        await client.send_message(ss[x][:-1], sms)
                    msm = msm + 1
                    mm = mm + 1
                    await call.message.edit_text(
                        f"<b>В Рассылку запущенно {xx} Акаунтов</b>\n"
                        f"<b>Подключен Акаунт №<code>{i}</code></b>\n"
                        f"<b>Отправляю этот текст:</b> \n\n"
                        f"{sms}"
                        f"<b>Пользователю:</b> <code>{ss[x][:-1]}</code>\n"
                        f"<b>Тайминг паузы установлен на {ti} секунд</b>\n"
                        f"<b>Всего отправленно смс:</b>    <code>{msm}</code>\n"
                    )
                    time.sleep(ti)
                    
            except:
                
                break
        
        i = i + 1
        
    await msg_to_delete.delete()



# CANCEL BROADCAST
@dp.callback_query_handler(text="xxx")
async def exitt(call: CallbackQuery):
    await call.message.edit_text("<b>меню</b>", reply_markup=back_to_main_menu)

