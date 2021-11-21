#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from asyncio import new_event_loop
from random import randint
import aiofiles
from loguru import logger
from nonebot import on_command, on_startswith
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment, Message, MessageEvent, GroupMessageEvent
from nonebot.plugin import on_message
from nonebot.typing import T_State

from .data_source import KEMO, kemodata, Q

kemo = on_command('kemo', priority=2, aliases={'k', 'ke', 'K', 'KEMO', 'KE', 'kemomimi', 'KEMOMIMI'})
ke_reply = on_message(priority=2)


@kemo.handle()
async def kemomm(bot: Bot, event: Event, state: T_State):
    api = KEMO()
    ids = randint(1, api.counts)
    resp = api.get_k_path(_id=ids)
    key = str(event.get_message()).strip()
    if key in ["上传", "upload"]:

        state["kemo"] = key
    elif not resp[0]:
        state["kemoo"] = True
        return await bot.send(event=event, message="数据库内找不到图片了呢~")
    else:
        state["kemoo"] = True
        mid = await bot.send(event=event, message=Message(
            MessageSegment.image(f"file:///{resp[1]}") + MessageSegment.text("kemomimi酱来了!")))
        return kemodata.insert({"mid": mid["message_id"], "id": ids})


@kemo.got("kemoo", prompt="请发出想要上传到kemo库的图片捏\n不要上传跟kemomimi酱无关的图片!!!!!")
async def kemooooooo(bot: Bot, event: GroupMessageEvent, state: T_State):
    if type(state["kemoo"]) == bool:
        return
    # logger.info(Message(state["pic"])[0].data["url"])  # 图片地址
    try:
        api = KEMO()
        imgs = [seg.data['url'] for seg in event.message if seg.type == 'image']
        await bot.send(event=event, message="您的图片已加入队列，请等待查重结果(预计3分钟)")
        loop = new_event_loop()
        for i in imgs:
            loop.run_until_complete(await api.upload(url=i, user=event.get_user_id(), tags=[], group_id=event.group_id))
    except KeyError:
        return await bot.send(event=event, message="不会吧不会吧，不会有人连图片都不会发吧！")


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
