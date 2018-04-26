# PyFly

#### 项目介绍
Flask + Layui Fly Template实现的一个社区项目，使用flask-admin实现了简单的后台管理功能，数据库使用Ｍongodb，前台实现功能：用户注册、登录、邮件激活、发帖、回帖、点赞、回复、采纳、删帖、结贴等功能

#### 软件架构
1.前端模板：[Layui Fly Template](http://www.layui.com/template/fly/)

2.Flask + flask-pymongo + flask-admin + flask-login + flask-mail



#### 安装教程

```
git clone https://gitee.com/981764793/PyFly

安装MongoDB
修改mongodb连接信息，STMP邮箱账号密码（用户注册验证用到）


pip install -r requirements.txt

python manager.py
```

#### 使用说明

1. 首次打开会自动往MongoDB新增一些默认数据（管理员账号和默认配置项），后台管理（flask-admin简单实现）: http://127.0.0.1:5000/admin

2. 可自己修改扩展模板作为信息分类网站或者简单的cms、博客

3.19应届小菜鸟初学Python的作品，都做得比较粗糙，希望各位大佬指正，另外如果能有个实习岗位就更好了，邮箱：981764793@qq.com

4.图片上传可选保存到后端或图床，默认保存到服务器，如果要开启图床上传在/static/js/mods/index.js搜索开启图床注释和解开相应注释后即可，然后在user.js进行相应操作，图床使用了[SM.MS图床](http://sm.ms)

####模板开发

1.全局过滤器mongo_date_str（格式化mongodb的日期字段）

2.全局函数：

    1）get_page(collection_name, pn=1, size=10, sort_by=None, filter1=None) 分页查询 pn页码 sort_by为tuple类型，目前只支持单字段排序，详情可看模板
    2）get_list(collection_name, sort_by=None, filter1=None, size=None) 列表查询
    3）find_one(collection_name, filter1=None) 获取单条
    4）date_cal(d1, num, is_add=True) 计算日期


####Todo

1.社交账号登录

2.暂时没想到。。。

#### 截图预览

![首页1](https://gitee.com/uploads/images/2018/0426/180217_6c36771c_750007.png "QQ截图20180426175656.png")

![首页2](https://gitee.com/uploads/images/2018/0426/180231_079d2ac1_750007.png "QQ截图20180426175715.png")

![发帖](https://gitee.com/uploads/images/2018/0426/180246_dd80896b_750007.png "QQ截图20180426175740.png")

![回帖](https://gitee.com/uploads/images/2018/0426/180259_11602e95_750007.png "QQ截图20180426175828.png")

![个人设置](https://gitee.com/uploads/images/2018/0426/180310_de7a3005_750007.png "QQ截图20180426175906.png")

![用户主页](https://gitee.com/uploads/images/2018/0426/180325_60301b7a_750007.png "QQ截图20180426175922.png")