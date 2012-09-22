import pwn, socket, basesock
import log
from consts import *

_DEFAULT_HANDLER_TIMEOUT = 10
_DEFAULT_HANDLER_BACKLOG = 10

class handler(basesock.basesock):
    def __init__(self, port = 0, fam = socket.AF_INET, typ = socket.SOCK_STREAM, sock_opts = [(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)], proto = 0, **kwargs):
        self.family = fam
        self.type = typ
        self.proto = proto
        self.listensock = None
        self.sock = None
        self.port = port
        self.sock_opts = sock_opts
        self.target = None
        self.debug = pwn.DEBUG
        self.timeout = kwargs.get('timeout', _DEFAULT_HANDLER_TIMEOUT)
        self.backlog = kwargs.get('backlog', _DEFAULT_HANDLER_BACKLOG)
        self.checked = kwargs.get('checked', True)
        self.start()

    def start(self):
        self.listensock = socket.socket(self.family, self.type, self.proto)

        for l,o,v in self.sock_opts:
            self.listensock.setsockopt(l,o,v)
        if self.timeout is not None:
            self.listensock.settimeout(self.timeout)
        self.listensock.bind(('', self.port))
        self.port = self.listensock.getsockname()[1]
        self.listensock.listen(self.backlog)
        log.info('Handler is waiting for connection on {%s}:%d\n' % (', '.join(i[1] for i in pwn.get_interfaces()), self.port))

    def stop(self):
        if self.listensock:
            self.listensock.close()
            self.listensock = None
            pwn.trace(' [+] Stopped handler on port %d\n' % self.port)
            self.port = None

    def wait_for_connection(self):
        if self.checked:
            try:
                self.sock, self.target = self.listensock.accept()
            except socket.timeout:
                log.failure('Handler on port %s timed out\n' % self.port)
                exit(PWN_PATCHED)
        else:
            self.sock, self.target = self.listensock.accept()
        log.success('Got connection on local port %d from %s:%d\n' % ((self.sock.getsockname()[1],) + self.target))

    def settimeout(self, n):
        self.timeout = n
        self.listensock.settimeout(n)
        self.sock.settimeout(n)
