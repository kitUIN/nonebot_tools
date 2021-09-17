#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PicImageSearch import NetWork, AsyncSauceNAO
from loguru import logger
from nonebot import on_regex, on_command, on_message
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment, Message, MessageEvent
from nonebot.typing import T_State

search = on_command("搜图", priority=1)  # 功能设置


@search.handle()
async def search_receive(bot: Bot, event: Event, state: dict):
    args = str(event.get_message()).strip()
    if args:
        state["pic"] = args


@search.got("pic", prompt="请发出想要搜索的图片")
async def handle_city(bot: Bot, event: MessageEvent, state: T_State):
    # logger.info(Message(state["pic"])[0].data["url"])  # 图片地址
    try:
        pic = await get_pic_info(Message(state["pic"])[0].data["url"])
        await search.finish(Message([MessageSegment.text(pic), MessageSegment.at(event.get_user_id())]))
    except KeyError:
        await bot.send(event=event, message="不会吧不会吧，不会有人连图片都不会发吧！")


async def get_pic_info(url):
    async with NetWork(proxy='http://127.0.0.1:10809') as client:  # 可以设置代理 NetWork(proxy='http://127.0.0.1:10809')
        saucenao = AsyncSauceNAO(api_key="54a8d90c583d3b66b6dd3d7e9001a39b588cd842", client=client)  # client不能少
        res = await saucenao.search(url=url)
        if res is None:
            return "搜图失败了呢，询问下开发者吧~"
        msg = f"相似度:{res.raw[0].similarity}%\r\n标题:{res.raw[0].title}\r\nPixiv_Id:(www.pixiv.net/artworks/{res.raw[0].pixiv_id})\r\n作者:{res.raw[0].author}(www.pixiv.net/users/{res.raw[0].member_id})\r\n"
        return msg
