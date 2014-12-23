__author__ = 'linh'
import sys
import os
import pickle
import traceback
import shutil
import time
import xmlrpclib
import zipfile

from twisted.web import xmlrpc
from twisted.web import server
from twisted.python import log

from lib.Utility import Utility

class StationConsole(xmlrpc.XMLRPC):
    """
    Console used to control master PC
    """
    def __init__(self, host='localhost', port=1000, info={}):
        self.allowNone = True
        self.useDateTime = True
        self.allowedMethods = True
        self._port = port
        self._host = host
        self._info = info

    def xmlrpc_ping(self, **kargs):
        """
        Get list of available test plans
        """
        pass

    def xmlrpc_run_test_case(self, info={}):
        print info
        print self._info
        return (True,)

def main():
    from twisted.internet import reactor
    log.startLogging(sys.stdout)
    r = SlaveConsole('localhost', 1000)
    reactor.listenTCP(1000, server.Site(r))
    reactor.run()

if __name__ == '__main__':
    main()
