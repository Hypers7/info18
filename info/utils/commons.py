from flask import session, current_app, g

from info.models import User


def index_filter(index):
    if index == 0:
        return 'first'
    elif index == 1:
        return 'second'
    elif index == 2:
        return 'third'
    else:
        return ''


def login_required(func):

    wrapper_name = func.__name__

    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return func(*args, **kwargs)

    wrapper.__name__ = wrapper_name

    return wrapper


# import functools
#
#
# def login_required(func):
#
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         user_id = session.get('user_id')
#         user = None
#         if user_id:
#             try:
#                 user = User.query.get(user_id)
#             except Exception as e:
#                 current_app.logger.error(e)
#         g.user = user
#         return func(*args, **kwargs)
#
#     return wrapper