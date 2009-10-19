from collect import items
from collections import defaultdict

class Bunch(dict):
    """ A dictionary that provides attribute-style access.
    """
    
    def __repr__(self):
        keys = self.keys()
        keys.sort()
        args = ', '.join(['%s=%r' % (key, self[key]) for key in keys])
        return '%s(%s)' % (self.__class__.__name__, args)
    
    def __contains__(self, k):
        try:
            return hasattr(self, k) or dict.__contains__(self, k)
        except:
            return False
    
    # only called if k not found in normal places 
    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)
    
    def __setattr__(self, k, v):
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
            object.__setattr__(self, k, v)
        except:
            try:
                self[k] = v
            except:
                raise AttributeError(k)
    
    def __delattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
            object.__delattr__(self, k)
        except:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
    

class DefaultBunch(Bunch, defaultdict):
    """ A defaultdict that provides attribute-style access.
    """

def InfiBunch():
    "Returns a DefaultBunch that defaults to DefaultBunch all the way down."
    return DefaultBunch( InfiBunch )


class BunchBunch(Bunch):
    """ A dictionary that provides attribute-style access and
        recursively setting dot-separated keys.
    """
    
    def __init__(self, __d=None, **kv):
        dict.__init__(self)
        self.update(__d, **kv)
    
    def setdotted(self, key, value):
        """ Sets a key-value pair in the dict interpreting a dot-separated key
            as a series of nested dictionaries, created as necessary.
        """
        try:
            k, rest = key.split('.',1)
            if not isinstance(self.get(k), BunchBunch):
                self[k] = BunchBunch()
                self[k].setdotted(rest, value)
        except ValueError:
            self[key] = BunchBunch(value) if isinstance(value, dict) else value
    
    def update(self, __d, **kv):
        "Accepts any number of dictionaries, and interprets dotted keys recursively."
        for k,v in items(__d,kv):
            self.setdotted(k,v)
        return self
    
    def deepcopy(self):
        c = self.copy()
        for k, v in c.iteritems():
            if hasattr(v, 'deepcopy') and callable(v.deepcopy):
                c[k] = v.deepcopy()
            elif isinstance(v, dict):
                c[k] = v.copy()
        return c
    
    def copy(self):
        return BunchBunch( dict.copy(self) )
    
    def todict(self):
        c = dict.copy(self)
        for k, v in c.iteritems():
            if callable(getattr(v, 'todict', None)):
                c[k] = v.todict()
            elif isinstance(v, dict):
                c[k] = v.copy()
        return c


class DefaultBunchBunch(BunchBunch, defaultdict):
    """ A defaultdict that provides attribute-style access and
        recursively setting dot-separated keys.
    """
    
    def __init__(self, factory):
        defaultdict.__init__(self, factory)
    

def InfiBunchBunch():
    """ Returns a DefaultBunchBunch that defaults to 
        DefaultBunchBunch all the way down.
    """
    return DefaultBunchBunch( InfiBunchBunch )



BUNCHER_ATTRS = ('__getattribute__', '__setattr__', '__dict__', '_proxy', '__repr__', '__delattr__', 'obj', '__class__', '__new__', '__del__', '__init__')
class Buncher(dict):
    """ A dictionary-proxy that provides attribute-style access to another dict object.
    """
    
    def __init__(self, obj):
        dict.__init__(self)
        self.obj = obj
    
    def __repr__(self):
        keys = self.keys()
        keys.sort()
        args = ', '.join(['%s=%r' % (key, self[key]) for key in keys])
        return '%s(%s)' % (self.__class__.__name__, args)
    
    def __getattribute__(self, k):
        if k in BUNCHER_ATTRS:
            return object.__getattribute__(self, k)
        
        o = self.obj
        try:
            return getattr(o, k)
        except AttributeError: pass
        
        try:
            return o[k]
        except KeyError:
            raise AttributeError(k)
    
    def __setattr__(self, k, v):
        if k == "obj":
            object.__setattr__(self, k, v)
        else:
            self.obj[k] = v
    
    def __delattr__(self, k):
        if k == "obj":
            object.__delattr__(self, k)
        else:
            del self.obj[k]
    
    def _proxy(method):
        def proxied(self, *args, **kw):
            return getattr(self.obj, method)(*args, **kw)
        proxied.__name__ = method
        return proxied
    
    for method in ('__hash__', 
            '__contains__', '__getitem__', '__setitem__', '__delitem__', 
            '__len__', '__iter__', 
            '__cmp__', '__eq__', '__ne__', '__ge__', '__gt__', '__le__', '__lt__'):
        locals()[method] = _proxy(method)
    

