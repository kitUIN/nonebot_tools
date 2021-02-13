import nonebot
from pydantic import BaseSettings


class Config(BaseSettings):
    # plugin custom config
    plugin_setting: str = "default"
    phone: str = ""
    password: str = ""

    class Config:
        extra = "ignore"


global_config = nonebot.get_driver().config
config = Config(**global_config.dict())  # 载入配置
