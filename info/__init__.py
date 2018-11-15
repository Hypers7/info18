from flask import Flask

# 集成sqlalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 集成状态保持的扩展
from flask_session import Session
# 导入配置文件
#  导入配置信息
from config import config_dict, Config
# 集成Python中的标准日志模块
import logging
from logging.handlers import RotatingFileHandler
# 导入redis
from redis import StrictRedis


# 实例化redis对象
redis_store = StrictRedis(Config.HOST, Config.PORT)


# 创建sqlalchemy实例对象
db = SQLAlchemy()


# log
# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)


# 定义函数 封装程序初始化的操作
# 工厂函数 用来生产程序实例app
# 让启动文件manage来调用函数 实现动态的传入不同的配置信息,获取不同配置信息下的app
def create_app(config):

    app = Flask(__name__)

    # 使用配置信息
    app.config.from_object(config_dict[config])

    # 创建sqlalchemy实例对象
    # db = SQLAlchemy(app)
    db.init_app(app)

    # 实例化session
    Session(app)

    # 导入蓝图,注册蓝图
    from info.modules.news import news_blue
    app.register_blueprint(news_blue)
    # 注册蓝图 表单
    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)

    return app


