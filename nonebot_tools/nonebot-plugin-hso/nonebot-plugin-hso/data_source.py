#! /usr/bin/env python3
# coding=utf-8
import asyncio
import random
import re
import time
from datetime import datetime

import httpx
from loguru import logger
from nonebot.adapters.cqhttp import MessageSegment, Message, Bot, Event
from tinydb import Query

from .config import hso_config
from .model import group_config, friend_config, Power, status, db_tmp, history

# -------------------------------------------------------
#                       Setu 类包装
# -------------------------------------------------------

Q = Query()


class Setu:
    def __init__(self, bot: Bot, event: Event, state: dict, **requests_kwargs):
        self.bot = bot
        self.event = event
        self.state = state
        self._REQUESTS_KWARGS = requests_kwargs
        # -----------------------------------
        self.config = hso_config  # 全局设置
        self.message = event.dict()
        self.type = self.message["message_type"]
        self.setu_level = 1  # 默认涩图等级
        self.current_config = None  # 当前配置
        self.power = Power()
        self.del_list = list()
        self.ess_list = list()
        self.r18 = None
        self.num = None
        self.tag = None
        self.api_set()

    def api_set(self):  # 开启api按钮
        priority = hso_config.priority
        for i in priority:
            setattr(self, f'api{i}', True)

    def update_status(self, get_num):
        date = datetime.now().strftime("%Y-%m-%d")
        if self.type == "private":
            mold = "user_id"
        elif self.type == "group":
            mold = "group_id"
        info = status.search((Q[mold] == self.message[mold]) & (Q["date"] == date))[0]
        info["num"] += get_num
        status.update(info, (Q[mold] == self.message[mold]) & (Q["date"] == date))

    def build_text(self, id = None, msg: str = None):
        if self.type == "group" and self.current_config[self.type]["at"]:
            at = True
        else:
            at = False
        text = {"id": id["message_id"], "msg": msg, "at": at}
        info = history.search(Q["msg"] == msg)
        if info:
            history.update({"id": id["message_id"]}, Q["msg"] == msg)
        else:
            history.insert(text)

    async def get_text(self, message_id):
        info = history.search(Q["id"] == message_id)[0]
        await self.send(msg=info["msg"], at=info["at"])

    @staticmethod
    def ifSent(pixiv_id, id):
        data = db_tmp.table("sentlist").search((Q["pixiv_id"] == pixiv_id) & (Q["id"] == id))
        if data:  # 如果有数据
            if time.time() - data[0]["time"] <= 36000:  # 发送过
                logger.info("id:{}发送过~".format(pixiv_id))
                return True
            else:
                db_tmp.table("sentlist").update({"time": time.time()}, (Q["pixiv_id"] == pixiv_id) & (Q["id"] == id))
                return False
        else:  # 没数据
            db_tmp.table("sentlist").insert({"pixiv_id": pixiv_id, "id": id, "time": time.time()})
            return False

    async def send(self, file: str = "", msg=None, at: bool = False):  # 发送图片或文字
        # if file[1:4] != "http" and file[1:4] != "":  # 本地文件
        #    file = "file:///" + file
        message_segment = list()
        if file:
            message_segment.append(MessageSegment.image(file=file))
        if msg:
            message_segment.append(MessageSegment.text(msg))
        if at:
            message_segment.append(MessageSegment.at(self.event.dict()["user_id"]))
        message = Message(message_segment)
        return await self.bot.send(event=self.event, message=message)

    async def withdraw(self, id=None):
        await asyncio.sleep(30)
        if id:
            return await self.bot.delete_msg(message_id=id)
        for x in self.del_list:
            await self.bot.delete_msg(message_id=x)

    @staticmethod
    async def build_msg(api="",
                        title="",
                        author="",
                        pid="",
                        uid="",
                        url="",
                        tags=None,
                        url_original=""):  # 构建消息
        if api == "lolicon" or api == "yuban":  # lolicon.app
            msg = "标题:{title}\r\n作者:{author}\r\n[www.pixiv.net/users/{author_id}]\r\n作品id:{id}\r\n" \
                  "[www.pixiv.net/artworks/{id}]\r\n原图:{url_original}\r\n".format(title=title, id=pid, url=url,
                                                                                  author_id=uid, author=author,
                                                                                  url_original=url_original)
            if tags:
                msg += "标签:{}\r\n".format(",".join(tags))
        else:
            msg = "msg配置错误,请联系管理员"
        return msg

    async def sent(self, msg, url_large=None, url_original=None):
        if self.current_config[self.type]["original"] or url_large is None:  # 是否发送原图
            id = await self.send(file=url_original)
        else:
            id = await self.send(file=url_large)
        if self.type == "group" and "R-18" not in msg:
            self.ess_list.append(id["message_id"])  # 加精表单
        self.del_list.append(id["message_id"])  # 撤回表单
        self.build_text(id, msg)  # 记录下载地址
        return id

    async def api_0(self):  # 本地图片(需要启用mongodb)
        pass

    #  这是api书写的范例
    async def api_1(self):  # https://github.com/yuban10703 请不要过多调用造成yuban的困扰
        is_send = None
        if self.api1 in vars() or self.num < 1:  # 判断是否开启
            return
        get_num = 0
        tag = ""
        url = "http://api.yuban10703.xyz:2333/setu_v4"
        if self.tag:
            tag = self.tag
        params = {"level": self.setu_level,
                  "num": self.num,
                  "tag": tag}
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, params=params, timeout=5)
                setu_data = res.json()
        except Exception as e:
            logger.warning("api1 boom~ :{}".format(e))
            await self.send(msg="涩图库一号好像坏了呢")

        else:
            if res.status_code == 200:
                for data in setu_data["data"]:
                    if self.ifSent(data["artwork"], self.event.get_user_id()):  # 判断是否发送过
                        continue
                    url_original = data["original"].replace("i.pximg.net", "i.pixiv.cat")  # 原图链接
                    url_large = data["large"].replace("i.pximg.net", "i.pixiv.cat")  # 高清链接
                    msg = await self.build_msg(api="yuban", title=data["title"], author=data["author"],
                                               uid=data["artist"], pid=data["_id"], tags=data["tags"],
                                               url_original=url_original)  # 组装消息

                    is_send = await self.sent(msg, url_original=url_original, url_large=url_large)  # 发送消息
                    get_num += 1
                    self.num -= 1
            # 打印获取到多少条
            self.update_status(get_num)  # 更新调用记录
            logger.info("从yubanのapi获取到{}张关于{}的setu  实际发送{}张".format(setu_data["count"], self.tag, get_num))
        return is_send

    async def api_2(self):  # https://api.lolicon.app/
        is_send = None
        if self.api1 in vars() or self.num < 1:  # 判断是否开启
            return
        if self.setu_level == 1:
            r18 = 0
        elif self.setu_level == 3:
            r18 = random.choice([0, 1])
        elif self.setu_level == 2:
            r18 = 1
        else:
            r18 = 0
        get_num = 0
        url = "https://api.lolicon.app/setu/v2"
        params = {"r18": r18,
                  "num": self.num,
                  "size": ["regular", "original"]}
        if self.num > 100:
            params["num"] = 100
        try:
            params["uid"] = [int(self.tag[0])]
            logger.info(params["uid"])
        except Exception as e:
            if len(self.tag) != 1 or (len(self.tag[0]) != 0 and not self.tag[0].isspace()):  # 如果tag不为空(字符串字数不为零且不为空)
                params["tag"] = self.tag
        async with httpx.AsyncClient() as client:
            res = await client.post(url, json=params, timeout=5)
            setu_data = res.json()
            if res.status_code == 200:
                for data in setu_data["data"]:
                    if self.ifSent(data["pid"], self.event.get_user_id()):  # 判断是否发送过
                        continue
                    msg = await self.build_msg(api="lolicon", title=data["title"], pid=data["pid"],
                                               author=data["author"],
                                               uid=data["uid"], tags=data["tags"],
                                               url_original=data["urls"]["original"])
                    logger.info(data["urls"])
                    is_send = await self.sent(msg, url_original=data["urls"]["original"])  # 发送消息
                    get_num += 1
                    self.num -= 1
                logger.info(
                    "从loliconのapi获取到{}张关于{}的Setu  实际发送{}张".format(len(setu_data["data"]), self.tag,
                                                                  get_num))  # 打印获取到多少条
                self.update_status(get_num)  # 更新调用记录
            else:
                await self.send(msg="涩图库二号好像坏了呢")
                logger.warning("api2:{}".format(res.status_code))

    """
    def api_2(self):  # https://yande.re/ 需要梯子且速度极其慢，不建议使用,异步用法未写
        url = "https://yande.re/post.json"
        if config["proxies"]:
            _REQUESTS_KWARGS = {
                "proxies": {
                    "https": config["proxy"],  # "http://127.0.0.1:10809"  代理
                }
            }
        else:
            _REQUESTS_KWARGS = dict()
        if len(self.tag) > 0:
            tag_switch = 1
        else:
            tag_switch = 0
        params = {"api_version": 2,
                  "tags": self.tag,
                  "limit": self.num,
                  "include_tags": tag_switch,
                  "filter": 1}
        if self.num > 10:  # api限制不能大于10
            params["num"] = 10
        try:
            res = requests.get(url, params, **_REQUESTS_KWARGS)
            setu_data = res.json()
        except Exception as e:
            logger.error("api0 boom~")
            logger.error(e)
        else:
            if res.status_code == 200:
                for data in setu_data["posts"]:
                    id = data["id"]
                    file_url = data["file_url"]
                    if self.if_sent(id):  # 判断是否发送过
                        continue
                    url_original = data["source"]
                    msg = self.build_msg(level="api0", title=data["tags"], author=data["author"],
                                         url_original=url_original)
                    with requests.get(file_url, **_REQUESTS_KWARGS) as resp:
                        with open("./tmp.jpg", "wb") as fd:
                            fd.write(resp.content)
                    sendMsg.send_pic(self.ctx, msg, picPath="./tmp.jpg")
                    self.api_0_realnum += 1
                # else:
                #     logger.warning("api0:{}".format(res.status_code))
            logger.info(
                "从yandeのapi获取到{}张setu  实际发送{}张".format(len(setu_data["posts"]), self.api_0_realnum))  # 打印获取到多少条
    """

    async def processing_and_inspect(self):  # 处理消息+调用
        # -----------------------------------------------
        if self.num == "一" or self.num == "":
            self.num = 1
        elif self.num == "二" or self.num == "俩" or self.num == "两":
            self.num = 2
        elif self.num == "三":
            self.num = 3
        elif self.num != "":
            # 如果指定了数量
            try:
                self.num = int(self.num)
            except ValueError:  # 出错就说明不是数字
                await self.send(msg="不会真的有人连数学数字都不会输入吧！")
                return
            if self.num <= 0:  # ?????
                await self.send(msg="你想笑死我好继承我的负产吗¿¿¿")
                return
        else:  # 未指定默认1
            self.num = 1
        # -----------------------------------------------
        if not self.current_config[self.type]["setu"]:  # setu开关判断
            return await self.send(msg="啊嘞啊嘞，涩图还没开呢~")
        if self.num > self.current_config[self.type]["max_num"]:  # 最大数量判断
            return await self.send(msg="要这么多涩图你怎么不冲死呢¿")
        if self.r18:
            self.setu_level = self.current_config[self.type]["setu_level"]  # r18判断
            if self.setu_level < 2:
                await self.send(msg="太涩了，你不能看哼~")
                return
        if self.type == "private":  # 优先级
            if self.r18:
                self.setu_level = 2
            logger.info(self.current_config)
            if self.current_config[self.type]["setu_level"] is dir():
                self.setu_level = self.current_config[self.type]["setu_level"]
            date = datetime.now().strftime("%Y-%m-%d")
            info = status.search((Q["user_id"] == self.message["user_id"]) & (Q["date"] == date))
            if info:
                info = info[0]
                info["num"] += self.num
                status.update(info, (Q["user_id"] == self.message["user_id"]) & (Q["date"] == date))
            else:
                info = {
                    "user_id": self.message["user_id"],
                    "num": 0,
                    "date": date
                }
                status.insert(info)
        elif self.type in ["group", "temp"]:
            date = datetime.now().strftime("%Y-%m-%d")
            if self.type == "group":  # 统计调用数量
                info = status.search((Q["group_id"] == self.message["group_id"]) & (Q["date"] == date))
                if info:
                    info = info[0]
                else:
                    info = {
                        "group_id": self.message["group_id"],
                        "num": 0,
                        "date": date
                    }
                    status.insert(info)
                    info = status.search((Q["group_id"] == self.message["group_id"]) & (Q["date"] == date))[0]
                now_num = info["num"] + self.num
                if self.current_config["group"]["top"] >= now_num:  # 上限判断
                    self.call = await self.send(
                        msg="当天已调用：{}\r\n群剩余调用：{}".format(str(now_num),
                                                          str(self.current_config["group"]["top"] - now_num)))
                elif self.current_config["group"]["top"] == 0:
                    pass
                else:
                    self.call = await self.send(msg=f"当天已调用：{str(info['num'])}\r\n再调用{str(self.num)}超过上限了呢~")
        await self.action()

    async def main(self):  # 判断消息类型给对应函数处理
        self.r18 = self.state["_matched_groups"][2]
        self.num = self.state["_matched_groups"][0]
        self.tag: list = [i for i in list(set(re.split(r",|，|\.|-| |_|/|\\", self.state["_matched_groups"][1]))) if
                          i != ""]  # 分割tag+去重+去除空元素
        if self.type != "private":  # 群聊or临时会话
            data = group_config.search(Q["group_id"] == self.message["group_id"])[0]  # 数据库
            if data:  # 查询group数据库数据
                self.current_config = data
            else:
                await self.power.group_build(self.message["group_id"])
                self.current_config = group_config.search(Q["group_id"] == self.message["group_id"])[0]
            await self.processing_and_inspect()
        else:  # 好友会话
            if hso_config.friend:
                pass
            else:
                return await self.send(msg="全局设置中好友调用未开启")
            data = friend_config.search(Q[self.type]["user_id"] == self.message["user_id"])
            if data:  # 该QQ如果自定义过
                self.current_config = data[0]
            else:
                data = {"private": {
                    "user_id": self.message["user_id"],
                    "setu_level": 2,
                    "original": False,
                    "setu": True,
                    "r18": True,
                    "max_num": 3}}
                self.current_config = data
                friend_config.insert(data)
                logger.info(f"无用户{self.message['user_id']}数据，创建成功~")
                # 如果没有自定义 就是默认行为
                await self.processing_and_inspect()

    async def set_essence_msg(self, message_id):  # 添加精华消息
        await self.bot.call_api('set_essence_msg', message_id=message_id)

    async def action(self):  # 判断数量

        for i in self.config.priority:
            if getattr(self, f"api{i}"):
                t = eval(f"self.api_{i}")
                await t()
        if self.type == "group":
            if self.current_config["group"]["essence"]:
                for i in self.ess_list:
                    await self.set_essence_msg(i)
            if self.current_config["group"]["top"] != 0:
                await self.withdraw(id=self.call["message_id"])
            if self.current_config[self.type]["revoke"]:  # 撤回
                await self.withdraw()
        if self.num != 0:
            await self.send(msg="淦！你的xp好奇怪啊！")
            return
        return
