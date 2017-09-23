class StrCallable(object):
    """Wraps around a callable to evaluate it on str and repr."""
    
    def __init__(self, function):
        self._function = function
        
    def __call__(self, *args, **kwargs):
        return self._function(*args, **kwargs)
        
    def __str__(self):
        return str(self._function())
        
    def __repr__(self):
        return str(self._function())
        
    @property
    def __class__(self):
        return self._function.__class__
