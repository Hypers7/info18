# 导入蓝图对象
from . import passport_blue
# 导入captcha工具 生成图片验证码
from info.utils.captcha.captcha import captcha
# 导入flask内置的请求上下文对象
from flask import request, jsonify, current_app, make_response, session

from info.utils.response_code import RET
# 导入redis实例
from info import redis_store, constants, db

import re, random
# 导入云通讯
from info.libs.yuntongxun.sms import CCP
# 导入模型类
from info.models import User

from datetime import datetime


# 生成图片验证码
@passport_blue.route('/image_code')
def generate_image_code():
    # 生成图片验证码
    # 写接口:接收参数 检查参数 业务处理 返回结果
    # 参数:前段传如uuid
    # 1.获取前端传入的uuid,查询字符串args
    # 2.如果没有uuid返回信息
    # 3.调用captcha工具生成图片验证码 name test image
    # 4.把图片验证码的内容test 根据uuid传给redis数据库中
    # 5.返回图片

    # 获取参数
    image_code_id = request.args.get('image_code_id')
    # 检查参数是否存在,导入response_code文件
    if not image_code_id:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 调用工具captcha生成图片验证码
    name, text, image = captcha.generate_captcha()
    # text存入redis数据库中,在info/__init__文件中实例化redis对象
    try:
        redis_store.setex('ImageCode_' + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        # 把错误信息记录到项目日志中
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='存储数据失败')
    else:
        # 使用响应对象返回图片
        response = make_response(image)
        # 设置响应类型
        response.headers['Content-Type'] = 'image/jpg'
        # 返回响应
        return response


# 发送短信验证码
@passport_blue.route('/sms_code', methods=['POST'])
def send_sms_code():

    # 接收参数 检查参数 业务处理 返回结果
    # 1 获取参数 mobile image_code image_code_id
    # 2 检查参数 参数必须全部都存在
    # 3 检查手机号的格式,使用正则表达式
    # 4 检查图片验证码是否正确
    # 5 从redis中获取真实的图片验证码
    # 6 判断图片获取结果是否存在
    # 7 如果存在先删除redis数据库中的图片验证码,因为图片验证码只能比较一次,只能读取redis数据库一次
    # 8 比较图片验证码是否正确
    # 9 生成短信验证码,6位数
    # 10 把短信验证码存储在redis数据库中
    # 11 调用云通讯发送短信
    # 12 保存发送结果,用来判断发送是否成功
    # 13 返回结果
    # 获取post请求的三个参数
    mobile = request.json.get('mobile')
    image_code = request.json.get('image_code')
    image_code_id = request.json.get('image_code_id')
    # 检查参数的完整性
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 检查手机号格式
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    try:
        real_image_code = redis_store.get('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据失败')
    # 判断获取结果
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已过期')
    # 如果获取到验证码需要把redis中的图片验证码删除,因为只能get一次
    try:
        redis_store.delete('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    # 比较图片验证码是否正确 ,忽略大小写
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码错误')

    # 根据手机号来查询用户未注册
    try:
        user = User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据库失败')
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已注册')
    # 生成短信随机码
    sms_code = '%06d' % random.randint(0, 9999999)
    try:
        redis_store.setex('SMSCode_' + mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
    # 调用云通讯发送短信
    try:
        # 构造短信发送对象
        ccp = CCP()
        # 第一个参数是手机号,第二个参数是内容夹过期时间
        result = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES/60],1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='发送短信异常')
    # 判断发送结果
    if result == -1:
        return jsonify(errno=RET.THIRDERR, errmsg='发送失败')
    else:
        return jsonify(errno=RET.OK, errmsg='发送成功')


# 注册
@passport_blue.route('/register', methods=['POST'])
def register():

    mobile = request.json.get('mobile')
    sms_code = request.json.get('sms_code')
    password = request.json.get('password')
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    try:
        real_sms_code = redis_store.get('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据库失败')
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码已过期')
    if real_sms_code != str(sms_code):
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')
    try:
        redis_store.delete('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')
    else:
        if user:
            return jsonify(errno=RET.DATAERR, errmsg='手机号以注册')

    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # 调用了模型类中的密码加密方法,generate_password_hash方法,werkzeug提供的
    user.password = password
    # 提交用户数据到mysql 数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DATAERR, errmsg='保存用户信息失败')
    session['user_id'] = user.id
    session['mobile'] = mobile
    session['nick_name'] = mobile

    return jsonify(errno=RET.OK, errmsg='注册成功')


# 登录
@passport_blue.route('/login', methods=['POST'])
def login():
    mobile = request.json.get('mobile')
    password = request.json.get('password')
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    if not re.match(r'1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')
    # 防止反推断
    if user is None and not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg='用户名或密码错误')
    #
    user.last_login = datetime.now()
    #
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存用户信息出错')

    session['user_id'] = user.id
    session['mobile'] = mobile
    # 拿到mysql中的nick_mane
    # 确保redis中缓存数据 和mysql数据库中的真实数据保持一致
    session['nike_name'] = user.nick_name

    return jsonify(errno=RET.OK, errmsg='登录成功')





















