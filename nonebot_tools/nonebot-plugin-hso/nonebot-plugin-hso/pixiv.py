from loguru import logger
from pixivpy_async import *
from .config import hso_config


class Pixiv:
    def __init__(self):
        self.proxy = False
        self.api = None
        self.default()

    def default(self):
        if not hso_config.pixiv:  # 开关
            logger.error("请在配置文件中开启pixiv功能")
            return
        if hso_config.refresh_token == "":  # token
            logger.error("请在配置文件中输入refresh_token值，帮助详见:")
            return
        else:
            token = hso_config.refresh_token
        if hso_config.pixiv_proxy:
            self.api = AppPixivAPI()
        else:
            self.api = PixivAPI()
        try:
            self.api.login(refresh_token=token)
            logger.success("登录成功")
        except:
            logger.error("登录失败")
            logger.error("请检查配置文件中refresh_token值，帮助详见:")

    async def get_illust_detail(self, id):  # 获取图片信息
        pass
