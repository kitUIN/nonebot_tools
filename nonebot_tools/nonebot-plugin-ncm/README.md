# nonebot-plugin-ncm
基于[go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 与[nonebot2](https://github.com/nonebot/nonebot2) 的网易无损音乐下载
## 开始
`pip install nonebot-plugin-ncm`
进行安装  
在`bot.py`添加`nonebot.load_plugin('nonebot-plugin-ncm')`
## 使用说明
`.env`配置文件中需要添加拥有**VIP的网易云账号**  
本程序实质为调用web接口下载音乐上传  
```
phone= #手机登录
password= #密码
bot= #机器人QQ号
```
网易云单曲分享到群内会自动解析下载  
第一次请使用`/ncm t` 启动解析  
或者分享一个单曲启动  
**回复bot消息即可自动上传音乐文件**
## 功能列表
- [x] 识别网易云单曲
    - 链接
    - 卡片
    - 卡片转发
- [ ] 识别网易云歌单    

### 命令列表：(命令开始符号可自行调换)  
|  命令   | 备注  |
|  ----  | ----  |
| /ncm t  | 开启解析 |
| /ncm f  | 关闭解析 |
# 鸣谢
- [pyncm](https://github.com/greats3an/pyncm)
