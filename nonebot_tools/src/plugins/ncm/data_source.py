import pathlib
from datetime import datetime

import httpx
import pyncm
from loguru import logger
from .config import config
from tinydb import TinyDB, Query

try:
    pathlib.Path("music").mkdir()
    pathlib.Path("db").mkdir()
    logger.success("音乐库创建成功")
except FileExistsError:
    logger.info("音乐库目录已存在")
music = TinyDB("./db/music.json")

Q = Query()


class Ncm:
    def __init__(self):
        self.api = pyncm.apis
        self.api.login.LoginViaCellphone(phone=config.phone, password=config.password)

    def detail(self, ids: list):
        songs: list = self.api.track.GetTrackDetail(song_ids=ids)['songs']
        detail = list()
        for data in songs:
            ar = list()
            for names in data["ar"]:
                ar.append(names["name"])
            detail.append(data["name"] + "-" + ",".join(ar))
        return detail

    async def download(self, ids: list, path: str = './music/'):  # [29043459,1363620027]
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
            filepath = path + filename
            paths = ["music", filename]
            config = {
                "id": id,
                "file": pathlib.Path.cwd().parent.joinpath(*paths),
                "filename": filename,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            info = music.search(Q["id"] == id)
            if info:
                music.update(config, Q["id"] == id)
            else:
                music.insert(config)
            with open(filepath, "wb") as f:
                async with httpx.AsyncClient() as client:
                    async with client.stream("GET", url) as response:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
