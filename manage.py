from flask import Flask, session
# 集成管理器脚本
from flask_script import Manager
# 集成sqlalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 数据迁移的扩展
from flask_migrate import Migrate, MigrateCommand
# 集成状态保持的扩展
from flask_session import Session
# 导入redis模块
from redis import StrictRedis

app = Flask(__name__)
# 配置秘钥
app.config['SECRET_KEY'] = '7nqfG7KXkkmg9e3gifTAuQNtXTQlIlYwlRuIibGlXyLjTYNW7MBtWA=='
# mysql配置信息
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql@localhost/python_1'
# 动态追踪修改
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# 实现状态保持, 配置session信息存储在redis中
app.config['SESSION_TYPE'] = 'redis'
# 指定redis的主机地址与端口号
host = '127.0.0.1'
port = 6379
app.config['SESSION_REDIS'] = StrictRedis(host, port)
app.config['SESSION_USE_SIGNER'] = True
# 设置session有效期,flask内置的session有效期配置
app.config['PERMANENT_SESSION_LIFETIME'] = 3600


# 创建sqlalchemy实例对象
db = SQLAlchemy(app)


# 使用管理器对象
manage = Manager(app)
# 使用迁移
Migrate(app, db)
# 添加迁移命令
manage.add_command('db', MigrateCommand)
# 实例化session
Session(app)


@app.route('/')
def index():
    session['itcast'] = '2019'
    return 'hehe'


if __name__ == '__main__':
    manage.run()