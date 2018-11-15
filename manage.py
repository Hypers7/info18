# 集成管理器脚本
from flask_script import Manager
# 数据迁移的扩展
from flask_migrate import Migrate, MigrateCommand
# 导入info目录下的app和db
from info import create_app, db, models
# 初始化数据库中的表,有过表结构才能迁移,

# 调用函数 获取app 传入参数 通过参数的不同可以获取不同环境下的app, db
app = create_app('dev')


# 使用管理器对象
manage = Manager(app)
# 使用迁移
Migrate(app, db)
# 添加迁移命令
manage.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manage.run()