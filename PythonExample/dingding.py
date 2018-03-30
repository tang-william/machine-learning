# -*- coding: UTF-8 -*-

#author:wendaoyu
#date=2018/2/8

from dingtalkchatbot.chatbot import DingtalkChatbot
from datetime import datetime


def transpond_link_to_dingding(title,info,message_url):
        # Webhook地址
        webhook = 'https://oapi.dingtalk.com/robot/send?access_token=7398bd6b0ec02211bb818c92836c8aa3bd7442de56bad7a029c4245aa41bf79b'
        # 初始化机器人Eva
        Eva = DingtalkChatbot(webhook)
        # 消息@列表
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = '''#### %s\n
                > 详情: %s\n
                > 详情链接: %s\n
                > ###### 报警时间:%s\n''' % (title, info, message_url, current_time)
        #       at_mobiles = [15313900930]
        #       Eva.send_markdown(title=title,text=text,at_mobiles=at_mobiles)

        Eva.send_markdown(title='氧气文字', text='#### 广州天气\n'
                                             '> 9度，西北风1级，空气良89，相对温度73%\n\n'
                                             '> ![美景](http://www.sinaimg.cn/dy/slidenews/5_img/2013_28/453_28488_469248.jpg)\n'
                                             '> ###### 10点20分发布 [天气](http://www.thinkpage.cn/) \n',
                          is_at_all=True);


transpond_link_to_dingding("","","")


# # WebHook 地址
# webhook = 'https://oapi.dingtalk.com/robot/send?access_token=7398bd6b0ec02211bb818c92836c8aa3bd7442de56bad7a029c4245aa41bf79b'
# shaosiming = DingtalkChatbot(webhook)
#
# text='#### 广州天气\n' '> 9度，西北风1级，空气良89，相对温度73%\n\n' '> ![美景](http://www.sinaimg.cn/dy/slidenews/5_img/2013_28/453_28488_469248.jpg)\n' '> ###### 10点20分发布 [天气](http://www.thinkpage.cn/) \n'
# print type(text)
# print text
# shaosiming.send_markdown(title='氧气文字',text='#### 广州天气\n'
#       '> 9度，西北风1级，空气良89，相对温度73%\n\n'
#                            '> ![美景](http://www.sinaimg.cn/dy/slidenews/5_img/2013_28/453_28488_469248.jpg)\n'
#                            '> ###### 10点20分发布 [天气](http://www.thinkpage.cn/) \n',
#                            is_at_all=True);