import os
import sys
import yaml
from dataclasses import dataclass

@dataclass
class Config:
    telegram_token: str
    onebot_websocket_url: str
    onebot_websocket_token: str

def load_config(path: str = "config.yml") -> Config:
    if not os.path.exists(path):
        print("Config file not found, Creating...")
        template = {
            'telegram_token': '<TELEGRAM_BOT_TOKEN>',
            'onebot_websocket_url': '<ONEBOT_WEBSOCKET_URL>',
            'onebot_websocket_token': '<ONEBOT_WEBSOCKET_TOKEN>',
        }
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(template, f, allow_unicode=True)
        print("配置文件已创建，请编辑后再次运行")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    try:
        config = Config(
            telegram_token=data['telegram_token'],
            onebot_websocket_url=data['onebot_websocket_url'],
            onebot_websocket_token=data['onebot_websocket_token'],
        )
    except KeyError as e:
        print(f"配置文件缺少{e}，请检查或者删除配置文件")
        sys.exit(-1)
    return config