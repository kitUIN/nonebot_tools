#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime

import aiofiles
import httpx
import pyncm
from loguru import logger
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

Q = Query()


class Ncm:
    def __init__(self):
        self.api = pyncm.apis
        self.api.login.LoginViaCellphone(phone=ncm_config.phone, password=ncm_config.password)

    def detail(self, ids: list):
        songs: list = self.api.track.GetTrackDetail(song_ids=ids)["songs"]
        detail = [(data["name"] + "-" + ",".join([names["name"] for names in data["ar"]])) for data in songs]
        return detail

    async def playlist(self, id):  # 下载歌单
        data = self.api.playlist.GetPlaylistInfo(id)
        if data["code"] == 200:
            raw = data["playlist"]
            tags = ",".join(raw['tags'])
            info = f"歌单:{raw['name']}\r\n创建者:{raw['creator']['nickname']}\r\n歌曲总数:{raw['trackCount']}\r\n" \
                   f"标签:{tags}\r\n播放次数:{raw['playCount']}\r\n收藏:{raw['subscribedCount']}\r\n" \
                   f"评论:{raw['commentCount']}\r\n分享:{raw['shareCount']}"
            songs = [i['id'] for i in raw['trackIds']]
            return info

    async def download(self, ids: list):  # 下载音乐
        data: list = self.api.track.GetTrackAudio(song_ids=ids, bitrate=3200 * 1000)["data"]
        # logger.info(data)
        name: list = self.detail(ids)
        # logger.info(name)
        for i in range(len(ids)):
            if data[i]["code"] == 404:
                logger.error("未从网易云读取到下载地址")
            url = data[i]["url"]
            id = data[i]["id"]
            if url[-3:] == "mp3":
                mold = ".mp3"
            else:
                mold = ".flac"
            filename = name[i] + mold
            file = Path.cwd().joinpath("music").joinpath(filename).__str__()
            config = {
                "id": id,
                "file": file,
                "filename": filename,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            info = music.search(Q["id"] == id)
            if info:  # 数据库储存
                music.update(config, Q["id"] == id)
            else:
                music.insert(config)
            async with httpx.AsyncClient() as client:  # 下载歌曲
                async with client.stream("GET", url=url) as r:
                    async with aiofiles.open(file, 'wb') as out_file:
                        async for chunk in r.aiter_bytes():
                            await out_file.write(chunk)
