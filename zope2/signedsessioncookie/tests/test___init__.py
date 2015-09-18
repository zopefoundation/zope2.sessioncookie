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

        self.assertEqual(response.counter, 0)  # cookie not set
        self.assertEqual(len(request._response_callbacks), 1)
        request._response_callbacks[0](request, response)
        self.assertEqual(response.counter, 1)


class Test_ssc_hook(_Base):

    def _callFUT(self, container, request):
        from .. import ssc_hook
        return ssc_hook(container, request)

    def test_it(self):

        class _ZopeResponse(object):
            counter = 0
            def __init__(self):
                self.cookies = {}
            def setCookie(self, name, **kw):
                self.cookies[name] = kw
                self.counter += 1

        container = object()
        request = _Request()
        response = request.RESPONSE = _ZopeResponse()
        self._setUpUtility()

        self._callFUT(container, request)

        self.assertTrue(response.set_cookie.im_func is
                        response.setCookie.im_func)
        self.assertEqual(request._lazy.keys(), ['SESSION'])
        session = request._lazy['SESSION']()

        session['foo'] = 'bar'
        self.assertEqual(response.cookies.keys(), [])

        session['baz'] = 'bam'
        self.assertEqual(response.cookies.keys(), [])

        self.assertEqual(response.counter, 0)  # cookie not set
        self.assertEqual(len(request._response_callbacks), 1)
        request._response_callbacks[0](request, response)
        self.assertEqual(response.counter, 1)
        self.assertEqual(response.cookies.keys(), ['COOKIE'])


class Test__emulate_pyramid_response_callback(_Base):

    def _callFUT(self, event):
        from .. import _emulate_pyramid_response_callback
        return _emulate_pyramid_response_callback(event)

    def test_wo_callbacks(self):
        event = _Event()
        self._callFUT(event)  # no exception for missing _response_callbacks

    def test_w_callbacks(self):
        event = _Event()
        _called = []
        def _callback(request, response):
            _called.append((request, response))
        event.request._response_callbacks = [_callback]
        self._callFUT(event)  # no exception for missing _response_callbacks
        self.assertEqual(_called, [(event.request, event.request.RESPONSE)])


class _Response(object):

    counter = 0

    def __init__(self):
        self.cookies = {}

    def set_cookie(self, name, **kw):
        self.cookies[name] = kw
        self.counter += 1


class _Request(object):

    def __init__(self, **kw):
        self.cookies = kw
        self._lazy = {}

    def set_lazy(self, name, factory):
        self._lazy[name] = factory

    def add_response_callback(self, callback):
        callbacks = getattr(self, '_response_callbacks', None)
        if callbacks is None:
            callbacks = self._response_callbacks = []
        callbacks.append(callback)


class _Event(object):
    def __init__(self):
        request = self.request = _Request()
        response = request.RESPONSE = _Response()
