# Script to be run via 'zopectl run'.
#
# Installs the SSC as a '__before_traverse__' hook,, after first disabling
# the default '/session_data_manager'.
#

import transaction
from ZPublisher.BeforeTraverse import registerBeforeTraverse

from zope2.signedsessioncookie import ssc_hook

sdm = app._getOb('session_data_manager', None)
if sdm is not None:
    sdm.updateTraversalData(requestSessionName=None)

registerBeforeTraverse(app, ssc_hook, 'signedsessioncookie', 50)

print('Done!')
transaction.commit()
