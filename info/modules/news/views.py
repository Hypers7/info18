# 导入模板对象, 导入上下文对象current_app
from flask import render_template, current_app, jsonify
# 导入蓝图对象 使用蓝图创建路由映射
from . import news_blue
from flask import session
from info.models import User, News, Category
from info import constants
from info.utils.response_code import RET


@news_blue.route('/')
def index():
    # 加载模板文件
    """
    首页
    实现页面右上角 检查用户登录状态 如果用户登录 显示用户信息 如果未登录提供登录注册入口
    1 从redis中获取用户id
    2 根据user id查询mysql获取用户信息
    3 把用户信息 传给模板

    新闻点击排行展示
    根据新闻的点击次数查询数据库 使用模板渲染数据

    新闻分类展示
    查询所有新闻分类 使用模板渲染数据
    :return:
    """
    user_id = session.get('user_id')
    user = None
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
    #     return 后不登录无法访问首页
    # 新闻点击排行
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询新闻排行数据失败')
    if not news_list:
        return jsonify(errno=RET.NODATA, errmsg='无新闻排行数据')
    news_click_list = []
    for news in news_list:
        news_click_list.append(news.to_dict())

    # 新闻分类展示
    try:
        categories = Category.query().all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询新闻分类数据失败')

    if not categories:
        return jsonify(errno=RET.NODATA, errmsg='无新闻分类数据')
    # 定义容器 存储新闻分类数据
    category_list = []
    # 遍历查询结果
    for category in categories:
        category_list.append(category.to_dict())

    # 定义字典 用来返回数据
    data = {
        'user_info': user.to_dict() if user else None,
        'news_click_list': news_click_list
        'category_list': category_list
    }
    style = {
        'style': "display: block"
    }
    return render_template('news/index.html', data=data, style=style)


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