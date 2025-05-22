import asyncio
import json
import sys


from telegram.ext import MessageHandler, filters, Application

from config import load_config
from websocket_client import websocket_handler

def _handle_ws_send_result(fut: asyncio.Future, event_details: str):
    try:
        fut.result()
        print("事件发送成功")
    except Exception as e:
        print(f"事件发送失败: {event_details}\n因为: {e}")

async def telegram_message_to_onebot(update, context) -> None:
    message = update.effective_message
    if not message or not message.from_user:
        return

    user = message.from_user
    nickname = user.username or (user.first_name + (user.last_name if user.last_name else ''))
    if not nickname:
        nickname = "匿名用户"

    time = message.date.timestamp()
    me = await context.bot.get_me()
    self_id = me.id
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

    if ws:
        try:
            event_json = json.dumps(event)
            send_task = asyncio.create_task(ws.send(event_json))
            send_task.add_done_callback(
                lambda fut: _handle_ws_send_result(fut, f"type {event['message_type']}, id {message.message_id}")
            )
            print(f"收到消息，计划发送至OneBot message_id: {message.message_id}")
        except Exception as e:
            print(f"发送OneBot事件失败!! {e}")

    else:
        if not ws: print("WebSocket connection ('ws') not available in bot_data.")
    return None

def main():
    config = load_config()
    builder = Application.builder().token(config.telegram_token)

    proxy_url = config.proxy_url
    if config.proxy_url and config.proxy_url.strip():
        if not proxy_url.lower().startswith(("http://", "https://", "socks4://", "socks5://")):
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

    bot_data = application.bot_data
    bot_data['ws'] = None
    bot_data['loop'] = loop

    websocket_client_task = loop.create_task(websocket_handler(application, config))

    print("Starting telegram bot polling.")

    try:
        application.run_polling(close_loop=False)

    except KeyboardInterrupt:
        print("正在优雅关闭Adapter...")

    finally:
        if websocket_client_task and not websocket_client_task.done():
            websocket_client_task.cancel()
            try:
                if loop.is_running():
                    loop.run_until_complete(websocket_client_task)

            except asyncio.CancelledError:
                print("WebSocket client closed.")

        if not loop.is_closed():
            loop.close()

        print("Application Closed!!")
        sys.exit(0)

if __name__ == "__main__":
    main()