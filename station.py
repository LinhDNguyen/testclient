__author__ = 'Linh Nguyen'

import sys

from lib.SlaveConsole import SlaveConsole
from lib.Utility import Utility

from twisted.internet import reactor
from twisted.python import log
from twisted.web import server

log.startLogging(sys.stdout)
"""
An example of an XML-RPC server in Twisted.

Usage:
    $ python xmlrpc.py

An example session (assuming the server is running):

    >>> import xmlrpclib
    >>> s = xmlrpclib.Server('http://localhost:1000/')
    >>> s.run_test_case({'name': 'Test case 1'})
    >>> s.create_plan('Test1', 'TEST1')
    >>> s.active_plan('Test1', 'Test1 - s1')
    >>> s.echo("lala")
    ['lala']
    >>> s.echo("lala", 1)
    ['lala', 1]
    >>> s.echo("lala", 4)
    ['lala', 4]
    >>> s.echo("lala", 4, 3.4)
    ['lala', 4, 3.3999999999999999]
    >>> s.echo("lala", 4, [1, 2])
    ['lala', 4, [1, 2]]
"""
if __name__ == '__main__':
    configs = Utility.parse_xml_config('configs.xml')
    if 'specific_config' in configs.keys():
        configs['specific_config'] = Utility.parse_config(configs['specific_config'])

    r = SlaveConsole('localhost', 1000, configs)
    reactor.listenTCP(1000, server.Site(r))
    reactor.run()
