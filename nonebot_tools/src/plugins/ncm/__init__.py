import httpx
from loguru import logger
from nonebot import on_regex, on_command
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment, Message
from tinydb import TinyDB, Query

from .config import Config
from .data_source import Ncm, music

setting = TinyDB("./db/setting.json")
Q = Query()
y = on_command("", priority=1)
x = on_regex("com/m/song/([0-9]*)/", priority=2)


@x.receive()
async def message_receive(bot: Bot, event: Event, state: dict):

    info = setting.search(Q["group_id"] == event.dict()['group_id'])
    if info:
        if info[0]["song"]:
            msg = "检测到网易云歌曲(id:{id})\r\n如需下载请使用指令\r\n#下载 {id}\r\n关闭自动下载请使用指令\r\n#关闭 ncm".format(
                id=state["_matched_groups"][0])
            await bot.send(event=event, message=Message(MessageSegment.text(msg)))
            await Ncm().download(ids=list(state["_matched_groups"]))
    else:
        setting.insert({"group_id": event.dict()['group_id'], "song": True})


@y.handle()
async def message_receive1(bot: Bot, event: Event, state: dict):
    args = str(event.get_message()).strip().split()
    state["key"] = args

    mold = state["key"][0]
    info = setting.search(Q["group_id"] == event.dict()['group_id'])
    if info:
        if mold == "下载":
            data = music.search(Q["id"] == int(state["key"][1]))[0]
            if info[0]["song"]:
                params = {
                    "group_id": event.dict()['group_id'],
                    "file": data["file"],
                    "name": data["filename"]
                }
                async with httpx.AsyncClient() as client:
                    res = await client.post("http://127.0.0.1:5700/upload_group_file", params=params)

        elif mold == "开启":
            info[0]["song"] = True
            setting.update(info, Q["group_id"] == event.dict()['group_id'])
            msg = "已开启自动下载功能"
            await bot.send(event=event, message=Message(MessageSegment.text(msg)))
        elif mold == "关闭":
            info[0]["song"] = False
            setting.update(info, Q["group_id"] == event.dict()['group_id'])
            msg = "已关闭自动下载功能"
            await bot.send(event=event, message=Message(MessageSegment.text(msg)))

    else:
        setting.insert({"group_id": event.dict()['group_id'], "song": True})
