import asyncio
import json
from typing import Coroutine

from telegram.ext import MessageHandler, filters, Application

from config import load_config
from websocket_client import websocket_handler

async def do_nothing()-> None:
    ...

async def telegram_message_to_onebot(update, context) -> Coroutine:
    message = update.effective_message
    if message is None or message.from_user is None:
        # TODO how to return
        return do_nothing()
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
        # TODO how to return *2
        return do_nothing()

    ws = context.bot_data.get('ws')
    if ws:
        try:
            asyncio.run_coroutine_threadsafe(ws.send(json.dumps(event)), context.bot_data['loop'])
        except Exception as e:
            print(f"发送OneBot事件失败!! {e}")


def main():
    config = load_config()
    if config.proxy_url.strip() == "": application = Application.builder().token(config.telegram_token).proxy(config.proxy_url).get_updates_proxy(config.proxy_url).build()
    else: application = Application.builder().token(config.telegram_token).build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_message_to_onebot))
    application.start_polling()
    bot = application.bot
    loop = asyncio.get_event_loop()
    bot_data = application.bot_data
    bot_data['ws'] = None
    bot_data['loop'] = loop

    try:
        loop.run_until_complete(websocket_handler(bot, config))
    except KeyboardInterrupt:
        print("正在优雅关闭Adapter...")
    finally:
        application.stop()
        loop.stop()

if __name__ == "__main__":
    main()