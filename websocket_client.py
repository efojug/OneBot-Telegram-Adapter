import asyncio
import json
import websockets
from onebot_adapter import OneBotAdapter

async def websocket_handler(bot, config):
    adapter = OneBotAdapter(bot)

    try:
        me = bot.get_me()
        self_id = me.id
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
            try:
                print(f"尝试连接OneBot WebSocket: {url}")
                async with websockets.connect(url, extra_headers=headers) as ws:
                    print("成功连接到OneBot WebSocket")
                    async for message in ws:
                        print(f"接收到OneBot数据: {message}")
                        response_data = None
                        try:
                            data = json.loads(message)
                            action = data["action"]
                            params = data["params"]
                            if params:
                                if isinstance(params, str):
                                    try:
                                        params_obj = json.loads(params)
                                    except json.JSONDecodeError:
                                        params_obj = None
                                        print(f"Missing params!! {params}")
                                        response_data = {
                                            "status": "failed",
                                            "retcode": 1400,
                                            "data": None,
                                            "message": "Missing params.",
                                        }
                                else:
                                    params_obj = None
                            if action:
                                response_data = await adapter.handle_action(action, params_obj)
                            else:
                                print(f"Missing action!! {action}")
                                response_data = {
                                    "status": "failed",
                                    "retcode": 1400,
                                    "data": None,
                                    "message": "Missing action.",
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


            except websockets.exceptions.ConnectionClosed as e:
                print(f"WebSocket 连接关闭: {e}\n 将在10秒后自动重连")

            except Exception as e:
                print(f"WebSocket 连接/接收时出错!! {e}\n 将在10秒后自动重连")

            finally:
                if 'ws' in bot.bot_data:  # Clear ws if connection drops
                    bot.bot_data['ws'] = None
                await asyncio.sleep(10)