from fly_bbs.utils import JSONEncoder
from werkzeug.security import check_password_hash
class Page:
    def __init__(self, pn, size, sort_by, filter1, result, has_more, total_page, total):
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
    def ok(self):
        self.__setitem__('status', 0)
        return self
    def fail(self, code=404):
        self.__setitem__('status', code)
        return self
    def put(self, k, v):
        self.__setitem__(k, v)
        return self

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