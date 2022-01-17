#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Union

import nonebot
from loguru import logger
from nonebot import on_regex, on_command, on_message

from nonebot.adapters import Message, Event
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, ActionFailed, GroupMessageEvent, PrivateMessageEvent
from .data_source import Pixiv, pixivlist, Q, pixiv_config, pixivhistory
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.typing import T_State

pixiv = on_command("pixiv", aliases={"p"}, priority=2)
uixiv = on_command("u", aliases={"uid"}, priority=2)
pixiv_reply = on_message(priority=2)
pixiv_api = Pixiv()
cmd = list(nonebot.get_driver().config.command_start)[0]


@pixiv.handle()
async def pixiv_look(bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent],
                     args: Message = CommandArg()):
    args = args.__str__().split()
    if len(args) == 2:
        if args[0] in ["p", "pid", "id", "i", "P", "Pid", "PID"]:
            if pixiv_config.on_temp:
                info = pixivlist.search(Q["pid"] == int(args[1]))
                if info:
                    resp = info[0]["data"]
                    logger.info(info)
                    msg = info[0]["msg"]
                    if pixiv_config.pic_msg:
                        await bot.send(event=event, message=Message(
                            [MessageSegment.image(i) for i in resp] +
                            MessageSegment.text(msg + "\n") +
                            MessageSegment.at(event.get_user_id())))
                    else:
                        mid = await bot.send(event=event, message=Message(MessageSegment.reply(event.message_id)+[MessageSegment.image(i) for i in resp]))
                        pixivhistory.insert({"mid": mid['message_id'], "msg": msg, "data": resp})
                    return
            pid = int(args[1])
            await pixiv_api.send_illust_detail(pid=pid, bot=bot, event=event)
        elif args[0] in ["u", "uid", "Uid", "UID", "U"]:
            uid = int(args[1])
            await pixiv_api.send_usr_detail(uid=uid, bot=bot, event=event)
    else:
        await bot.send(event=event, message=f"{cmd}pixiv pid p站id 查看图片\n{cmd}pixiv uid p站用户id 查看用户")


@uixiv.handle()
async def uixiv_look(bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent],
                     args: Message = CommandArg()):
    args = args.__str__().split()
    uid = int(args[0])
    await pixiv_api.send_usr_detail(uid=uid, bot=bot, event=event)


@pixiv_reply.handle()
async def pixiv_reply_look(bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent]):
    logger.info(event.reply)
    if event.reply:
        logger.info(event.reply.message_id)
        info = pixivhistory.search(Q['mid'] == event.reply.message_id)
        logger.info(info)
        if info:
            # resp = info[0]["data"]
            msg = info[0]["msg"]
            await bot.send(event=event,
                           message=Message(MessageSegment.text(msg + "\n") + MessageSegment.at(event.get_user_id())))
