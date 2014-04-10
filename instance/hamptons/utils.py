

class RedisDict(object):
    """ Dict wrapper for a Redis set"""
    def __init__(self, username, redis):
        self.u = username
        self.r = redis
        self.df = {}
    
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
    
    def setdefault(self, key, default=None):
        raise NotImplementedError("Fuck your defaults")
    
    def keys(self):
        return self.r.hkeys(self.u)
    
    def values(self):
        return self.r.hvals(self.u)
    
    @property
    def dict(self):
        return self.r.getall(self.u)
    
    has_key = property(lambda self: self.dict.has_key)
    get = property(lambda self: self.dict.get)
    items = property(lambda self: self.dict.items)
    iteritems = property(lambda self: self.dict.iteritems)
    iterkeys = property(lambda self: self.dict.iterkeys)
    itervalues = property(lambda self: self.dict.itervalues)
    viewitems = property(lambda self: self.dict.viewitems)
    viewkeys = property(lambda self: self.dict.viewkeys)
    viewvalues = property(lambda self: self.dict.viewvalues)
    copy = property(lambda self: self.dict.copy) # not quite right
    fromkeys = property(lambda self: self.dict.fromkeys)
    __eq__ = property(lambda self: self.dict.__eq__)
    __ne__ = property(lambda self: self.dict.__ne__)
    __cmp__ = property(lambda self: self.dict.__cmp__)
    __format__ = property(lambda self: self.dict.__format__)
    __reduce__ = property(lambda self: self.dict.__reduce__)
    __reduce_ex__ = property(lambda self: self.dict.__reduce_ex__)
    __iter__ = property(lambda self: self.dict.__iter__)
    __repr__ = property(lambda self: self.dict.__repr__)
    __str__ = property(lambda self: self.dict.__str__)
    
    __lt__ = property(lambda self: NotImplemented)
    __gt__ = property(lambda self: NotImplemented)
    __le__ = property(lambda self: NotImplemented)
    __ge__ = property(lambda self: NotImplemented)
    
    def pop(self, key, default=None):
        if key not in self:
            if default is None:
                raise KeyError(key)
            return default
        out = self.r.hget(self.u, key)
        self.r.hdel(key)
        return out
    
    def popitem(self):
        keys = self.keys()
        if len(keys) < 1:
            raise KeyError('no keys')
        key = keys.pop()
        return self.pop(key)
    
    def clear(self):
        self.r.hdel(*self.keys())
    
    def update(self, E, **F):
        if hasattr(E, 'keys'):
            for k in E:
                self[k] = E[k]
        else:
            for (k, v) in E:
                self[k] = v
        for k in F:
            self[k] = F[k]