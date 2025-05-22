from telegram import Bot
from telegram.error import TelegramError

class OneBotApi:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_private_msg(self, user_id: int, message_segments, auto_scape: bool = False) -> int:
        text = ""
        reply_id = None

        for seg in message_segments:
            t = seg.get("type")
            data = seg.get("data", {})
            if t == "reply":
                reply_id = data.get("id")
            elif t == "text":
                text += data.get("text", "")

        try:
            result = await self.bot.send_message(chat_id=user_id, text=text.strip(), reply_to_message_id=reply_id)
            return result.message_id
        except TelegramError as e:
            print(f"发送私聊消息失败!! {e} : chat_id={user_id}, text={text}, reply_id={reply_id}")
            raise

    async def send_group_msg(self, group_id: int, message, auto_escape: bool = False) -> int:
        text = ""
        reply_id = None
        mentions = []

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
                result = await self.bot.send_message(chat_id=group_id, text=text.strip(), reply_to_message_id=reply_id)
                return result.message_id
            except TelegramError as e:
                print(f"发送群聊消息失败!! {e} : chat_id={group_id}, text={text}, reply_id={reply_id}")
                raise

    async def get_group_info(self, group_id: int) -> {}:
        chat_full_info = await self.bot.get_chat(group_id)
        return {
        "group_all_shut": 0,
        "group_remark": "",
        "group_id": group_id,
        "group_name": chat_full_info.title,
        "member_count": await self.bot.get_chat_member_count(chat_id=group_id),
        "max_member_count": 2000
        }