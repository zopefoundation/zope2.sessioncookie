import struct

from pyramid.compat import pickle
from zope.interface import implementer

try:
    from Crypto import Random
except ImportError:
    _HAS_CRYPTO = False
else:
    _HAS_CRYPTO = True
    from Crypto.Cipher import Blowfish
    BLOCK_SIZE = Blowfish.block_size
    IV = Random.new().read(BLOCK_SIZE)

from .interfaces import ISignedSessionCookieConfig


class EncryptingPickleSerializer(object):

    def __init__(self, secret):
        self.secret = secret

    def loads(self, bstruct):
        iv, payload = bstruct[:BLOCK_SIZE], bstruct[BLOCK_SIZE:]
        cipher = Blowfish.new(self.secret, Blowfish.MODE_CBC, iv)
        payload = cipher.decrypt(payload)
        return pickle.loads(payload)

    def dumps(self, appstruct):
        pickled = pickle.dumps(appstruct)
        # For an explanation / example of the padding, see:
        # https://www.dlitz.net/software/pycrypto/api/current/\
        # Crypto.Cipher.Blowfish-module.html
        plen = BLOCK_SIZE - divmod(len(pickled), BLOCK_SIZE)[1]
        padding = struct.pack('b' * plen, *([plen] * plen))
        cipher = Blowfish.new(self.secret, Blowfish.MODE_CBC, IV)
        return IV + cipher.encrypt(pickled + padding)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.secret == other.secret


@implementer(ISignedSessionCookieConfig)
class SignedSessionCookieConfig(object):

    def __init__(self, 
                 secret,
                 salt=None,
                 cookie_name='session',
                 max_age=None,
                 path=None,
                 domain=None,
                 secure=True,
                 http_only=True,
                 hash_algorithm=None,
                 timeout=None,
                 reissue_time=None,
                 encrypt=False,
                ):
        self.secret = secret
        self.salt = salt
        self.cookie_name = cookie_name
        self.max_age = max_age
        self.path = path
        self.domain = domain
        self.secure = secure
        self.http_only = http_only
        self.hash_algorithm = hash_algorithm
        self.timeout = timeout
        self.reissue_time = reissue_time
        if encrypt and not _HAS_CRYPTO:
            raise ValueError('Install pycrypto!')
        self.encrypt = encrypt

    def getCookieAttrs(self):
        """-> dict for configuring the Pyramid session cookie class."""
        result = dict([(key, value) for key, value in self.__dict__.items()
                       if value is not None])
        if result.pop('encrypt'):
            result['serializer'] = EncryptingPickleSerializer(self.secret)
            if 'secret' in result:
                del result['secret']
            if 'salt' in result:
                del result['salt']
        result['httponly'] = result.pop('http_only')
        if 'hash_algorithm' in result:
            result['hashalg'] = result.pop('hash_algorithm')
        return result
