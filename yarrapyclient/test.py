#!/usr/bin/python3.7
from yarraclient import *

server = Server('YarraAda','xdglpdcdap002.nyumc.org')
t = Task(server, 'BartSample', 'test.dat', 'SimpleProtocol', 999)
t.submit()