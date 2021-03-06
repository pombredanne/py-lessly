""" Supplies DelegatingJSONEncoder, a JSON encoder which delegates to the supplied 
    object if it provides matching methods for getting a serializable 
    representation or a full encoding.
"""

__all__ = ('DelegatingJSONEncoder', '_default_encoder', 'encode', 'decode')

from json import JSONEncoder
from datetime import date, time, datetime



class DelegatingJSONEncoder(JSONEncoder):
    """ A JSON encoder which delegates to the supplied object if it provides
        matching methods for getting a serializable representation or a
        full encoding.
    """
    
    def default(self, o):
        if hasattr(o, '__json_default__'):
            return o.__json_default__()
            
        elif isinstance(o, (datetime, date, time)):
            return o.strftime('%b %d %Y %H:%M:%S')
        
        try:
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, o)
    
    def encode(self, o):
        if hasattr(o, '__json__'):
            return o.__json__()
        
        if callable(getattr(o, '__json_default__', None)):
            o = o.__json_default__()
        
        return super(DelegatingJSONEncoder, self).encode(o)
    

_default_encoder = DelegatingJSONEncoder()
encode = _default_encoder.encode

