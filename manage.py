from flask import Flask, session
# 集成管理器脚本
from flask_script import Manager
# 集成sqlalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 数据迁移的扩展
from flask_migrate import Migrate, MigrateCommand
# 集成状态保持的扩展
from flask_session import Session
# 导入配置文件
from config import config_dict
app = Flask(__name__)

# 使用配置信息
app.config.from_object(config_dict['dev'])

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