# 2020.01.18: 代码整理中, 稍后commit 


# 注意：
> # ~~i.  此版本代码已经年久失修~~
> # ~~ii. 功能已经不能保证~~
> # ~~iii.  仅供参考学习交流使用~~
>  ~~另外，程序目前来看应该是已经失效，有需求的可以自己按照这个流程重新抓包获取通信协议，更新自习室和座位表，修改代码模拟抢座。~~
> # 正在重启工程 igotolibrary ...

------

# igotolibrary-抢座助手
![language](https://img.shields.io/badge/language-python3.x-green.svg) 
![license](https://img.shields.io/badge/LICENSE-MIT-brightgreen.svg)
## 简介
一个简单的 Python 爬虫，通过 *Charles* 抓包分析公众号《**我去图书馆**》、《**来选座**》的服务通信协议，获取自习室和座位表信息，使用```Python```+```requests```库模拟预定座位的流程，实现定时/实时自动抢座。

------
## 运行方式
* 1. 先抓包获取sessionid;
* 2. 填入配置文件,
    > 格式为:
    > ```
    > [user1]=[sessionid],[第几自习室]，[几号座位]，[第几自习室]，[几号座位]  ...
    > ```
    > 比如:
    > ```
    > user1 = 29ijfnxxxxxxxxxxxxx24dbsl6,1,80,2,81 
    > ```
    > 代表你想抢的座位是第一自习室80号座位，备选座位是第二自习室81号座位;
  
* 填写完成保存退出，然后当前目录启动```cmd```，输入
    > ```shell
    > python RSmain.py 
    > ```
  即可运行。
 
 
------
## 部署demo
我已将工程部署到了微信 《**为了学习**》公众号，欢迎测试，服务启动中...

> ![mahua](https://github.com/RenjiaLu9527/igotolibrary/blob/master/qrcode.png)



> # 有问题可留言或联系管理员



    
