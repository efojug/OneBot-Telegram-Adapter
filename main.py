import asyncio
import json
# from typing import Coroutine, Optional

from telegram.ext import MessageHandler, filters, Application

from config import load_config
from websocket_client import websocket_handler

def _handle_ws_send_result(fut: asyncio.Future, event_details: str):
    try:
        fut.result()
    except Exception as e:
        print(f"WebSocket send operation for event {event_details} failed: {e}")

async def do_nothing()-> None:
    ...

async def telegram_message_to_onebot(update, context) -> None:
    message = update.effective_message
    if not message or not message.from_user:
        return

    user = message.from_user
    nickname = user.username or (user.first_name + (user.last_name if user.last_name else ''))
    if not nickname:
        nickname = "匿名用户"

    time = message.date.timestamp()
    self_id = context.bot.get_me().id
    raw_text = message.text or ""

    event = {
        "time": int(time),
        "post_type": "message",
        "self_id": self_id
    }

    if message.chat.type in ["group", "supergroup"]:
        event.update({
            "message": [{"type": "text", "data": {"text": raw_text}}],
            "font": 0,
            "raw_message": raw_text,
            "message_type": "group",
            "sub_type": "normal",
            "message_id": message.message_id,
            "group_id": message.chat.id,
            "user_id": user.id,
            "sender": {
                "user_id": user.id,
                "nickname": nickname,
                "sex": "",
                "age": 0
            }
        })
    elif message.chat.type == "private":
        event.update({
            "message": [{"type": "text", "data": {"text": raw_text}}],
            "font": 0,
            "raw_message": raw_text,
            "message_type": "private",
            "sub_type": "friend",
            "message_id": message.message_id,
            "user_id": user.id,
            "sender": {
                "user_id": user.id,
                "nickname": nickname,
                "sex": "",
                "age": 0
            }
        })
    else:
        print(f"不支持的消息来源: {message.chat.type}")
        return

    ws = context.bot_data.get('ws')
    main_loop = context.bot_data.get('loop')

    if ws and main_loop:
        try:
            event_json = json.dumps(event)
            coro = ws.send(event_json)
            future = asyncio.run_coroutine_threadsafe(coro, main_loop)
            future.add_done_callback(lambda fut: _handle_ws_send_result(fut, f"type {event['message_type']}, id {message.message_id}"))
            print(f"Scheduled event to be sent to OneBot: (msg_id: {message.message_id})")
        except Exception as e:
            print(f"发送OneBot事件失败!! {e}")

    else:
        if not ws: print("WebSocket connection ('ws') not available in bot_data.")
        if not main_loop: print("Asyncio event loop ('loop') not available in bot_data.")
    return None

def main():
    config = load_config()
    builder = Application.builder().token(config.telegram_token)

    proxy_url = config.proxy_url
    if config.proxy_url and config.proxy_url.strip():
        if not proxy_url.lower().startswith("http://" or "https://" or "socks://"):
            proxy_url = "http://" + proxy_url

        print(f"Using proxy: {proxy_url}")
        builder.proxy(proxy_url).get_updates_proxy(proxy_url).build()

    application = builder.build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_message_to_onebot))

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    bot = application.bot
    bot_data = application.bot_data
    bot_data['ws'] = None
    bot_data['loop'] = loop

    print("Starting telegram bot polling.")

    try:
        loop.run_until_complete(websocket_handler(bot, config))
    except KeyboardInterrupt:
        print("正在优雅关闭Adapter...")
        application.stop()

    application.run_polling()

if __name__ == "__main__":
    main()