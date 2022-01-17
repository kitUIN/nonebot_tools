#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime

import aiofiles
import httpx
import nonebot

from pyncm import apis
from pyncm.apis.cloudsearch import CloudSearchType
from loguru import logger
from nonebot.adapters.onebot.v11 import MessageSegment, Message

from .config import ncm_config
from tinydb import TinyDB, Query

dbPath = Path("db")
musicPath = Path("music")
if not dbPath.is_dir() or not musicPath.is_dir():
    if not musicPath.is_dir():
        Path("music").mkdir()
        logger.success("音乐库创建成功")
    elif not dbPath.is_dir():
        Path("db").mkdir()
        logger.success("数据库目录创建成功")
else:
    logger.info("数据库与音乐库目录已存在")
music = TinyDB("./db/music.json")
playlist = TinyDB("./db/playlist.json")
setting = TinyDB("./db/setting.json")
Q = Query()
cmd = list(nonebot.get_driver().config.command_start)[0]
#  白名单导入
for ids in ncm_config.whitelist:
    info = setting.search(Q["group_id"] == ids)
    if info:
        info[0]["song"] = True
        info[0]["list"] = True
        setting.update(info[0], Q["group_id"] == ids)
    else:
        setting.insert({"group_id": ids, "song": True, "list": True})


class Ncm:
    def __init__(self, bot, event):
        self.api = apis
        self.api.login.LoginViaCellphone(phone=ncm_config.ncm_phone, password=ncm_config.ncm_password)
        self.bot = bot
        self.event = event

    def detail(self, ids: list):
        songs: list = self.api.track.GetTrackDetail(song_ids=ids)["songs"]
        detail = [(data["name"] + "-" + ",".join([names["name"] for names in data["ar"]])) for data in songs]
        return detail

    @staticmethod
    def build_song(data):
        resp = {"msg": "", "ids": []}
        num = 1
        for i in data:
            resp["msg"] += f"{num}.[歌曲:{i['name']}](id:{i['id']})  作者:{i['ar']['name']}(id:){i['ar']['id']}\r\n"
            resp["ids"].append(i['id'])
            num += 1
        return resp

    async def search_song(self, keyword, limit=5):  # 搜索歌曲
        res = self.api.cloudsearch.GetSearchResult(keyword=keyword, type=CloudSearchType.SONG, limit=limit)
        return self.build_song(res["result"]["songs"])

    async def search_user(self, keyword, limit=5):  # 搜索用户
        self.api.cloudsearch.GetSearchResult(keyword=keyword, type=CloudSearchType.USER, limit=limit)

    async def search_playlist(self, keyword, limit=5):  # 搜索歌单
        self.api.cloudsearch.GetSearchResult(keyword=keyword, type=CloudSearchType.PLAYLIST, limit=limit)

    async def playlist(self, lid):  # 下载歌单
        data = self.api.playlist.GetPlaylistInfo(lid)
        # logger.info(data)
        if data["code"] == 200:
            raw = data["playlist"]
            tags = ",".join(raw['tags'])
            msg = f"歌单:{raw['name']}\r\n创建者:{raw['creator']['nickname']}\r\n歌曲总数:{raw['trackCount']}\r\n" \
                  f"标签:{tags}\r\n播放次数:{raw['playCount']}\r\n收藏:{raw['subscribedCount']}\r\n" \
                  f"评论:{raw['commentCount']}\r\n分享:{raw['shareCount']}\r\nLIST:{lid}" \
                  f"\r\n如需下载请回复该条消息\r\n关闭解析请使用指令\r\n{cmd}ncm f"
            songs = [i['id'] for i in raw['trackIds']]
            info = playlist.search(Q["playlist_id"] == lid)
            if info:
                info[0]["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                playlist.update(info[0], Q["playlist_id"] == lid)
            else:
                config = {
                    "playlist_id": lid,
                    "counts": raw['trackCount'],  # 歌曲总数
                    "ids": songs,  # id列表
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取时间
                }
                playlist.insert(config)
            return msg

    async def download(self, ids: list):  # 下载音乐
        data: list = self.api.track.GetTrackAudio(song_ids=ids, bitrate=3200 * 1000)["data"]
        # logger.info(data)
        name: list = self.detail(ids)
        # logger.info(name)
        num = 1
        for i in range(len(ids)):
            if data[i]["code"] == 404:
                logger.error("未从网易云读取到下载地址")
                return
            url = data[i]["url"]
            nid = data[i]["id"]
            filename = f"{name[i]}.{data[i]['type']}"
            file = Path.cwd().joinpath("music").joinpath(filename)
            config = {
                "id": nid,
                "file": file.__str__(),  # 获取文件位置
                "filename": filename,  # 获取文件名
                "from": "song" if len(ids) == 1 else "list",  # 判断来自单曲还是歌单
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取时间
            }
            info = music.search(Q["id"] == nid)
            if info:  # 数据库储存
                music.update(config, Q["id"] == nid)
            else:
                music.insert(config)
            async with httpx.AsyncClient() as client:  # 下载歌曲
                async with client.stream("GET", url=url) as r:
                    async with aiofiles.open(file, 'wb') as out_file:
                        async for chunk in r.aiter_bytes():
                            await out_file.write(chunk)
            if len(ids) > 1:
                if num//10 == 0 or num==len(ids):
                    await self.bot.send(event=self.event, message=Message(MessageSegment.text(f"下载进度:{num}/{len(ids)}")))
                num += 1
