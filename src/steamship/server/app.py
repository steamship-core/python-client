"""

Please see https://docs.steamship.com/ for information about building a Steamship App

"""

import json
from typing import Dict, Union
from functools import wraps
from steamship.server.request import Request
from steamship.server.response import Response, Error
from functools import wraps

def makeRegisteringDecorator(foreignDecorator):
    """
        Returns a copy of foreignDecorator, which is identical in every
        way(*), except also appends a .decorator property to the callable it
        spits out.
    """
    def newDecorator(func):
        # Call to newDecorator(method)
        # Exactly like old decorator, but output keeps track of what decorated it
        R = foreignDecorator(func) # apply foreignDecorator, like call to foreignDecorator(method) would have done
        R.decorator = newDecorator # keep track of decorator
        #R.original = func         # might as well keep track of everything!
        return R

    newDecorator.__name__ = foreignDecorator.__name__
    newDecorator.__doc__ = foreignDecorator.__doc__
    newDecorator.__is_endpoint__ = True
    # (*)We can be somewhat "hygienic", but newDecorator still isn't signature-preserving, i.e. you will not be able to get a runtime list of parameters. For that, you need hackish libraries...but in this case, the only argument is func, so it's not a big issue

    return newDecorator


# https://stackoverflow.com/questions/2366713/can-a-decorator-of-an-instance-method-access-the-class
def endpoint(verb: str = None, path: str = None):
  """By using **kw we can tag the function with any parameters"""
  def decorator(function):
    # This is used in conjunction with the __init_subclass__ code!
    # Otherwise the __name__ won't be correct in maybeDecorated.__name__!
    @wraps(function) 
    def wrap(self, *args, **kwargs):
      return function(self, *args, **kwargs)
    wrap.__path__ = path
    wrap.__verb__ = verb
    return wrap
  decorator = makeRegisteringDecorator(decorator)
  return decorator

def get(path: str, **kwargs):
  return endpoint(verb='GET', path=path, **kwargs)

def post(path: str, **kwargs):
  return endpoint(verb='POST', path=path, **kwargs)

class App:
  """An NLUDB microservice.

  This base class:

    1. Provide a pre-authenticated instance of the NLUDB client
    2. Provides a Lambda handler that routes to registered functions
    3. Provides useful methods connecting functions to the router.
  """
    
  """Base class to expose instance methods"""
  def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    cls._method_mappings = {}
    
    for maybeDecorated in cls.__dict__.values():
      if hasattr(maybeDecorated, 'decorator'):
        decorator = getattr(maybeDecorated, 'decorator')
        if hasattr(decorator, '__is_endpoint__') and getattr(decorator, '__is_endpoint__') == True:
          path = getattr(maybeDecorated, '__path__') if hasattr(maybeDecorated, '__path__') else None
          verb = getattr(maybeDecorated, '__verb__') if hasattr(maybeDecorated, '__verb__') else None        
          cls._register_mapping(verb, path, maybeDecorated.__name__)

  @classmethod
  def _register_mapping(Self, verb: str, path: str, name: str):
    """Registering a mapping permits the method to be invoked via HTTP."""
    if getattr(Self, "_method_mappings") is None:
      setattr(Self, "_method_mappings", {})
    if verb not in Self._method_mappings:
      Self._method_mappings[verb] = {}
    Self._method_mappings[verb][path] = name
    print("[{}] {} {} => {}".format(Self.__name__, verb, path, name))   

  def __call__(self, request: Request, context: any = None):
    """Invokes a method call if it is registered."""
    if not getattr(self.__class__, "_method_mappings"):
      return Error(
        httpStatus=404,
        message="No mappings available for app."
      )

    if request.verb not in self.__class__._method_mappings:
      return Error(
        httpStatus=404,
        message="No methods for verb {} available.".format(request.verb)
      )
    if request.method not in self.__class__._method_mappings[request.verb]:
      return Error(
        httpStatus=404,
        message="No handler for {} {} available.".format(request.verb, request.method)
      )    
    method = self.__class__._method_mappings[request.verb][request.method]

    if not (hasattr(self, method) and callable(getattr(self, method))):
      return Error(
        httpStatus=500,
        message="Handler for {} {} not callable.".format(request.verb, request.method)
      )

    if request.arguments is None:      
      return getattr(self, method)()
    else:
      return getattr(self, method)(**request.arguments)
