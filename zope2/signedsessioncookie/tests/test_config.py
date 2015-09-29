import unittest


class SignedSessionCookieConfigTests(unittest.TestCase):

    def _getTargetClass(self):
        from ..config import SignedSessionCookieConfig
        return SignedSessionCookieConfig

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_class_conforms_to_ISignedSessionCookieConfig(self):
        from zope.interface.verify import verifyClass
        from ..interfaces import ISignedSessionCookieConfig
        verifyClass(ISignedSessionCookieConfig, self._getTargetClass())

    def test_instance_conforms_to_ISignedSessionCookieConfig(self):
        from zope.interface.verify import verifyObject
        from ..interfaces import ISignedSessionCookieConfig
        verifyObject(ISignedSessionCookieConfig,
                     self._makeOne('SECRET'))

    def test_ctor_minimal(self):
        config = self._makeOne('SECRET')
        self.assertEqual(config.secret, 'SECRET')
        self.assertEqual(config.salt, None)
        self.assertEqual(config.cookie_name, 'session')
        self.assertEqual(config.max_age, None)
        self.assertEqual(config.path, None)
        self.assertEqual(config.domain, None)
        self.assertEqual(config.secure, True)
        self.assertEqual(config.http_only, True)

    def test_ctor_explicit(self):
        config = self._makeOne('SECRET', 'SALT', 'COOKIE', 1234,
                               '/foo', 'www.example.com', False, False)
        self.assertEqual(config.secret, 'SECRET')
        self.assertEqual(config.salt, 'SALT')
        self.assertEqual(config.cookie_name, 'COOKIE')
        self.assertEqual(config.max_age, 1234)
        self.assertEqual(config.path, '/foo')
        self.assertEqual(config.domain, 'www.example.com')
        self.assertEqual(config.secure, False)
        self.assertEqual(config.http_only, False)

    def test_getCookieAttrs_defaults(self):
        config = self._makeOne('SECRET')
        self.assertEqual(config.getCookieAttrs(),
                         {'secret': 'SECRET',
                          'cookie_name': 'session',
                          'secure': True,
                          'httponly': True,
                         })

    def test_getCookieAttrs_explicit(self):
        config = self._makeOne('SECRET', 'SALT', 'COOKIE', 1234,
                               '/foo', 'www.example.com', False, False)
        self.assertEqual(config.getCookieAttrs(),
                         {'secret': 'SECRET',
                          'salt': 'SALT',
                          'cookie_name': 'COOKIE',
                          'max_age': 1234,
                          'path': '/foo',
                          'domain': 'www.example.com',
                          'secure': False,
                          'httponly': False,
                         })
