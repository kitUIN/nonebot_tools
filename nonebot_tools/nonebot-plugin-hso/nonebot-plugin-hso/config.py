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
    priority: tuple = (1, 2)  # 优先级(1,2,3)表示api1->api2->api3
    friend: bool = True  # 好友开关
    lolicon_key: str = ""  # lolicon Key
    bot: str = ""  # 机器人QQ号
    refresh_token: str = ""  # pixiv token
    pixiv: bool = False  # pixiv开关
    pixiv_proxy: bool = False  # pixiv代理开关
    mongo_host: str = ""
    mongo_port: str = ""

    class Config:
        extra = "ignore"


global_config = nonebot.get_driver().config
hso_config = Config(**global_config.dict())  # 载入配置
# logger.info(hso_config)
