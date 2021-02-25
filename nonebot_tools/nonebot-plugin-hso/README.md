# hso
基于go-cqhttp nonebot2的setu 插件
# TODO
- [X] 发送setu(无需命令符)(默认关闭)
  - 正则匹配`来(.*?)[点丶份张幅](.*?)的?(|r18)[色瑟涩🐍][图圖🤮]`
- setu api:
  - [x] lolicon.app
- [X] 自动撤回(群默认开启，好友会话关闭，默认20s)
- [x] 群独立配置
- [ ] 统计
- [x] 回复消息获取图片详细信息
  - 为了规避长文本消息引发风控，bot只会发图片，如果要知道详细可以回复图片消息
  - 该功能需要在`.env` 文件中将BOT QQ号码放入`bot`
### 命令列表：(命令开始符号可自行调换)  
|  命令   | 备注  |
|  ----  | ----  |
| /hso setu t/f  | 开启/关闭setu功能 |
| /hso r18 t/f  | 开启/关闭 r18|
| /hso original t/f | 开启/关闭原图 |
| /hso revoke t/f | 开启/关闭setu撤回 |
| /hso essence t/f | 开启/关闭自动加精(需要管理员) |
| /hso setu_level < int > | 修改setu等级 默认等级 0:正常 1:性感 2:色情 3:All |
| /hso max_num < int > | 修改一次最多数量 |
| /hso top < int > | 修改色图最大上限(0为无限) |


# 配置文件
```
superusers=[] #加入bot  qq号以启用回复功能
api1=True # 色图库是否开启 api1=lolicon
PRIORITY=[1]  #　色图库(元组)优先级:api0 > api1  如果是[1,0]即为api1 > api0
LOLICON_KEY=none  # lolicon.app 的Key，前往https://api.lolicon.app申请
Friend=True  #好友色图调用开关
bot= # 机器人QQ

```
## 自行添加色图库
1.在`data_source.py`<sup>[直达](https://github.com/kitUIN/nonebot_tools/blob/master/nonebot_tools/nonebot-plugin-hso/nonebot-plugin-hso/data_source.py) </sup>添加你自己的api，可以仿照代码中的api_0()进行编写  
  
假设你添加了`api_2`
  
2.完成后在`配置文件`中添加您的`api_2`
```#添加下列数据
api2=True # （这里不需要加_）色图库是否开启 api2=你新加的
PRIORITY=[1，2]  #　色图库(元组)优先级:api1 > api2
```
3.`config.py`<sup>[直达](https://github.com/kitUIN/nonebot_tools/blob/master/nonebot_tools/nonebot-plugin-hso/nonebot-plugin-hso/config.py) </sup>中在Config类中添加你`api_2`开关
```python

from pydantic import BaseSettings

class Config(BaseSettings):
    # 全局
    api2 = True  # 添加这一行就行
```
4.重启bot即可
# 鸣谢
[SetuBot](https://github.com/yuban10703/OPQ-SetuBot)  
