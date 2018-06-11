from fly_bbs.utils import JSONEncoder
from werkzeug.security import check_password_hash


class Page:
    def __init__(self, pn, size, sort_by=None, filter1=None, result=None, has_more=False, total_page=0, total=0):
        self.pn = pn
        self.size = size
        self.sort_by = sort_by
        self.result = result
        self.filter1 = filter1
        self.has_more = has_more
        self.total_page = total_page
        self.total=total

    def __repr__(self):
        return JSONEncoder().encode(o = self.__dict__)


class R(dict):

    @staticmethod
    def ok(msg=None, data=None):
        r = R()
        r.put('status', 0)
        r.put('msg', msg)
        r.put('data', data)
        return r

    @staticmethod
    def fail(code=404, msg=None):
        r = R()
        r.put('status', code)
        r.put('msg', msg)
        return r

    def put(self, k, v):
        self.__setitem__(k, v)
        return self

    def get_status(self):
        return self.get('status')

    def get_msg(self):
        return self.get('msg')


class BaseResult(R):
    def __init__(self, code=0, msg='', data=None):
        self.put('status', code)
        self.put('msg', msg)
        self.put('data', data)


class User:
    user = None
    is_authenticated = True
    is_anonymous = False
    is_active = False

    def __init__(self, user):
        self.user = user
        self.is_active = user['is_active']

    def get_id(self):
        return str(self.user['_id'])

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)


class GlobalApiException(Exception):

    def __init__(self, cm):
        self.code_msg = cm
