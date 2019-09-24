#!/usr/bin/python3.7
from yarraclient import *

server = Server('YarraAda','mnt')
print(server.modes)
t = Task(server, 'BartSample', 'test.dat', 'SimpleProtocol', 999)
t.submit()