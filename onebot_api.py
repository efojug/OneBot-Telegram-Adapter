from telegram import Bot
from telegram.error import TelegramError

class OneBotApi:
    def __init__(self, bot: Bot):
        self.bot = bot

    def send_private_message(self, user_id: int, message, auto_scape: bool = False) -> int:
        text = ""
        reply_id = None
        for seg in message:
            t = seg.get("type")
            data = seg.get("data", {})
            if t == "reply":
                reply_id = data.get("id")
            elif t == "text":
                text += data.get("text", "")

        try:
            result = self.bot.send_message(chat_id=user_id, text=text, reply_to_message_id=reply_id)
            return result.message_id
        except TelegramError as e:
            print(f"发送私聊消息失败!! {e} : chat_id={user_id}, text={text}, reply_id={reply_id}")
            raise

    def send_group_msg(self, group_id: int, message, auto_escape: bool = False) -> int:
        text = ""
        reply_id = None
        for seg in message:
            t = seg.get("type")
            data = seg.get("data", {})
            if t == "reply":
                reply_id = data.get("id")
            elif t == "text":
                text += data.get("text", "")
            elif t == "at":
                text += "@" + data.get("qq", "")

            try:
                result = self.bot.send_message(chat_id=group_id, text=text, reply_to_message_id=reply_id)
                return result.message_id
            except TelegramError as e:
                print(f"发送群聊消息失败!! {e} : chat_id={group_id}, text={text}, reply_id={reply_id}")
                raise