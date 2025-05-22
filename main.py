import asyncio
import json

from pycparser.ply.yacc import token
from telegram.ext import Updater, MessageHandler, CommandHandler
from config import load_config
from websocket_client import websocket_handler


def telegram_message_to_onebot(bot, update, context):
    message = update.effective_message
    if message is None or message.from_user is None:
        return
    user = message.from_user
    nickname = user.username or (user.first_name + (user.last_name or ''))
    if not nickname:
        nickname = "匿名用户"
    time = message.date.timestamp()
    self_id = context.bot.get_me().id
    raw_text = message.text or ""
    event = {
        "time": int(time),
        "self_id": self_id,
        "post_type": "message",
        "message": [{"type": "text", "data": {"text": raw_text}}],
        "raw_message": raw_text,
        "font": 0,
        "sender": {
            "user_id": user.id,
            "nickname": nickname,
            "sex": "",
            "age": 0
        }
    }
    if message.chat.type in ["group", "supergroup"]:
        event.update({
            "message_type": "group",
            "sub_type": "normal",
            "message_id": message.message_id,
            "group_id": message.chat.id,
            "user_id": user.id
        })
    elif message.chat.type == "private":
        event.update({
            "message_type": "private",
            "sub_type": "friend",
            "message_id": message.message_id,
            "user_id": user.id,
        })
    else:
        print(f"不支持的消息来源: {message.chat.type}")
        return

    ws = context.bot_data.get('ws')
    if ws:
        try:
            asyncio.run_coroutine_threadsafe(ws.send(json.dumps(event)), context.bot_data['loop'])
        except Exception as e:
            print(f"发送OneBot事件失败!! {e}")


def main():
    config = load_config()
    updater = Updater(token=config.telegram_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & (Filters.chat_type.groups | Filters.chat_type.supergroup), telegram_message_to_onebot))
    dp.add_handler(MessageHandler(Filters.text & Filters.chat_type.private, telegram_message_to_onebot))
    updater.start_polling()
    bot = updater.bot
    loop = asyncio.get_event_loop()
    bot_data = updater.dispatcher.bot_data
    bot_data['ws'] = None

    bot_data['loop'] = loop
    try:
        loop.run_until_complete(websocket_handler(bot, config))
    except KeyboardInterrupt:
        pass
    finally:
        updater.stop()
        loop.stop()

if __name__ == "__main__":
    main()