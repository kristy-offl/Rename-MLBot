import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import pyrogram
from config import Config 
from pyrogram import Client, Filters, InlineKeyboardButton, InlineKeyboardMarkup
from translation import Translation
from Tools.Download import download

my_father = "https://t.me/{}".format(Config.USER_NAME[1:])
support = "https://telegram.dog/Ns_Bot_supporters"
@Client.on_message(Filters.command(["start"]))
async def start(c, m):

    await c.send_message(chat_id=m.chat.id,
                         text=Translation.START.format(m.from_user.first_name, Config.USER_NAME),
                         reply_to_message_id=m.message_id,
                         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("My Father 👨‍💻", url=my_father), InlineKeyboardButton("📌Support channel", url=support)]]))
    logger.info(f"{m.from_user.first_name} used start command")



@Client.on_message(Filters.command(["help"]))
async def help(c, m):

    await c.send_message(chat_id=m.chat.id,
                         text=Translation.HELP,
                         reply_to_message_id=m.message_id,
                         parse_mode="markdown")


@Client.on_message(Filters.command(["about"]))
async def about(c, m):

    await c.send_message(chat_id=m.chat.id,
                         text=Translation.ABOUT,
                         disable_web_page_preview=True,
                         reply_to_message_id=m.message_id,
                         parse_mode="markdown")

@Client.on_message(Filters.command(["converttovideo"]))
async def video(c, m):
  if m.from_user.id in Config.BANNED_USER:
      await c.send_message(chat_id=m.chat.id, text=Translation.BANNED_TEXT)
  if m.from_user.id not in Config.BANNED_USER:
    if m.reply_to_message is not None:
      await download(c, m)
    else:
       await c.send_message(chat_id=m.chat.id, text=Translation.REPLY_TEXT)

@Client.on_message(Filters.command(["converttofile"]))
async def file(c, m):
  if m.from_user.id in Config.BANNED_USER:
      await c.send_message(chat_id=m.chat.id, text=Translation.BANNED_TEXT)
  if m.from_user.id not in Config.BANNED_USER:
    if m.reply_to_message is not None:
      await download(c, m)
    else:
       await c.send_message(chat_id=m.chat.id, text=Translation.REPLY_TEXT)
 
@Client.on_message(filters.command(["rename"]))
async def rename(bot, update):
    update_channel = Config.UPDATE_CHANNEL
    if update_channel:
        try:
            user = await bot.get_chat_member(update_channel, update.chat.id)
            if user.status == "kicked":
               await update.reply_text(Scripted.ACCESS_DENIED)
               return
        except UserNotParticipant:
            await update.reply_text(text=Scripted.JOIN_NOW_TEXT,
                  reply_markup=InlineKeyboardMarkup( [ [ InlineKeyboardButton(text="ᴊᴏɪɴ ɴᴏᴡ 🔓", url=f"https://t.me/{Config.UPDATE_CHANNEL}") ]
                ] 
              )
            )
            return
        except Exception:
            await update.reply_text(Scripted.CONTACT_MY_DEVELOPER)
            return

    if (" " in update.text) and (update.reply_to_message is not None):
        cmd, file_name = update.text.split(" ", 1)
        new_file = file_name[:60] + file_name[-4:]
        description = Scripted.CUSTOM_CAPTION.format(file_name)
        download_location = Config.DOWNLOAD_LOCATION + "/"
        c = await bot.send_message(
            chat_id=update.chat.id,
            text=Scripted.TRYING_TO_DOWNLOAD,
            reply_to_message_id=update.message_id
        )
        c_time = time.time()
        the_real_download_location = await bot.download_media(
            message=update.reply_to_message,
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=(Scripted.DOWNLOAD_START, c, c_time) )

        if the_real_download_location is not None:
            try:
                await bot.edit_message_text(
                    text=Scripted.TRYING_TO_UPLOAD,
                    chat_id=update.chat.id,
                    message_id=c.message_id
                )
            except:
                pass
            new_file_name = download_location + file_name
            os.rename(the_real_download_location, new_file_name)
            logger.info(the_real_download_location)
            thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
            if not os.path.exists(thumb_image_path):
                mes = await sthumb(update.from_user.id)
                if mes != None:
                    m = await bot.get_messages(update.chat.id, mes.msg_id)
                    await m.download(file_name=thumb_image_path)
                    thumb_image_path = thumb_image_path
                else:
                    thumb_image_path = None
            else:
                width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                img.resize((320, height))
                img.save(thumb_image_path, "JPEG")
            c_time = time.time()
            await bot.send_document(
            chat_id=update.chat.id,
            document=new_file_name,
            thumb=thumb_image_path,
            caption=description,
            reply_to_message_id=update.reply_to_message.message_id,
            progress=progress_for_pyrogram,
            progress_args=(Scripted.UPLOAD_START, c, c_time))

            try:
                os.remove(the_real_download_location)
                os.remove(thumb_image_path)
            except:
                pass
            await bot.edit_message_text(
                  text=Scripted.UPLOAD_SUCCESS,
                  chat_id=update.chat.id,
                  message_id=c.message_id
            )

    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Scripted.REPLY_TO_FILE,
            reply_to_message_id=update.message_id)
