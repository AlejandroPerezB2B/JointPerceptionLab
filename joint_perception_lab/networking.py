"""TCP coordination for dyadic sessions. Not hardware clock synchronization."""
import hashlib
import json
import socket
import time

PORT = 48321


def order_digest(practice, main):
    sequence = [(phase, t['filename']) for phase, trials in [('practice', practice), ('main', main)] for t in trials]
    return hashlib.sha256(json.dumps(sequence, separators=(',', ':')).encode()).hexdigest()


class Peer:
    def __init__(self, sock, role):
        self.sock = sock
        self.sock.settimeout(120)
        self.reader = sock.makefile('rb')
        self.role = role

    @classmethod
    def connect(cls, role, address, port=PORT):
        if role == 'host':
            listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(('0.0.0.0', port))
            listener.listen(1)
            listener.settimeout(120)
            try:
                sock, _ = listener.accept()
            finally:
                listener.close()
        else:
            sock = socket.create_connection((address, port), timeout=20)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return cls(sock, role)

    def send(self, obj):
        self.sock.sendall((json.dumps(obj, separators=(',', ':'))+'\n').encode())

    def receive(self, kind):
        line = self.reader.readline()
        if not line:
            raise ConnectionError('Peer disconnected')
        msg = json.loads(line)
        if msg.get('type') == 'ABORT':
            raise KeyboardInterrupt('Remote participant aborted')
        if msg.get('type') != kind:
            raise RuntimeError(f'Protocol error: expected {kind}, received {msg}')
        return msg

    def handshake(self, digest, session_label):
        self.send({'type':'HELLO', 'digest':digest, 'session_label':session_label, 'protocol':1})
        other = self.receive('HELLO')
        if other['digest'] != digest or other['session_label'] != session_label or other.get('protocol') != 1:
            self.send({'type':'ABORT', 'reason':'Session label / trial sequence mismatch'})
            raise ValueError('Host and client have different session labels or trial orders')

    def barrier(self, phase, trial, stage):
        payload = {'type':'READY','phase':phase,'trial':trial,'stage':stage}
        self.send(payload)
        other = self.receive('READY')
        if any(other.get(k) != payload[k] for k in ('phase','trial','stage')):
            raise RuntimeError('Peer trial state mismatch')
        # Acknowledgement handshake reduces but does not eliminate onset jitter.
        if self.role == 'host':
            self.send({'type':'GO'})
            self.receive('ACK')
        else:
            self.receive('GO')
            self.send({'type':'ACK'})

    def exchange_response(self, phase, trial, response, rt_s):
        self.send({'type':'RESPONSE','phase':phase,'trial':trial,'response':response,'rt_s':rt_s})
        msg = self.receive('RESPONSE')
        if msg['phase'] != phase or msg['trial'] != trial:
            raise RuntimeError('Response trial mismatch')
        return msg

    def close(self):
        try:
            self.reader.close()
        finally:
            self.sock.close()
