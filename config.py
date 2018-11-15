# 导入redis模块
from redis import StrictRedis


class Config():
    # 设置debug调试模式
    DEBUG = None
    # 配置秘钥
    SECRET_KEY = '7nqfG7KXkkmg9e3gifTAuQNtXTQlIlYwlRuIibGlXyLjTYNW7MBtWA=='

    # mysql配置信息
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@localhost/python_1'
    # 动态追踪修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 实现状态保持, 配置session信息存储在redis中
    SESSION_TYPE = 'redis'
    # 指定redis的主机地址
    host = '127.0.0.1'
    # 指定redis端口号
    port = 6379
    SESSION_REDIS = StrictRedis(host, port)
    SESSION_USE_SIGNER = True
    # 设置session有效期,flask内置的session有效期配置
    PERMANENT_SESSION_LIFETIME = 3600


# 封装不同环境下的配置类,开发模式与生产模式
class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_dict = {
    'dev':DevelopmentConfig,
    'pro':ProductionConfig
}