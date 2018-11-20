# 导入模板对象, 导入上下文对象current_app
from flask import render_template, current_app, jsonify, request
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
    if user_id:
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
        categories = Category.query.all()
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
        'news_click_list': news_click_list,
        'category_list': category_list
    }
    style = {
        'style': "display: block"
    }
    return render_template('news/index.html', data=data, style=style)


@news_blue.route('/news_list')
def news_list():
    """
    首页新闻列表
    获取参数 检查参数 业务处理 返回接果
    1 获取参数 get请求 cid page per_page
    2 检查参数 转换参数的数据类型
    cid,page,per_page= into(cid),int(page),int(per_page)
    3 根据分类id查询新闻列表 新闻列表默认安装新闻发布时间倒序排序
    判断用户选择的新闻分类
    if cid > 1:
        News.query.filter(News.category_id == cid).order_by(News.create_time.desc().paginate(page, per_page, false)
    else:
        News.query.filter().order_by(News.create_time.desc().paginate(page, per_page, false)
     filters = []
    if cid > 1:
        filters.append(News.category_id == cid)
    paginate = News.query.filter(*filters).order_by(News.create_time.desc().paginate(page, per_page, false)
    获取分页后的数据
    paginate.items
    paginate.pages
    paginate.page
    遍历分页后的数据数据 调用模型类中的方法 转成字典
    返回结果
    :return:
    """
    cid = request.args.get('cid', '1')
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')
    try:
        cid, page, per_page = int(cid), int(page), int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数格式错误')
    filters = []
    if cid > 1:
        filters.append(News.category_id == cid)
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询新闻列表失败')
    # 使用分页对象 获取分页后的数据,总数据,总页数,当前页数
    news_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page
    news_dict_list = []
    # 遍历分页数据 转成字典
    for news in news_list:
        news_dict_list.append(news.to_dict())
    # 定义容器
    data = {
        'total_page': total_page,
        'current_page': current_page,
        'news_dict_list': news_dict_list
    }

    # 返回数据
    return jsonify(errno=RET.OK, errmsg='ok', data=data)







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