#! /usr/bin/env python3
# coding=utf-8

from pydantic import BaseSettings
import nonebot


# -----------
# 配置
# -----------
class Config(BaseSettings):
    # PIXIV
    refresh_token: str = ""  # PIXIV Token
    on_proxy: bool = False  # PIXIV代理开关
    proxy: str = ""  # PIXIV代理
    r18: bool = False  # PIXIV R18 开关(非网页中的设置，只是防止发出r18的p站图)
    pic_msg: bool = True  # PIXIV 图片消息与文字消息一起发送 开关
    on_temp: bool = True  # 缓存图片信息方便下次发送

    class Config:
        extra = "ignore"


global_config = nonebot.get_driver().config
pixiv_config = Config(**global_config.dict())  # 载入配置
