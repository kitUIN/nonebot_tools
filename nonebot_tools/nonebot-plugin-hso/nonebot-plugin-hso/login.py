#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# thanks to https://github.com/txperl/PixivBiu
#  help http://biu.tls.moe/#/lib/dl?id=%e9%97%ae%e9%a2%98%e8%af%b4%e6%98%8e
import re
from pathlib import Path
import requests
from base64 import urlsafe_b64encode
from hashlib import sha256
from secrets import token_urlsafe
from urllib.parse import urlencode

from loguru import logger
from requests_toolbelt.adapters import host_header_ssl

USER_AGENT = "PixivAndroidApp/5.0.234 (Android 11; Pixel 5)"
REDIRECT_URI = "https://app-api.pixiv.net/web/v1/users/auth/pixiv/callback"
LOGIN_URL = "https://app-api.pixiv.net/web/v1/login"
AUTH_TOKEN_URL_HOST = "https://oauth.secure.pixiv.net"
CLIENT_ID = "MOBrBDS8blbauoSck0ZfDbtuzpyT"
CLIENT_SECRET = "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj"


class Login:
    def __init__(self):
        session = requests.Session()
        session.mount('https://', host_header_ssl.HostHeaderSSLAdapter())
        self.requests = session
        self.code_verifier, self.code_challenge = self.oauth_pkce(self.s256)
        self.login_params = {
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
            "client": "pixiv-android",
        }
        self.path = self.path()

    @staticmethod
    def path():
        paths = [".env"]
        path = Path.cwd()
        while not path.joinpath(*paths).exists():
            path = path.parent
        return path

    def s256(self, data):
        """S256 transformation method."""

        return urlsafe_b64encode(sha256(data).digest()).rstrip(b"=").decode("ascii")

    def oauth_pkce(self, transform):
        """Proof Key for Code Exchange by OAuth Public Clients (RFC7636)."""

        code_verifier = token_urlsafe(32)
        code_challenge = transform(code_verifier.encode("ascii"))

        return code_verifier, code_challenge

    def login(self, host=AUTH_TOKEN_URL_HOST, kw={}):
        """
        尝试通过 Code 获取 Refresh Token。
        :param host: token api 的主机域
        :param kw: requests 请求的额外参数
        """
        proxy = input("若无请直接回车，若有代理，请输入代理地址(http开头)： ").strip()
        if proxy:
            kw = {
                'https': proxy
            }
        logger.info(
            "\r\n[Login] 请按以下步骤进行操作:"
            f"\r\n1. 访问「{LOGIN_URL}?{urlencode(self.login_params)}」"
            "\r\n（若您别无他法，还是不能访问以上网址，那可参考此方式「https://github.com/mashirozx/Pixiv-Nginx」先进行配置）"
            "\r\n2. 打开浏览器的「开发者工具 / Dev Console / F12」，切换至「Network」标签"
            "\r\n3. 开启「Preserve log / 持续记录」"
            "\r\n4. 在「Filter / 筛选」文本框中输入「callback?」"
            "\r\n5. 登录您的 Pixiv 账号"
            "\r\n6. 成功登录后，会出现一个类似「https://app-api.pixiv.net/.../callback?state=...&code=...」的字段，"
            "\r\n将「code」后面的参数输入本程序"
        )
        code = input("Code: ").strip()

        response = self.requests.post(
            "%s/auth/token" % host,
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "code_verifier": self.code_verifier,
                "grant_type": "authorization_code",
                "include_policy": "true",
                "redirect_uri": REDIRECT_URI,
            },
            headers={"User-Agent": USER_AGENT, "host": "oauth.secure.pixiv.net"},
            **kw
        )
        rst = response.json()

        if "refresh_token" in rst:
            logger.success('您的token为:' + rst["refresh_token"])
            with open(self.path.joinpath(*['.env']), 'r+', encoding='utf-8') as f:  # 搜索env配置
                x = f.readlines()
                for i in x:  # 查找文件中的refresh_token
                    environment = re.search('^ENVIRONMENT=(.*)(|\\n)$', i)
                    if environment:
                        env = ['.env.' + environment[1]]
                        break
            with open(self.path.joinpath(*env), 'r+', encoding='utf-8') as f:
                x = f.readlines()
                for i in x:  # 查找文件中的refresh_token
                    refresh_token = re.search('^REFRESH_TOKEN=(.*)$', i)
                    if refresh_token:
                        break
                if refresh_token:  # 找到后进行替换
                    x[x.index(i)] = f'REFRESH_TOKEN={rst["refresh_token"]}\n'
                    logger.success(f'\r\n已为您在{env[0]}文件中替换:\r\nREFRESH_TOKEN={refresh_token[1]}'
                                   f'--->REFRESH_TOKEN={rst["refresh_token"]}')
                else:  # 没有就创建
                    x.append(f'\nREFRESH_TOKEN={rst["refresh_token"]}\n')
                    logger.success(f'\r\n已为您在{env[0]}文件中创建:\r\nREFRESH_TOKEN={rst["refresh_token"]}')
                f.seek(0)
                f.writelines(x)
        else:
            logger.error(Exception("Request Error.\nResponse: " + str(rst)))


if __name__ == '__main__':
    Login().login()
