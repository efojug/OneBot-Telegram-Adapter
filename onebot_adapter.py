import json
from onebot_api import OneBotApi

class OneBotAdapter:
    def __init__(self, bot):
        self.api = OneBotApi(bot)

    def handle_action(self, action: str, params: dict):
        if action == 'send_group_msg':
            if params is None:
                print("Error: send_group_msg() 缺少参数!!")
                return
            try:
                group_ud = int(params.get('group_id', 0))
                message_array = params.get('messages', [])
                auto_escape = params.get('auto_escape', False)
                self.api.send_group_msg(group_ud, message_array, auto_escape)
            except Exception as e:
                print(f"Error: send_group_msg failed!! {e}")

        elif action == 'send_private_msg':
            if params is None:
                print("Error: send_private_msg() 缺少参数!!")
                return
            try:
                user_id = int(params.get('user_id', 0))
                message_array = params.get('messages', [])
                auto_escape = params.get('auto_escape', False)
                self.api.send_private_msg(user_id, message_array, auto_escape)
            except Exception as e:
                print(f"Error: send_private_msg failed!! {e}")