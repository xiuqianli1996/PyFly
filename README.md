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

1. 首次打开会自动往MongoDB新增一些默认数据（管理员账号和默认配置项）
2. 可自己修改扩展模板作为信息分类网站或者简单的cms、博客
3.19应届小菜鸟初学Python的作品，希望各位大佬指正，另外如果能有个实习岗位就更好了，邮箱：981764793@qq.com
