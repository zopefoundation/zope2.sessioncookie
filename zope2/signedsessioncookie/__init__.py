"""Signed Session Cookies for Zope2"""

from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from pyramid.session import SignedCookieSessionFactory
from zope.component import getUtility

from .interfaces import ISignedSessionCookieConfig

ZopeCookieSession = None

def _getSessionClass():
    """Defer initializing session class parameters at import time.

    Wait until ZCA is available.
    """
    global ZopeCookieSession

    if ZopeCookieSession is None:
        config = getUtility(ISignedSessionCookieConfig)
        attrs = config.getCookieAttrs()
        PyramidCookieSession = SignedCookieSessionFactory(**attrs)

        class ZopeCookieSession(PyramidCookieSession):
            """Wrap Pyramid's class, adding Zope2 security majyk.
            """
            security = ClassSecurityInfo()
            security.setDefaultAccess('allow')
            security.declareObjectPublic()

            def __guarded_getitem__(self, key):
                return self[key]

            def __guarded_setitem__(self, key, value):
                self[key] = value

            def __guarded_delitem__(self, key):
                del self[key]

            def changed(self):
                self._set_cookie(self.request.RESPONSE)

        InitializeClass(ZopeCookieSession)

    return ZopeCookieSession

def ssc_hook(container, request):
    """Hook for '__before_traverse__' on root object.

    Establishes 'pyramid.session'-compatible methods on request/response,
    and sets up the wrapper session class.
    """
    # Make the response emulate Pyramid's response.
    request.RESPONSE.set_cookie = request.RESPONSE.setCookie

    # Set up the lazy SESSION implementation.
    klass = _getSessionClass()
    request.set_lazy('SESSION', lambda: klass(request))
