import asyncio
import json
import websockets
from websockets import ConnectionClosed

from onebot_adapter import OneBotAdapter

async def websocket_handler(application, config):
    adapter = OneBotAdapter(application.bot)

    try:
        me = await application.bot.get_me()
        self_id = me.id
        print(f"Bot ID: {self_id} ({me.username}) 连接成功.")
    except Exception as e:
        print(f"获取Bot ID失败!! {e}")
        return

    url = config.onebot_websocket_url
    if not url.lower().startswith("ws://"):
        url = f"ws://{url}"

    headers = [
        ("X-Self-ID", str(self_id)),
        ("X-Client-Role", "Universal")
    ]

    if config.onebot_websocket_token:
        headers.append(("Authorization", f"Bearer {config.onebot_websocket_token}"))

    while True:
        print(f"尝试连接OneBot WebSocket: {url}")
        application.bot_data['ws'] = None
        try:
            async with websockets.connect(url, additional_headers=headers) as ws:
                application.bot_data['ws'] = ws
                print("成功连接至OneBot")
                async for message in ws:
                    print(f"接收到OneBot数据: {message}")
                    response_data = None
                    decoded_data = {}
                    try:
                        decoded_data = json.loads(message)
                        action = decoded_data.get('action')
                        params = decoded_data.get("params", {})

                        if action:
                            response_data = await adapter.handle_action(action, params)
                        else:
                            print(f"Missing action in message: {message}")
                            response_data = {
                                "status": "failed",
                                "retcode": 1400,
                                "data": None,
                                "message": "Missing 'action' field in request.",
                            }

                    except json.JSONDecodeError:
                        print(f"处理OneBot消息出错!! Invalid JSON {message}")
                        response_data = {
                            "status": "failed",
                            "retcode": 1400,
                            "data": None,
                            "message": "Invalid JSON received"
                        }

                    except Exception as e:
                        print(f"处理OneBot消息出错!! {e}")
                        response_data = {
                            "status": "failed",
                            "retcode": 1,
                            "data": None,
                            "message": f"Error processing message: {str(e)}"
                        }

                    if response_data:
                        try:
                            await ws.send(json.dumps(response_data))
                            print(f"Sent response: {json.dumps(response_data)}")
                        except Exception as e:
                            print(f"发送响应失败!! {e}")


        except ConnectionClosed as e:
            print(f"WebSocket 连接关闭: {e}\n将在10秒后自动重连")

        except ConnectionRefusedError as e:
            print(f"OneBot WebSocket connection refused by server {e}.\nReconnecting in 10s...")

        except Exception as e:
            print(f"WebSocket 连接/接收时出错!! {e}\n将在10秒后自动重连")

        finally:
            if application.bot_data.get('ws') is not None:  # Clear ws if connection drops
                application.bot_data['ws'] = None
            print("等待10秒...")
            await asyncio.sleep(10)