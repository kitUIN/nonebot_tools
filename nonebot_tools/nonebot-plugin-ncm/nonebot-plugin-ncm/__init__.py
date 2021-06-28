#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from loguru import logger
from nonebot import on_regex, on_command, on_message
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment, Message
from tinydb import TinyDB, Query
import re
from .data_source import Ncm, music, ncm_config

setting = TinyDB("./db/setting.json")
Q = Query()
set = on_command("ncm", priority=1)  # 功能设置
music_regex = on_regex("song\?id=([0-9]+)&", priority=1)  # 歌曲id识别 (新增json识别)
playlist_regex = on_regex("com\/playlist\/([0-9]*)\/|com\\\/playlist\\\/([0-9]*)\\\/", priority=1)  # 歌单识别
reply = on_message(priority=2)  # 回复下载


@music_regex.receive()
async def music_receive(bot: Bot, event: Event, state: dict):
    # logger.info(event.get_type())
    if event.dict()["message_type"] == "private":
        return await bot.send(event=event, message=Message(MessageSegment.text("私聊无法启用解析功能")))
    # logger.info(bot.__dict__)
    # logger.info(event.dict())
    # logger.info(state)
    info = setting.search(Q["group_id"] == event.dict()["group_id"])
    id = list(filter(None, state["_matched_groups"]))  # 去除None
    if info:
        if info[0]["song"]:
            msg = f"歌曲ID:{id[0]}\r\n如需下载请回复该条消息\r\n关闭解析请使用指令\r\n#ncm f"
            await bot.send(event=event, message=Message(MessageSegment.text(msg)))
            await Ncm().download(ids=id)
    else:
        setting.insert({"group_id": event.dict()["group_id"], "song": True})

"""
@playlist_regex.receive()
async def music_receive(bot: Bot, event: Event, state: dict):
    # logger.info(event.get_type())
    if event.dict()["message_type"] == "private":
        return await bot.send(event=event, message=Message(MessageSegment.text("私聊无法启用解析功能")))
    logger.info(bot.__dict__)
    logger.info(event.dict())
    logger.info(state)
    id = list(filter(None, state["_matched_groups"]))[0]  # 去除None
    msg = await Ncm().playlist(id=id)
    await bot.send(event=event, message=Message(MessageSegment.text(msg)))
"""

@reply.receive()
async def message_receive(bot: Bot, event: Event, state: dict):
    # logger.info(event.dict())
    _reply = event.dict()["reply"]
    if _reply and str(_reply["sender"]["user_id"]) in ncm_config.bot:
        try:  # 防止其他回复状况报错
            message: str = _reply["message"][0].data["text"]
        except KeyError:
            return
        # logger.info(message)
        id = re.search("ID:([0-9]*)", message)
        # logger.info(id)
        info = setting.search(Q["group_id"] == event.dict()["group_id"])
        if info:
            data = music.search(Q["id"] == int(id[1]))
            if info[0]["song"]:
                await bot.call_api('upload_group_file', group_id=event.dict()["group_id"],
                                   file=data[0]["file"], name=data[0]["filename"])
            else:
                logger.error("数据库中未有该音乐地址数据")
        else:
            logger.error("数据库中未发现该ID")


@set.handle()
async def set_receive(bot: Bot, event: Event, state: dict):  # 功能设置接收
    true = ["True", "T", "true", "t"]
    false = ["False", "F", "false", "f"]
    args = str(event.get_message()).strip().split()
    state["key"] = args
    # logger.info(bot.__dict__)
    # logger.info(event.dict())
    #  logger.info(state)
    if state["key"]:
        mold = state["key"][0]
    else:
        cmd = list(nonebot.get_driver().config.command_start)[0]
        msg = f"{cmd}ncm:获取命令菜单\r\n{cmd}ncm t:开启解析\r\n{cmd}ncm f:关闭解析"
        return await bot.send(event=event, message=Message(MessageSegment.text(msg)))
    info = setting.search(Q["group_id"] == event.dict()["group_id"])
    if info:
        if mold in true:
            info[0]["song"] = True
            setting.update(info, Q["group_id"] == event.dict()["group_id"])
            msg = "已开启自动下载功能"
            await bot.send(event=event, message=Message(MessageSegment.text(msg)))
        elif mold in false:
            info[0]["song"] = False
            setting.update(info, Q["group_id"] == event.dict()["group_id"])
            msg = "已关闭自动下载功能"
            await bot.send(event=event, message=Message(MessageSegment.text(msg)))
    else:
        setting.insert({"group_id": event.dict()["group_id"], "song": True})
