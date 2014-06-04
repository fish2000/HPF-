
from __future__ import print_function

VERBOSE = False
NOTHING = object()

dict_dict = dict.__dict__
dict_keys = dict_dict.keys()

class BaseRedisDict(object):
    """ Dict wrapper for a Redis set """
    
    class __metaclass__(type):
        def __new__(cls, name, bases, attrs):
            """ Get docstrings for our duckpunched dict methods,
                from the Python builtin dict base class """
            
            for attr_name in attrs.keys():
                if attr_name in dict_keys:
                    if hasattr(dict_dict[attr_name], '__doc__'):
                        # If you try to copy docstrings for an aliased dict method,
                        # either an AttributeError or (more likely) a TypeError
                        # will stop the show -- hence all of this stuff:
                        try:
                            attrs[attr_name].__doc__ = dict_dict[attr_name].__doc__
                        except (TypeError, AttributeError), err:
                            if VERBOSE:
                                print("%s with attribute %s: %s" % (
                                    type(err).__name__, attr_name, err))
                        else:
                            if VERBOSE:
                                print("Copied docstring for attribute: %s" % attr_name)
            
            return type(name, bases, attrs)
    
    def __init__(self, username, redis):
        self.u = username
        self.r = redis
    
    def __len__(self):
        return self.r.hlen(self.u)
    
    def __contains__(self, key):
        return bool(self.r.hexists(self.u, key))
    
    def __getitem__(self, key):
        if key not in self:
            raise KeyError(key)
        return self.r.hget(self.u, key)
    
    def __setitem__(self, key, value):
        self.r.hset(self.u, key, value)
    
    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        self.r.hdel(self.u, key)
    
    def get(self, key, default=None):
        if key not in self:
            return default
        return self.r.hget(self.u, key)
    
    def setdefault(self, key, default=NOTHING):
        if default is NOTHING:
            return self.get(key)
        self.r.hsetnx(self.u, key, default)
    
    def get_default(self, key):
        return self.get(key)
    
    def keys(self):
        return self.r.hkeys(self.u)
    
    def values(self):
        return self.r.hvals(self.u)
    
    def has_key(self, key):
        return key in self
    
    @property
    def dict(self):
        """ Return a vanilla Python dict populated from the RedisDict """
        # This method has no analogous method in the dict builtin
        return self.r.hgetall(self.u)
    
    @staticmethod
    def fromkeys(S, v=None):
        return dict.fromkeys(S, v)
    
    # Methods aliased from the dict builtin
    items = property(lambda self: self.dict.items)
    iteritems = property(lambda self: self.dict.iteritems)
    iterkeys = property(lambda self: self.dict.iterkeys)
    itervalues = property(lambda self: self.dict.itervalues)
    viewitems = property(lambda self: self.dict.viewitems)
    viewkeys = property(lambda self: self.dict.viewkeys)
    viewvalues = property(lambda self: self.dict.viewvalues)
    
    # Protocols aliased from the dict builtin
    __eq__ = property(lambda self: self.dict.__eq__)
    __ne__ = property(lambda self: self.dict.__ne__)
    __cmp__ = property(lambda self: self.dict.__cmp__)
    __format__ = property(lambda self: self.dict.__format__)
    __iter__ = property(lambda self: self.dict.__iter__)
    __repr__ = property(lambda self: self.dict.__repr__)
    __str__ = property(lambda self: self.dict.__str__)
    
    # Unimplemented dict protocol methods
    __lt__ = property(lambda self: NotImplemented)
    __gt__ = property(lambda self: NotImplemented)
    __le__ = property(lambda self: NotImplemented)
    __ge__ = property(lambda self: NotImplemented)
    
    # Pickling-protocol helper methods
    def __getstate__(self):
        return self.u
    
    def __setstate__(self, state):
        # Uses the default redis connection
        import redis
        self.u = state
        self.r = redis.Redis()
    
    def copy(self):
        return RedisDict(self.u, self.r)
    
    def pop(self, key, default=NOTHING):
        if key not in self:
            if default is NOTHING:
                raise KeyError(key)
            return default
        out = self.r.hget(self.u, key)
        self.r.hdel(self.u, key)
        return out
    
    def popitem(self):
        keys = self.keys()
        if len(keys) < 1:
            raise KeyError('no keys')
        key = keys.pop()
        return self.pop(key)
    
    def clear(self):
        self.r.hdel(self.u, *self.keys())
    
    def update(self, E, **F):
        # This is copied right out of the Python docs
        # for the dict builtin's methods
        if hasattr(E, 'keys'):
            for k in E:
                self[k] = E[k]
        else:
            for (k, v) in E:
                self[k] = v
        for k in F:
            self[k] = F[k]

class RedisDict(BaseRedisDict):
    
    def __setstate__(self, state):
        # THIS MAKES THE WHOLE ENTERPRISE UN-PORTABLE
        from sandpiper.redpool import redpool as redis
        self.u = state
        self.r = redis


class RedisSet(object):
    
    def __init__(self, setname, redis, values=NOTHING):
        self.s = setname
        self.r = redis
        if values is not NOTHING:
            self.r.sadd(self.s, *values)
    
    def __len__(self):
        return self.r.scard(self.s)
    
    def __contains__(self, value):
        return self.r.sismember(self.s, value)
    
    def add(self, elem):
        self.r.sadd(self.s, elem)
    
    def remove(self, elem):
        if self.r.srem(self.s, elem) == 0:
            raise KeyError(elem)
    
    def discard(self, elem):
        self.r.srem(self.s, elem)
    
    def pop(self):
        return self.r.spop(self.s)
    
    def clear(self):
        self.r.sinterstore(self.s, self.s, '')
    
    @property
    def set(self):
        return self.r.smembers(self.s)
    
    isdisjoint = property(lambda self: self.set.isdisjoint)
    issubset = property(lambda self: self.set.issubset)
    issuperset = property(lambda self: self.set.issuperset)
    union = property(lambda self: self.set.union)
    intersection = property(lambda self: self.set.intersection)
    difference = property(lambda self: self.set.difference)
    symmetric_difference = property(lambda self: self.set.symmetric_difference)
    update = property(lambda self: self.set.update)
    intersection_update = property(lambda self: self.set.intersection_update)
    difference_update = property(lambda self: self.set.difference_update)
    symmetric_difference_update = property(lambda self: self.set.symmetric_difference_update)
    
    __and__ = property(lambda self: self.set.__and__)
    __iand__ = property(lambda self: self.set.__iand__)
    __rand__ = property(lambda self: self.set.__rand__)
    __or__ = property(lambda self: self.set.__or__)
    __ior__ = property(lambda self: self.set.__ior__)
    __ror__ = property(lambda self: self.set.__ror__)
    __xor__ = property(lambda self: self.set.__xor__)
    __ixor__ = property(lambda self: self.set.__ixor__)
    __rxor__ = property(lambda self: self.set.__rxor__)
    __sub__ = property(lambda self: self.set.__sub__)
    __isub__ = property(lambda self: self.set.__isub__)
    __rsub__ = property(lambda self: self.set.__rsub__)
    
    __cmp__ = property(lambda self: self.set.__cmp__)
    __eq__ = property(lambda self: self.set.__eq__)
    __ne__ = property(lambda self: self.set.__ne__)
    __le__ = property(lambda self: self.set.__le__)
    __lt__ = property(lambda self: self.set.__lt__)
    __ge__ = property(lambda self: self.set.__ge__)
    __gt__ = property(lambda self: self.set.__gt__)
    
    __format__ = property(lambda self: self.set.__format__)
    __iter__ = property(lambda self: self.set.__iter__)
    __str__ = property(lambda self: self.set.__str__)
    __repr__ = property(lambda self: self.set.__repr__)
    
    '''
    def isdisjoint(self, other):
        pass
    
    def issubset(self, other):
        pass
    
    def issuperset(self, other):
        pass
    
    def union(self, *others):
        pass
    
    def intersection(self, *others):
        pass
    
    def difference(self, *others):
        pass
    
    def symmetric_difference(self, other):
        pass
    
    def update(self, *others):
        pass
    
    def intersection_update(self, *others):
        pass
    
    def difference_update(self, *others):
        pass
    
    def symmetric_difference_update(self, other):
        pass
    '''
