#! /usr/bin/env python3
# coding=utf-8
import asyncio
import json
import pathlib

import httpx
from loguru import logger
from nonebot import on_command, on_message
from nonebot import on_regex
from nonebot.adapters.cqhttp import Bot, Event, Message, MessageSegment

from .data_source import Setu, hso_config
from .model import Power

# -----------
# 事件响应
# -----------


# -----------------------------------------------------------------
setu = on_regex(pattern="来(.*?)[点丶份张幅](.*?)的?(|r18)[色瑟涩🐍][图圖🤮]", priority=1)
db = on_command("hso", priority=2)
reply = on_message(priority=3)
pic = on_command("查看")
asyncio.run(Power().update_all())


@setu.receive()
async def message_receive(bot: Bot, event: Event, state: dict):  # 涩图调用
    # logger.info(bot.__dict__)
    # logger.info(event.dict())
    # logger.info(state)
    await Setu(bot, event, state).main()


# -----------------------------------------------------------------

@db.handle()
async def db_update(bot: Bot, event: Event, state: dict):  # 数据库
    args = str(event.get_message()).strip().split()
    state["key"] = args
    # logger.info(bot.__dict__)
    # logger.info(event.dict())
    # logger.info(state)
    await Power().change(bot, event, state)


@reply.receive()
async def message_receive(bot: Bot, event: Event, state: dict):
    # logger.info(event.dict())
    replay = event.dict()["reply"]
    if replay and str(replay["sender"]["user_id"]) in hso_config.bot:
        await Setu(bot, event, state).get_text(message_id=event.dict()["reply"]["message_id"])


@pic.handle()
async def pic(bot: Bot, event: Event, state: dict):  # 数据库
    # logger.info(bot.__dict__)
    # logger.info(event.dict())
    # logger.info(state)
    args = str(event.get_message()).strip().split()
    url = args[0]
    if url[:4] == "http":
        await bot.send(message=Message(MessageSegment.image(url)), event=event)
    else:
        key = "https://pixiv.cat/{}.jpg".format(url)
        await bot.send(message=Message(MessageSegment.image(key)), event=event)
