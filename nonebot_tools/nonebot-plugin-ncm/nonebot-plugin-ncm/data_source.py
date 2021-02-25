from pathlib import Path
from datetime import datetime

import httpx
import pyncm
from loguru import logger
from .config import ncm_config
from tinydb import TinyDB, Query

try:
    Path("music").mkdir()
    Path("db").mkdir()
    logger.success("音乐库创建成功")
except FileExistsError:
    logger.info("音乐库目录已存在")
music = TinyDB("./db/music.json")

Q = Query()


class Ncm:
    def __init__(self):
        self.api = pyncm.apis
        self.api.login.LoginViaCellphone(phone=ncm_config.phone, password=ncm_config.password)
    def detail(self, ids: list):
        songs: list = self.api.track.GetTrackDetail(song_ids=ids)["songs"]
        detail = list()
        for data in songs:
            ar = list()
            for names in data["ar"]:
                ar.append(names["name"])
            detail.append(data["name"] + "-" + ",".join(ar))
        return detail

    async def download(self, ids: list):  # 下载音乐
        data: list = self.api.track.GetTrackAudio(song_ids=ids, bitrate=3200 * 1000)["data"]
        name: list = self.detail(ids)
        for i in range(len(ids)):
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
            with open(file, "wb") as f:  # 下载歌曲
                async with httpx.AsyncClient() as client:
                    async with client.stream("GET", url) as response:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
