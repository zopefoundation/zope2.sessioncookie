import unittest


class _Base(unittest.TestCase):

    def setUp(self):
        from zope.component.testing import setUp
        from zope2 import signedsessioncookie
        setUp()
        signedsessioncookie.ZopeCookieSession = None

    def tearDown(self):
        from zope.component.testing import tearDown
        from zope2 import signedsessioncookie
        signedsessioncookie.ZopeCookieSession = None
        tearDown()

    def _setUpUtility(self, secret='SEEKRIT', cookie_name='COOKIE'):
        from zope.component import provideUtility
        from ..config import SignedSessionCookieConfig
        config = SignedSessionCookieConfig(secret, cookie_name=cookie_name)
        provideUtility(config)


class Test__getSessionClass(_Base):

    def _callFUT(self):
        from .. import _getSessionClass
        return _getSessionClass()

    def test_w_existing_set(self):
        from zope2 import signedsessioncookie
        EXISTING = signedsessioncookie.ZopeCookieSession = object()
        klass = self._callFUT()
        self.assertTrue(klass is EXISTING)

    def test_wo_existing_set(self):
        from zope2 import signedsessioncookie
        self.assertTrue(signedsessioncookie.ZopeCookieSession is None)
        self._setUpUtility()
        klass = self._callFUT()
        self.assertEqual(klass._cookie_name, 'COOKIE')
        self.assertTrue(signedsessioncookie.ZopeCookieSession is klass)

    def test_session_class_extras(self):
        self._setUpUtility()
        klass = self._callFUT()
        request = _Request()
        response = request.RESPONSE = _Response()
        session = klass(request)

        session['foo'] = 'bar'
        self.assertEqual(session.__guarded_getitem__('foo'), 'bar')

        session.__guarded_setitem__('foo', 'baz')
        self.assertEqual(session['foo'], 'baz')

        session.__guarded_delitem__('foo')
        self.assertEqual(dict(session), {})


class _Response(object):

    def __init__(self):
        self.cookies = {}

    def set_cookie(self, name, **kw):
        self.cookies[name] = kw


class _Request(object):

    def __init__(self, **kw):
        self.cookies = kw
        self._lazy = {}

    def set_lazy(self, name, factory):
        self._lazy[name] = factory
