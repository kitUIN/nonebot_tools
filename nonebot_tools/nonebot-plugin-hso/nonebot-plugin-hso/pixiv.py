import os

from loguru import logger
from pixivpy_async import *
from .model import hso_config, Power


class Pixiv:
    def __init__(self):
        self.proxy = False
        if not hso_config.pixiv:  # 开关
            logger.error("请在配置文件中开启pixiv功能")
            return
        if hso_config.refresh_token == "":  # token
            logger.error("请在配置文件中输入refresh_token值，帮助详见:https://www.kituin.cf/wiki/hso_bot/hso#refresh_token")
            return
        else:
            self.token = hso_config.refresh_token
        if hso_config.pixiv_proxy:
            self.api = AppPixivAPI(proxy="http://127.0.0.1:10809")
        else:
            self.api = PixivAPI(proxy="http://127.0.0.1:10809")

    async def login(self):
        try:
            await self.api.login(refresh_token=self.token)
            logger.success("登录成功")
        except:
            logger.error("登录失败")
            logger.error("请检查配置文件中refresh_token值，帮助详见:https://www.kituin.cf/wiki/hso_bot/hso#refresh_token")

    async def get_illust_detail(self, pid):  # 获取图片信息
        await self.login()
        pic = list()
        msg = ""
        try:
            res = await self.api.illust_detail(pid)
            msg = f"PIXIV_ID:{res['illust']['id']}\r\n标题:{res['illust']['title']}\r\n内容:{res['illust']['caption']}\r\n作者:\r\n    {res['illust']['user']['name']}\r\n    UID:{res['illust']['user']['id']}\r\n创建时间:{res['illust']['create_date']}\r\n尺寸:{res['illust']['width']}X{res['illust']['height']}\r\n标签:"
            for i in res['illust']['tags']:
                msg += i['name'] + "\r\n"
            if res['illust']['page_count'] > 1:
                for j in range(res['illust']['page_count']):
                    pic.append(f"https://pixiv.cat/{res['illust']['id']}_{j}.jpg")
            else:
                pic.append(f"https://pixiv.cat/{res['illust']['id']}.jpg")
        except Exception as e:
            logger.error(e)
        return [msg, pic]

    async def get_usr_detail(self, uid):
        await self.login()
        user = (await self.api.user_detail(uid))["user"]
        user_illusts = (await self.api.user_illusts(uid))["illusts"]
        name = "thubil"
        path = os.path.join(os.path.curdir, name)
        await self.api.download(url=user['profile_image_urls']['medium'], name=name)
        illusts_count = len(user_illusts)
        illusts_ids = [i['id'] for i in user_illusts]
        detail_msg = f"ID:{user['id']}\r\n昵称:{user['name']}({user['account']})\r\n个人签名:{user['comment']}\r\n作品(共{illusts_count}):{illusts_ids}\r\n查看作品请使用#pid <id> "
        return [detail_msg, path, illusts_count,illusts_ids]


