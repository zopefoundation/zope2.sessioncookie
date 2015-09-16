Implementation Notes
====================

- Clearing the existing ``__before_traverse__`` hook on the root:

.. code-block:: python

   root.session_data_manager.updateTraversalData(None)

- Setting the ``__before_traverse__`` hook on the root:

.. code-block:: python

  from ZPublisher.BeforeTraverse import registerBeforeTraverse
  registerBeforeTraverse(root, ssc_hook, 'zope2.signedsessioncookie', 50)

- Implementing the ``__before_traverse__`` hook:

.. code-block:: python

   from zope2.signedsessioncookie.factory import SessionFactory

   def ssc_hook(container, request):
       ssc_factory = SessionFactory(request)
       request.set_lazy('SESSION', ssc_factory)

- Implementing the SSC factory:

.. code-block:: python

   from zope.component import getUtility
   from zope2.signedsessioncookie.interfaces import IConfig
   from zope2.signedsessioncookie.sessoin import SignedCookieSession

   class SessionFactory(object):

        def __init__(self, request):
            self.request = request

        def __call__(self):
            config = getUtility(IConfig)
            return SignedCookieSession(config, request.RESPONSE)

- Implementing the session:

.. code-block:: python

   class SignedCookieSession(object):
       pass
