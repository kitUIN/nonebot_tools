

<p align="center">
  <img src="https://i.niupic.com/images/2022/01/17/9TxD.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# nonebot-plugin-ncm

✨ 基于go-cqhttp与nonebot2的 网易云 无损音乐下载 ✨
</div>

<p align="center">
  <a href="https://github.com/kitUIN/nonebot_tools/blob/master/nonebot-plugin-ncm/nonebot-plugin-ncm/LICENSE">
    <img src="https://img.shields.io/badge/license-Apache--2.0-green" alt="license">
  </a>
  <a>
    <img src="https://img.shields.io/static/v1?label=nonebot2&message=v2.0.0-beta.1&color=brightgreen" alt="nonebot">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-ncm">
    <img src="https://img.shields.io/badge/release-v1.2.2-blue" alt="pypi">
  </a>
</p>


## 开始
1.`pip install nonebot-plugin-ncm` 进行安装(v1.2.2)  
2.并在`bot.py`添加`nonebot.load_plugin('nonebot-plugin-ncm')`(如果是通过`nb-cli`安装可以跳过这步(beta1以上版本))  
如果希望使用nonebot2 a16及以下版本  
请使用`pip install nonebot-plugin-ncm==1.1.0`进行安装  

## 使用说明
`.env`配置文件中需要添加拥有**VIP的网易云账号**  
本程序实质为调用web接口下载音乐上传  
默认下载最高音质的音乐  
```
ncm_admin=["owner", "admin"] # 设置命令权限（非解析下载，仅解析功能开关设置）
ncm_phone= #手机登录
ncm_password= #密码
ncm_song=True  # 单曲解析开关
ncm_list=True  # 歌单解析开关
ncm_priority=2  # 解析优先级(ncm插件解析的优先级,1最高)
white_list=[]  # 白名单一键导入
```
网易云单曲分享到群内会自动解析下载  
**仅限群聊使用！！！(因为go-cqhttp还不支持好友发文件)**  
  
~~nonebot-adapter-cqhttp 2.0.0a14版本存在bug,请回滚到2.0.0a13版本使用！！！~~  
~~pip install nonebot-adapter-cqhttp==2.0.0a13~~  
**目前使用最新版即可**  
  
**默认不开启解析功能**  
**请使用`/ncm t` 启动解析**  
(或者使用配置中的`white_list`项批量导入需要开启的群号)

**回复bot消息即可自动下载上传音乐文件(回复消息不输入内容也行)**  

**低版本升级至1.0.0版本请删掉db文件夹**  
## 功能列表
- [x] 识别网易云单曲
    - 链接
    - 卡片
    - 卡片转发
- [x] 识别网易云歌单    
    - 链接
    - 卡片
    - 卡片转发

### 命令列表：(命令开始符号可自行调换)  
|  命令   | 备注  |
|  ----  | ----  |
| /ncm  | 获取命令菜单 |
| /ncm t  | 开启解析 |
| /ncm f  | 关闭解析 |
### 示例图
<details>
  <summary>点击查看详细内容</summary>

  **单曲**  
  [![WqbK7d.png](https://z3.ax1x.com/2021/07/30/WqbK7d.png)](https://imgtu.com/i/WqbK7d)
  **歌单**  
  [![WqbQAA.png](https://z3.ax1x.com/2021/07/30/WqbQAA.png)](https://imgtu.com/i/WqbQAA)  
  
</details>

# 鸣谢
- [pyncm](https://github.com/greats3an/pyncm)
- [nonebot2](https://github.com/nonebot/nonebot2)