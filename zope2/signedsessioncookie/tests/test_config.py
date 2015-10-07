import unittest


class EncryptingPickleSerializerTests(unittest.TestCase):

    def _getTargetClass(self):
        from ..config import EncryptingPickleSerializer
        return EncryptingPickleSerializer

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor(self):
        SECRET = 'SEEKRIT'
        eps = self._makeOne(SECRET)
        self.assertEqual(eps.secret, SECRET)

    def test_dumps_short(self):
        from pyramid.compat import pickle
        from zope2.signedsessioncookie import config as MUT
        SECRET = 'SEEKRIT'
        IV = 'ABCDEFGH'
        APPSTRUCT = {}
        PICKLED = pickle.dumps(APPSTRUCT)
        with _Monkey(MUT,
                     _HAS_CRYPTO=True,
                     Blowfish=_Blowfish,
                     BLOCK_SIZE=8,
                     IV=IV,
                    ):
            eps = self._makeOne(SECRET)
            iv_encrypted = eps.dumps(APPSTRUCT)
            iv, encrypted = iv_encrypted[:8], iv_encrypted[8:]
            self.assertEqual(iv, IV)
            self.assertTrue(encrypted.startswith(PICKLED))
            self.assertEqual(len(encrypted) % 8, 0)

    def test_dumps_longer(self):
        from pyramid.compat import pickle
        from zope2.signedsessioncookie import config as MUT
        SECRET = 'SEEKRIT'
        IV = 'ABCDEFGH'
        APPSTRUCT = {'foo': 'bar', 'baz': 1}
        PICKLED = pickle.dumps(APPSTRUCT)
        with _Monkey(MUT,
                     _HAS_CRYPTO=True,
                     Blowfish=_Blowfish,
                     BLOCK_SIZE=8,
                     IV=IV,
                    ):
            eps = self._makeOne(SECRET)
            iv_encrypted = eps.dumps(APPSTRUCT)
            iv, encrypted = iv_encrypted[:8], iv_encrypted[8:]
            self.assertEqual(iv, IV)
            self.assertTrue(encrypted.startswith(PICKLED))
            self.assertEqual(len(encrypted) % 8, 0)

    def test_loads_short(self):
        from pyramid.compat import pickle
        from zope2.signedsessioncookie import config as MUT
        SECRET = 'SEEKRIT'
        IV = 'ABCDEFGH'
        APPSTRUCT = {}
        PICKLED = pickle.dumps(APPSTRUCT)
        PLEN = len(PICKLED) % 8
        with _Monkey(MUT,
                     _HAS_CRYPTO=True,
                     Blowfish=_Blowfish,
                     BLOCK_SIZE=8,
                    ):
            eps = self._makeOne(SECRET)
            loaded = eps.loads(IV + PICKLED + 'x' * PLEN)
            self.assertEqual(loaded, APPSTRUCT)

    def test_loads_longer(self):
        from pyramid.compat import pickle
        from zope2.signedsessioncookie import config as MUT
        SECRET = 'SEEKRIT'
        IV = 'ABCDEFGH'
        APPSTRUCT = {'foo': 'bar', 'baz': 1}
        PICKLED = pickle.dumps(APPSTRUCT)
        PLEN = len(PICKLED) % 8
        with _Monkey(MUT,
                     _HAS_CRYPTO=True,
                     Blowfish=_Blowfish,
                     BLOCK_SIZE=8,
                    ):
            eps = self._makeOne(SECRET)
            loaded = eps.loads(IV + PICKLED + 'x' * PLEN)
            self.assertEqual(loaded, APPSTRUCT)


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
        self.assertEqual(config.hash_algorithm, None)
        self.assertEqual(config.timeout, None)
        self.assertEqual(config.reissue_time, None)

    def test_ctor_explicit(self):
        config = self._makeOne('SECRET', 'SALT', 'COOKIE', 1234,
                               '/foo', 'www.example.com', False, False,
                               'md5', 2345, 234)
        self.assertEqual(config.secret, 'SECRET')
        self.assertEqual(config.salt, 'SALT')
        self.assertEqual(config.cookie_name, 'COOKIE')
        self.assertEqual(config.max_age, 1234)
        self.assertEqual(config.path, '/foo')
        self.assertEqual(config.domain, 'www.example.com')
        self.assertEqual(config.secure, False)
        self.assertEqual(config.http_only, False)
        self.assertEqual(config.hash_algorithm, 'md5')
        self.assertEqual(config.timeout, 2345)
        self.assertEqual(config.reissue_time, 234)

    def test_ctor_no_pycrypto(self):
        from zope2.signedsessioncookie import config as MUT
        with _Monkey(MUT, _HAS_CRYPTO=False):
            with self.assertRaises(ValueError):
                self._makeOne('SECRET', encrypt=True)

    def test_ctor_w_pycrypto(self):
        from zope2.signedsessioncookie import config as MUT
        with _Monkey(MUT, _HAS_CRYPTO=True):
            config = self._makeOne('SECRET', encrypt=True)
            self.assertTrue(config.encrypt)

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
                               '/foo', 'www.example.com', False, False,
                               'md5', 2345, 234)
        self.assertEqual(config.getCookieAttrs(),
                         {'secret': 'SECRET',
                          'salt': 'SALT',
                          'cookie_name': 'COOKIE',
                          'max_age': 1234,
                          'path': '/foo',
                          'domain': 'www.example.com',
                          'secure': False,
                          'httponly': False,
                          'hashalg': 'md5',
                          'timeout': 2345,
                          'reissue_time': 234,
                         })


class _Blowfish(object):

    MODE_CBC = 1

    @classmethod
    def new(cls, secret, mode, iv):
        return cls()

    def encrypt(self, plaintext):
        return plaintext

    def decrypt(self, encrypted):
        return encrypted


class _Monkey(object):
    # context-manager for replacing module names in the scope of a test.

    def __init__(self, module, **kw):
        self.module = module
        self.to_restore = dict([(key, getattr(module, key)) for key in kw])
        for key, value in kw.items():
            setattr(module, key, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key, value in self.to_restore.items():
            setattr(self.module, key, value)
