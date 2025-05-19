from pyrogram import Client, filters
import datetime
import time
from database.users_chats_db import db
from info import ADMINS
from utils import users_broadcast, groups_broadcast, temp, get_readable_time
import asyncio
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup 

lock = asyncio.Lock()

@Client.on_callback_query(filters.regex(r'^broadcast_cancel'))
async def broadcast_cancel(bot, query):
    _, ident = query.data.split("#")
    if ident == 'users':
        await query.message.edit("ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ᴜsᴇʀs ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...")
        temp.USERS_CANCEL = True
    elif ident == 'groups':
        temp.GROUPS_CANCEL = True
        await query.message.edit("ᴛʀʏɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ ɢʀᴏᴜᴘs ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...")
       
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_users(bot, message):
    if lock.locked():
        return await message.reply('Currently broadcast processing, Wait for complete.')

    msg = await message.ask('<b>Do you want pin this message in users?</b>', reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True))
    if msg.text == 'Yes':
        is_pin = True
    elif msg.text == 'No':
        is_pin = False
    else:
        return await msg.edit('Wrong Response!')
    await msg.delete()
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    b_sts = await message.reply_text(text='<b>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ʏᴏᴜʀ ᴍᴇssᴀɢᴇs ᴛᴏ ᴜsᴇʀs ⌛️</b>')
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0
    success = 0

    async with lock:
        async for user in users:
            time_taken = get_readable_time(time.time()-start_time)
            if temp.USERS_CANCEL:
                temp.USERS_CANCEL = False
                await b_sts.edit(f"Users broadcast Cancelled!\nCompleted in {time_taken}\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done} / {total_users}</code>\nSuccess: <code>{success}</code>")
                return
            sts = await users_broadcast(int(user['id']), b_msg, is_pin)
            if sts == 'Success':
                success += 1
            elif sts == 'Error':
                failed += 1
            done += 1
            if not done % 20:
                btn = [[
                    InlineKeyboardButton('CANCEL', callback_data=f'broadcast_cancel#users')
                ]]
                await b_sts.edit(f"Users broadcast in progress...\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done} / {total_users}</code>\nSuccess: <code>{success}</code>", reply_markup=InlineKeyboardMarkup(btn))
        await b_sts.edit(f"Users broadcast completed.\nCompleted in {time_taken}\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done} / {total_users}</code>\nSuccess: <code>{success}</code>")

        
@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS))
async def broadcast_group(bot, message):
    b_msg = await bot.ask(chat_id = message.from_user.id, text = "Nᴏᴡ Sᴇɴᴅ Mᴇ Yᴏᴜʀ Bʀᴏᴀᴅᴄᴀsᴛ Mᴇssᴀɢᴇ")
    groups = await db.get_all_chats()
    sts = await message.reply_text(
        text='Bʀᴏᴀᴅᴄᴀsᴛɪɴɢ ʏᴏᴜʀ ᴍᴇssᴀɢᴇs Tᴏ Gʀᴏᴜᴘs...'
    )
    start_time = time.time()
    total_groups = await db.total_chat_count()
    done = 0
    failed = 0

    success = 0
    async for group in groups:
        pti, sh = await groups_broadcast(int(group['id']), b_msg)
        if pti:
            success += 1
        elif sh == "Error":
                failed += 1
        done += 1
        if not done % 20:
            await sts.edit(f"Bʀᴏᴀᴅᴄᴀsᴛ ɪɴ ᴘʀᴏɢʀᴇss:\n\nTᴏᴛᴀʟ Gʀᴏᴜᴘs {total_groups}\nCᴏᴍᴘʟᴇᴛᴇᴅ: {done} / {total_groups}\nSᴜᴄᴄᴇss: {success}")    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"Bʀᴏᴀᴅᴄᴀsᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ:\nCᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ {time_taken} sᴇᴄᴏɴᴅs.\n\nTᴏᴛᴀʟ Gʀᴏᴜᴘs {total_groups}\nCᴏᴍᴘʟᴇᴛᴇᴅ: {done} / {total_groups}\nSᴜᴄᴄᴇss: {success}")
    
