import datetime
import os
from typing import Optional, Union
import re
from loguru import logger
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, Message, Event, GroupMessageEvent, PrivateMessageEvent
from nonebot.typing import T_State
from pixivpy_async import *
from tinydb import TinyDB, Query
from .config import pixiv_config
from pathlib import Path


Q = Query()
dbPath = Path("db")
pidsPath = Path("pids")
if not dbPath.is_dir() or not pidsPath.is_dir():
    if not pidsPath.is_dir():
        Path("pids").mkdir()
        logger.success("pixiv图库创建成功")
    elif not dbPath.is_dir():
        Path("db").mkdir()
        logger.success("数据库目录创建成功")
else:
    logger.info("数据库与pixiv图库已存在")
pixivlist = TinyDB("./db/pixivlist.json")
pixivhistory = TinyDB("./db/pixivhistory.json")

class Pixiv:

    def __init__(self):
        if pixiv_config.refresh_token == "":
            logger.warning("未输入refresh_token值,将自动启动无代理模式")
            pixiv_config.on_proxy = False
        else:
            self.token = pixiv_config.refresh_token
        if pixiv_config.proxy or pixiv_config.on_proxy:
            self.api = AppPixivAPI(proxy=pixiv_config.proxy)
        else:
            pass

    async def login(self):
        """
        登陆

        :return:
        """
        try:
            await self.api.login(refresh_token=self.token)
            logger.success("登录成功")
        except Exception as e:
            logger.error(f"登录失败:{e}")
            logger.error("请检查配置文件中refresh_token值")

    async def send_illust_detail(self, pid: Union[str, int], bot: Bot, event: Union[GroupMessageEvent,PrivateMessageEvent]):
        """
        发送p站图片

        :param pid: pixiv 图片id
        :param bot: BOT
        :param event: EVENT
        :return:
        """
        await self.login()
        flag = False
        try:
            res = await self.api.illust_detail(int(pid))
            if "illust" in res.keys():
                r = re.match("([0-9]*)-([0-9]*)-([0-9]*)T([0-9]*):([0-9]*):([0-9]*)\+([0-9]*):([0-9]*)",
                             res['illust']['create_date'])
                date = datetime.datetime.strftime(
                    datetime.datetime(int(r[1]), int(r[2]), int(r[3]), int(r[4]), int(r[5]),
                                      int(r[6])) - datetime.timedelta(hours=int(r[7]) - 8, minutes=int(r[8])),
                    '%Y-%m-%d %H:%M:%S')
                msg = f"PID:{res['illust']['id']}\n标题:{res['illust']['title']}\n内容:{res['illust']['caption']}\n" \
                      f"作者:\n    {res['illust']['user']['name']}\n    UID:{res['illust']['user']['id']}\n" \
                      f"创建时间:{date}\n尺寸:{res['illust']['width']}x{res['illust']['height']}\n" \
                      f"标签: "
                tags = [i['name'] for i in res['illust']['tags']]
                if "R-18" in tags:
                    flag = True
                msg += ",".join(tags)
                if flag and not pixiv_config.r18:
                    return await bot.send(event=event, message=Message(
                        MessageSegment.image("https://i.niupic.com/images/2022/01/17/9TwY.jpg") + MessageSegment.text(
                            "小孩子不能看涩涩的東西！")))
                resp = await self.download(res, bot, event)
                if pixiv_config.on_temp:
                    pixivlist.insert({"pid": pid, "msg": msg, "data": resp})
                if pixiv_config.pic_msg:
                    await bot.send(event=event, message=Message(
                        [MessageSegment.image(i) for i in resp] +
                        MessageSegment.text(msg + "\n") +
                        MessageSegment.at(event.get_user_id())))
                else:
                    mid = await bot.send(event=event, message=Message(MessageSegment.reply(event.message_id)+[MessageSegment.image(i) for i in resp]))

                    pixivhistory.insert({"mid": mid['message_id'], "msg": msg, "data": resp})
            else:
                return await bot.send(event=event, message=Message(MessageSegment.text(res['error']["user_message"])))
        except Exception as e:
            logger.error(e)
            await bot.send(event=event, message=Message(MessageSegment.text("发生了奇怪的错误捏~")))

    async def send_usr_detail(self, uid: Union[str, int], bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent]):
        """
        发送p站用户信息

        :param uid: pixiv 用户id
        :param bot: BOT
        :param event: EVENT
        :return:
        """
        await self.login()
        user = (await self.api.user_detail(int(uid)))["user"]
        url=user['profile_image_urls']['medium']
        basename = os.path.basename(url)
        await self.api.download(url=url, path="pids", name=basename)
        path = Path.cwd().joinpath("pids", basename)
        detail_msg = f"ID:{user['id']}\n昵称:{user['name']}({user['account']})\n个人签名:{user['comment']}"
        await bot.send(event=event,
                       message=Message(MessageSegment.reply(event.message_id) +
                                       MessageSegment.image(f"file:///{path}") +
                                       MessageSegment.text(detail_msg)))

    async def download(self, json_result: dict, bot: Bot, event: Event):
        """
        下载图片

        :param json_result: json
        :param bot: BOT
        :param event: EVENT
        :return:
        """
        meta_pages = json_result["illust"]["meta_pages"]
        names = list()
        if meta_pages:
            await bot.send(event=event, message=Message(MessageSegment.text(f"存在{str(len(meta_pages))}个图片，正在下载...")))
            image_url: list = [ii["image_urls"]["original"] for ii in meta_pages]
        else:
            image_url: list = [json_result["illust"]["meta_single_page"]["original_image_url"]]
        for i in image_url:
            url_basename = os.path.basename(i)
            ff = await self.api.download(url=i, replace=True, path="pids", name=url_basename)
            if ff:
                png_path = f"file:///{Path.cwd().joinpath('pids', url_basename)}"
                names.append(png_path)
                logger.info(png_path)
                # messages.append(MessageSegment.image(png))
            else:
                logger.error(f"{url_basename}下载失败")
        # await bot.send(event=event, message=messages)
        return names

    async def ugoira_metadata(self, pid, bot, event):
        await self.login()
        res = await self.api.ugoira_metadata(pid)
        logger.info(res)
