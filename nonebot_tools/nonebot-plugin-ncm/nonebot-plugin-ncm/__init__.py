#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Tuple, Any

import nonebot
from loguru import logger
from nonebot import on_regex, on_command, on_message
from nonebot.adapters import Message, Event
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, ActionFailed, GroupMessageEvent, PrivateMessageEvent
import re

from nonebot.matcher import Matcher
from nonebot.params import Received, EventMessage, CommandArg, State, RegexGroup
from nonebot.typing import T_State

from .data_source import Ncm, music, ncm_config, playlist, setting, Q,cmd

set = on_command("ncm", priority=1)  # 功能设置
music_regex = on_regex("(song|url)\?id=([0-9]+)(|&)", priority=ncm_config.ncm_priority)  # 歌曲id识别 (新增json识别)
playlist_regex = on_regex("playlist\?id=([0-9]+)&", priority=ncm_config.ncm_priority)  # 歌单识别
music_reply = on_message(priority=ncm_config.ncm_priority)  # 回复下载
search = on_regex("搜(歌|歌单|用户)", priority=ncm_config.ncm_priority)  # 搜东西


@music_regex.handle()
async def music_receive(bot: Bot, event: Event, regroup: Tuple[Any, ...] = RegexGroup()):
    logger.info(regroup[1])
    if event.dict()["message_type"] == "private":
        return await bot.send(event=event, message=Message(MessageSegment.text("私聊无法启用解析功能")))
    info = setting.search(Q["group_id"] == event.dict()["group_id"])
    logger.info(info)
    nid = regroup[1]
    if info:
        if info[0]["song"]:

            msg = f"歌曲ID:{nid}\r\n如需下载请回复该条消息\r\n关闭解析请使用指令\r\n{cmd}ncm f"
            await bot.send(event=event, message=Message(MessageSegment.text(msg)))

    else:
        setting.insert({"group_id": event.dict()["group_id"], "song": False, "list": False})


@playlist_regex.handle()
async def music_receive(bot: Bot, event: Event, regroup: Tuple[Any, ...] = RegexGroup()):
    if event.dict()["message_type"] == "private":
        return await bot.send(event=event, message=Message(MessageSegment.text("私聊无法启用解析功能")))
    info = setting.search(Q["group_id"] == event.dict()["group_id"])
    lid = regroup[0]
    logger.info(lid)
    if info:
        if info[0]["list"]:
            msg = await Ncm(bot, event).playlist(lid=lid)
            await bot.send(event=event, message=Message(MessageSegment.text(msg)))
    else:
        setting.insert({"group_id": event.dict()["group_id"], "song": False, "list": False})


@music_reply.handle()
async def music_reply_receive(bot: Bot, event: Event):
    if event.dict()["reply"] and event.dict()["reply"]["sender"]["user_id"] == event.self_id:
        try:  # 防止其他回复状况报错
            message: str = event.dict()["reply"]["message"][0].data["text"]
        except KeyError:
            return
        # logger.info(message)
        nid = re.search("ID:([0-9]*)", message)
        if nid:
            # logger.info(id)
            info = setting.search(Q["group_id"] == event.dict()["group_id"])
            if info:
                await Ncm(bot, event).download(ids=[int(nid[1])])
                data = music.search(Q["id"] == int(nid[1]))
                if data:
                    try:
                        await bot.call_api('upload_group_file', group_id=event.dict()["group_id"],
                                           file=data[0]["file"], name=data[0]["filename"])
                    except ActionFailed as e:
                        if e.info["wording"] == "server requires unsupported ftn upload":
                            await bot.send(event=event, message=Message(MessageSegment.text(
                                "[ERROR]  文件上传失败\r\n[原因]  机器人缺少上传文件的权限\r\n[解决办法]  请将机器人设置为管理员或者允许群员上传文件")))
                else:
                    logger.error("数据库中未有该音乐地址数据")
            else:
                logger.error("数据库中未发现该ID")
        else:
            lid = re.search("LIST:([0-9]*)", message)
            info = playlist.search(Q["playlist_id"] == lid[1])
            if info:

                await Ncm(bot, event).download(ids=info[0]["ids"])
                for i in info[0]["ids"]:
                    data = music.search(Q["id"] == i)
                    if data:
                        await bot.call_api('upload_group_file', group_id=event.dict()["group_id"],
                                           file=data[0]["file"], name=data[0]["filename"])
                    else:
                        logger.error("数据库中未有该音乐地址数据")
            else:
                logger.error("数据库中未发现该歌单ID")


@set.handle()
async def set_receive(bot: Bot, event: Event, args: Message = CommandArg()):  # 功能设置接收
    true = ["True", "T", "true", "t"]
    false = ["False", "F", "false", "f"]
    # logger.info(bot.__dict__)
    # logger.info(event.dict())

    logger.success(event.dict()['sender']['role'])
    if event.dict()['sender']['role'] in ncm_config.ncm_admin or str(event.get_user_id()) in ncm_config.superusers:
        if args:
            args = args.__str__().split()
            mold = args[0]
        else:
            msg = f"{cmd}ncm:获取命令菜单\r\n说明:网易云歌曲分享到群内后回复机器人即可下载\r\n{cmd}ncm t:开启解析\r\n{cmd}ncm f:关闭解析"
            await set.finish(message=MessageSegment.text(msg))
        info = setting.search(Q["group_id"] == event.dict()["group_id"])
        #logger.info(info)
        if info:
            if mold in true:
                logger.info(info)
                info[0]["song"] = True
                info[0]["list"] = True
                setting.update(info[0], Q["group_id"] == event.dict()["group_id"])
                msg = "已开启自动下载功能"
                await bot.send(event=event, message=Message(MessageSegment.text(msg)))
            elif mold in false:
                info[0]["song"] = False
                info[0]["list"] = False
                setting.update(info[0], Q["group_id"] == event.dict()["group_id"])
                msg = "已关闭自动下载功能"
                await bot.send(event=event, message=Message(MessageSegment.text(msg)))
        else:
            if mold in true:
                setting.insert({"group_id": event.dict()["group_id"], "song": True, "list": True})
            elif mold in false:
                setting.insert({"group_id": event.dict()["group_id"], "song": False, "list": False})
    else:
        await bot.send(event=event, message=Message(MessageSegment.text("你咩有权限哦~")))
