# coding=utf-8

import os


class Proxy(object):
    def __init__(self, func, name=None):
        object.__setattr__(self, "__func__", func)
        object.__setattr__(self, "__name__", name)

    @property
    def self(self):
        return getattr(self.__func__(), self.__name__)

    def __getattr__(self, item):
        return getattr(getattr(self.__func__(), self.__name__), item)

    def __setattr__(self, key, value):
        obj = getattr(self.__func__(), self.__name__)
        setattr(obj, key, value)
        setattr(self.__func__(), self.__name__, obj)

    def __setitem__(self, key, value):
        obj = getattr(self.__func__(), self.__name__)
        obj.__setitem__(key, value)
        setattr(self.__func__(), self.__name__, obj)

    def __getitem__(self, item):
        return getattr(self.__func__(), self.__name__).__getitem__(item)

    @property
    def __dict__(self):
        return getattr(self.__func__(), self.__name__).__dict__


class ImmutableDict(dict):
    """
    不可变dict
    """
    def __setitem__(self, key, value):
        raise TypeError("%r object does not support item assignment" % type(self).__name__)

    def __delitem__(self, key):
        raise TypeError("%r object does not support item deletion" % type(self).__name__)

    def __getattribute__(self, attribute):
        if attribute in ('clear', 'update', 'pop', 'popitem', 'setdefault'):
            raise AttributeError("%r object has no attribute %r" % (type(self).__name__, attribute))
        return dict.__getattribute__(self, attribute)

    def __hash__(self):
        return hash(tuple(sorted(self.iteritems())))

    def fromkeys(self, S, v=None):
        return type(self)(dict(self).fromkeys(S, v))


class Env(dict):
    """
    应用环境变量, 获取所有以`prefix.upper()_` 开头的环境变量
    """
    def __init__(self, prefix="kalos"):
        object.__setattr__(self, "__env_prefix__", prefix.upper())

        kvs = {}
        for k, v in os.environ.iteritems():
            if k.startswith(self.__env_prefix__):
                key = k[len(self.__env_prefix__) + 1:]
                if key in self.keys():
                    msg = "duplicate key {}".format(key)
                    raise KeyError(msg)
                kvs[key] = v
        super(Env, self).__init__(**kvs)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return ""


def cookie_date(d):
    """
    转化成cookie expire格式
    :param d:
    :return:
    """
    d = d.utctimetuple()
    delim = "-"
    return '%s, %02d%s%s%s%s %02d:%02d:%02d GMT' % (
        ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')[d.tm_wday],
        d.tm_mday, delim,
        ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
         'Oct', 'Nov', 'Dec')[d.tm_mon - 1],
        delim, str(d.tm_year), d.tm_hour, d.tm_min, d.tm_sec
    )