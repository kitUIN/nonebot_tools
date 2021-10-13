import time
import aiofiles
import httpx
from loguru import logger
from tinydb import TinyDB, Query
import os
from pathlib import Path
from skimage.metrics import structural_similarity as compare_ssim
from imageio import imread
import numpy as np

dbPath = Path("db")
kemoPath = Path("kemo")
if not dbPath.is_dir() or not kemoPath.is_dir():
    if not kemoPath.is_dir():
        Path("kemo").mkdir()
        logger.success("kemo库创建成功")
    elif not dbPath.is_dir():
        Path("db").mkdir()
        logger.success("数据库目录创建成功")
else:
    logger.info("数据库与kemo目录已存在")
kemolist = TinyDB("./db/kemolist.json")
kemodata = TinyDB("./db/kemodata.json")
Q = Query()


class KEMO:
    def __init__(self):
        self.path = Path("kemo")
        self.counts = len(kemolist)

    @staticmethod
    def build_list(_id, path, user="admin", tags=None):
        if tags is None:
            tags = []
        date = time.localtime(time.time())
        infom = {
            "id": _id,
            "path": path.__str__(),
            "time": f"{date[0]}/{date[1]}/{date[2]} {date[3]}:{date[4]}:{date[5]}",
            "tags": tags,
            "uploader": user
        }
        info = kemolist.search(Q["id"] == _id)
        if info:
            kemolist.update(infom, Q["id"] == _id)
        else:
            kemolist.insert(infom)

    def get_k_path(self, _id) -> list:
        info = kemolist.search(Q["id"] == _id)
        if info:
            path = info[0]["path"]
            msg = f"编号:{info[0]['id']}\n位于:{path}\n上传时间:{info[0]['time']}\n" \
                  f"上传人:{info[0]['uploader']}\n添加的标签:{info[0]['tags']}"
            return [True, path, msg]
        else:
            return [False, "", "未找到该编号图片"]

    async def upload(self, url, user, tags):
        async with httpx.AsyncClient() as client:  # 下载
            async with client.stream("GET", url=url) as r:
                async with aiofiles.open(self.path.joinpath(f"{self.counts + 1}.jpg"), 'wb') as out_file:
                    async for chunk in r.aiter_bytes():
                        await out_file.write(chunk)
        flag = self.compare(self.path.joinpath(f"{self.counts + 1}.jpg"))
        if flag[0]:
            self.build_list(_id=self.counts + 1, path=self.path.joinpath(f"{self.counts + 1}.jpg"), user=user, tags=tags)
        return  flag

    def compare(self, path) -> list:
        names = [files for root, dirs, files in os.walk(self.path)][0]
        n = len(names)
        for i in range(n):
            logger.info(i + 1)
            img1 = imread(path)
            img2 = imread(self.path.joinpath(names[i]))
            img2 = np.resize(img2, (img1.shape[0], img1.shape[1], img1.shape[2]))
            ssim = compare_ssim(img1, img2, multichannel=True)
            # logger.success(f"{counts}:{names[i]}<-->{names[j]} ,相似度:{ssim}")
            if ssim > .9:
                logger.error(f"与{names[i]}重复")
                info = kemolist.search(Q["path"] == self.path.joinpath(names[i]))
                if info:
                    path = self.get_k_path(_id=info[0]["id"])
                return [False, path]
        return [True, "图片未收录，已经上传"]
