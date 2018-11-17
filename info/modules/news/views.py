# 导入模板对象, 导入上下文对象current_app
from flask import render_template, current_app
# 导入蓝图对象 使用蓝图创建路由映射
from . import news_blue
from flask import session
from info.models import User


@news_blue.route('/')
def index():
    # 加载模板文件
    """
    首页
    实现页面右上角 检查用户登录状态 如果用户登录 显示用户信息 如果未登录提供登录注册入口
    1 从redis中获取用户id
    2 根据user id查询mysql获取用户信息
    3 把用户信息 传给模板

    :return:
    """
    user_id = session.get('user_id')
    user = None
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
    #     return 后不登录无法访问首页

    # 定义字典 用来返回数据
    data = {
        'user_info': user.to_dict() if user else None
    }
    return render_template('news/index.html', data=data)


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