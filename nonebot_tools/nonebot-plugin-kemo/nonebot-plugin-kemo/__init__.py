#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from random import randint
import aiofiles
from loguru import logger
from nonebot import on_command, on_startswith
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment, Message, MessageEvent
from nonebot.plugin import on_message
from nonebot.typing import T_State

from .data_source import KEMO, kemodata, Q

kemo = on_command('kemo', priority=2, aliases={'k', 'ke', 'K', 'KEMO', 'KE', 'kemomimi', 'KEMOMIMI'})
ke_reply = on_message(priority=2)
upload = on_command('kemoupload', priority=2)


@kemo.handle()
async def kemo(bot: Bot, event: Event, state: dict):
    api = KEMO()
    ids = randint(1, api.counts)
    resp = api.get_k_path(_id=ids)
    if resp[0]:
        mid = await bot.send(event=event, message=Message(
            MessageSegment.image(f"file:///{resp[1]}") + MessageSegment.text("kemomimi酱来了!")))
        kemodata.insert({"mid": mid["message_id"], "id": ids})
    else:
        await bot.send(event=event, message="数据库内找不到图片了呢~")


@ke_reply.receive()
async def kemo_reply(bot: Bot, event: Event, state: dict):
    if event.dict()["reply"] and event.dict()["reply"]["sender"]["user_id"] == event.self_id:
        logger.info(event.dict()["reply"]["message_id"])
        try:  # 防止其他回复状况报错
            message: str = event.dict()["reply"]["message"][1].data["text"]
            if message == "kemomimi酱来了!":
                api = KEMO()
                info = kemodata.search(Q["mid"] == event.dict()["reply"]["message_id"])
                if info:
                    resp = api.get_k_path(_id=info[0]["id"])
                    if resp[0]:
                        await bot.send(event=event, message=resp[2])

        except KeyError:
            return


@upload.handle()
async def search_receive(bot: Bot, event: Event, state: dict):
    args = str(event.get_message()).strip()
    if args:
        state["kem"] = args


@upload.got("kem", prompt="请发出想要上传到kemo库的图片捏")
async def handle_city(bot: Bot, event: MessageEvent, state: T_State):
    # logger.info(Message(state["pic"])[0].data["url"])  # 图片地址
    try:
        api = KEMO()
        msg = await api.upload(url=Message(state["pic"])[0].data["url"], user=event.get_user_id(), tags=[])
        if msg[0]:
            await bot.send(event=event, message=MessageSegment.image(f"file:///{msg[0]}"))
        else:
            await bot.send(event=event, message=msg)
    except KeyError:
        await bot.send(event=event, message="不会吧不会吧，不会有人连图片都不会发吧！")
