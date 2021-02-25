#! /usr/bin/env python3
# coding=utf-8
from loguru import logger
from pydantic import BaseSettings
import nonebot


# -----------
# 配置
# -----------
class Config(BaseSettings):
    # 全局
    superusers: list = [0]  # 超级管理员
    priority: tuple = (0, 1)  # 优先级(1,2,3)表示api1->api2->api3
    api1 = True  # setu库开启状况 api1=lolicon
    friend: bool = True  # 好友开关
    lolicon_key: str = ""  # lolicon Key
    bot: str = ""  # 机器人QQ号

    class Config:
        extra = "ignore"


global_config = nonebot.get_driver().config
hso_config = Config(**global_config.dict())  # 载入配置
logger.info(hso_config)
