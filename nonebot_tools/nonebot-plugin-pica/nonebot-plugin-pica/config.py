import nonebot
from pydantic import BaseSettings


class Config(BaseSettings):
    bika_account: str = ""
    bika_password: str = ""
    bika_token: str= ""

    class Config:
        extra = "ignore"


global_config = nonebot.get_driver().config
bika_config = Config(**global_config.dict())  # 载入配置
