import json
from onebot_api import OneBotApi

class OneBotAdapter:
    def __init__(self, bot):
        self.api = OneBotApi(bot)

    async def handle_action(self, action: str, params: dict):
        response = {
            "status": "failed",
            "retcode": 1,
            "data": None,
            "message": ""
        }
        try:

            if action == 'send_group_msg':
                if params is None:
                    print("Error: send_group_msg() 缺少参数!!")
                    return
                try:
                    group_ud = int(params.get('group_id', 0))
                    message_array = params.get('messages', [])
                    auto_escape = params.get('auto_escape', False)
                    message_id = await self.api.send_group_msg(group_ud, message_array, auto_escape)
                    response.update({
                        "status": "ok",
                        "retcode": 0,
                        "data": {
                            "message_id": message_id
                        },
                        "message": "",
                        "wording": ""
                    })
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
                    message_id = await self.api.send_private_msg(user_id, message_array, auto_escape)
                    response.update({
                        "status": "ok",
                        "retcode": 0,
                        "data": {
                            "message_id": message_id
                        },
                        "message": "",
                        "wording": ""
                    })
                except Exception as e:
                    print(f"Error: send_private_msg failed!! {e}")


            elif action == 'get_group_info':
                if params is None:
                    print("Error: get_group_info() 缺少参数!!")

                    response.update({
                        "status": "failed",
                        "retcode": 1003,
                        "message": "Missing 'group_id' parameter."
                    })

                    return response

                try:
                    group_id = int(params.get('group_id', 0))

                    if not group_id:
                        raise ValueError("Invalid group_id: 0")

                    group_data = await self.api.get_group_info(group_id)

                    response.update({
                        "status": "ok",
                        "retcode": 0,
                        "data": group_data,
                        "message": ""
                    })

                except ValueError as ve:
                    print(f"Error: get_group_info failed!! {ve}")
                    response.update({
                        "status": "failed",
                        "retcode": 1002,
                        "message": str(ve)
                    })

                except Exception as e:
                    print(f"Error: get_group_info failed!! {e}")
                    response["message"] = f"Error executing get_group_info: {e}"

            else:
                print(f"Unknown action!! {action}")
                response["message"] = f"Unknown action: {action}"
                response["retcode"] = 1404

        except Exception as e:
            print(f"Error: {action} failed!! {e}")
            response["message"] = f"Error executing {action}: {e}"
            response["retcode"] = 1

        return response