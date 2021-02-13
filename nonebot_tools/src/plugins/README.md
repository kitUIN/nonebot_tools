# nonebot_ncm
基于go-cqhttp与nonebot2的网易无损音乐下载
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
```
网易云单曲分享到群内会自动解析下载  
第一次请使用`/开启 ncm` 启动解析  
或者分享一个单曲启动  
### 命令列表：(命令开始符号可自行调换)  
|  命令   | 备注  |
|  ----  | ----  |
| /开启 ncm  | 开启解析 |
| /关闭 ncm  | 关闭解析 |
| /下载 <id>  | 下载解析出id的歌曲 |

