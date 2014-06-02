
from __future__ import print_function

VERBOSE = False

dict_dict = dict.__dict__
dict_keys = dict_dict.keys()

class RedisDict(object):
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
                                print("%s with attribute %s: %s" % (type(err).__name__, attr_name, err))
                        else:
                            if VERBOSE:
                                print("Copied docstring for attribute: %s" % attr_name)
            
            return type(name, bases, attrs)
    
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
        # We cannot (yet) set dict-default methods
        raise NotImplementedError("Fuck your defaults")
    
    def keys(self):
        return self.r.hkeys(self.u)
    
    def values(self):
        return self.r.hvals(self.u)
    
    @property
    def dict(self):
        """ Return a vanilla Python dict populated from the RedisDict """
        # This method has no analogous method in the dict builtin
        return self.r.hgetall(self.u)
    
    # Methods aliased from the dict builtin
    has_key = property(lambda self: self.dict.has_key)
    get = property(lambda self: self.dict.get)
    items = property(lambda self: self.dict.items)
    iteritems = property(lambda self: self.dict.iteritems)
    iterkeys = property(lambda self: self.dict.iterkeys)
    itervalues = property(lambda self: self.dict.itervalues)
    viewitems = property(lambda self: self.dict.viewitems)
    viewkeys = property(lambda self: self.dict.viewkeys)
    viewvalues = property(lambda self: self.dict.viewvalues)
    #copy = property(lambda self: self.dict.copy) # not quite right
    fromkeys = property(lambda self: self.dict.fromkeys) # not quite right either
    __eq__ = property(lambda self: self.dict.__eq__)
    __ne__ = property(lambda self: self.dict.__ne__)
    __cmp__ = property(lambda self: self.dict.__cmp__)
    __format__ = property(lambda self: self.dict.__format__)
    __reduce__ = property(lambda self: self.dict.__reduce__)
    __reduce_ex__ = property(lambda self: self.dict.__reduce_ex__)
    __iter__ = property(lambda self: self.dict.__iter__)
    __repr__ = property(lambda self: self.dict.__repr__)
    __str__ = property(lambda self: self.dict.__str__)
    
    # Unimplemented dict methods
    __lt__ = property(lambda self: NotImplemented)
    __gt__ = property(lambda self: NotImplemented)
    __le__ = property(lambda self: NotImplemented)
    __ge__ = property(lambda self: NotImplemented)
    
    def copy(self):
        return RedisDict(self.u, self.r)
    
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