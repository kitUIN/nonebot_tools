import nonebot
from pydantic import BaseSettings


class Config(BaseSettings):
    # plugin custom config
    plugin_setting: str = "default"
    phone: str = ""
    password: str = ""
    bot: str = ""

    class Config:
        extra = "ignore"


global_config = nonebot.get_driver().config
ncm_config = Config(**global_config.dict())  # 载入配置
