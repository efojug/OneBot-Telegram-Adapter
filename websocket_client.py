import asyncio
import json
import websockets
from onebot_adapter import OneBotAdapter

async def websocket_handler(bot, config):
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
            headers.append(("X-Client-Token", config.onebot_websocket_token))

        while True:
            try:
                print(f"尝试连接OneBot WebSocket: {url}")
                async with websockets.connect(url, extra_headers=headers) as ws:
                    print("成功连接到OneBot WebSocket")
                    async for message in ws:
                        print(f"接收到OneBot数据: {message}")
                        try:
                            data = json.loads(message)
                            action = data["action"]
                            params = data["params"]
                            if params is not None:
                                if isinstance(params, str):
                                    try:
                                        params_obj = json.loads(params)
                                    except json.JSONDecodeError:
                                        params_obj = None
                                else:
                                    params_obj = None
                                OneBotAdapter.handle_action(action, params_obj)
                        except Exception as e:
                            print(f"处理OneBot消息出错!! {e}")
            except Exception as e:
                print(f"WebSocket 连接/接收时出错!! {e}\n 将在10秒后自动重连")
                await asyncio.sleep(10)