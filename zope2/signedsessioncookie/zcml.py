from zope.component import provideUtility

from .config import SignedSessionCookieConfig


def _doConfigure(_secret, _salt, _cookie_name, _max_age, _path, _domain,
                 _secure, _http_only,
                 _hash_algorithm, _timeout, _reissue_time, _encrypt):

    config = SignedSessionCookieConfig(
        secret = _secret,
        salt = _salt,
        cookie_name = _cookie_name,
        max_age = _max_age,
        path = _path,
        domain = _domain,
        secure = _secure,
        http_only = _http_only,
        hash_algorithm = _hash_algorithm,
        timeout = _timeout,
        reissue_time = _reissue_time,
        encrypt = _encrypt,
        )

    provideUtility(config)


def configureSSC(context,
                 secret,
                 salt=None,
                 cookie_name='session',
                 max_age=None,
                 path='/',
                 domain=None,
                 secure=True,
                 http_only=True,
                 hash_algorithm=None,
                 timeout=None,
                 reissue_time=None,
                 encrypt=False,
                ):
    context.action(discriminator='configureSSC',
                   callable=_doConfigure,
                   args=(secret, salt, cookie_name, max_age, path, domain,
                         secure, http_only,
                         hash_algorithm, timeout, reissue_time, encrypt)
                   )
