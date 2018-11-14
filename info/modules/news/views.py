# 导入模板对象
from flask import render_template, current_app
# 导入蓝图对象 使用蓝图创建路由映射
from . import news_blue


@news_blue.route('/')
def index():
    # 加载模板文件
    return render_template('news/index.html')


# 加载logo图标:浏览器会默认请求 url地址:http://127.0.0.1:5000/favicon.ico
# favicon文件路径 :http://127.0.0.1:5000/static/news/favicon.ico
# 原因:
# 1 浏览器不是每次请求都会使用缓存
# 2 清空缓存
# 3 彻底退出浏览器
@news_blue.route('/favicon.ico')
def favicon():
    # 把favicon图标传给浏览器,发送静态文件给浏览器
    return current_app.send_static_file('news/favicon.ico')