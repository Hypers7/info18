from flask import Flask
# 集成sqlalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 集成状态保持的扩展
from flask_session import Session
# 导入配置文件
from config import config_dict

    # 创建sqlalchemy实例对象
    # db = SQLAlchemy()


# 定义函数 封装程序初始化的操作
# 工厂函数 用来生产程序实例app
# 让启动文件manage来调用函数 实现动态的传入不同的配置信息,获取不同配置信息下的app
def create_app(config):

    app = Flask(__name__)

    # 使用配置信息
    app.config.from_object(config_dict[config])

    # 创建sqlalchemy实例对象
    db = SQLAlchemy(app)
    # db.init_app(app)

    # 实例化session
    Session(app)

    return app, db


