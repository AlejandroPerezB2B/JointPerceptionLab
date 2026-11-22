import socket
import threading
from joint_perception_lab.networking import Peer, order_digest
from joint_perception_lab.timing import analyse_frame_log


def test_digest_ignores_paths():
    a = [{'filename':'S24L0.mp4', 'path':'C:/one/S24L0.mp4'}]
    b = [{'filename':'S24L0.mp4', 'path':'D:/two/S24L0.mp4'}]
    assert order_digest(a,a) == order_digest(b,b)
    assert order_digest(a,a) != order_digest([],a)


def test_frame_qc():
    r = analyse_frame_log([0,.033,.066,.12], [0,1,2,3],30,.01667)
    assert r['source_frame_updates']==4
    assert r['intervals_over_1_5_source_frames']==1
    assert r['source_frame_skips']==0


def test_peer_protocol():
    a,b=socket.socketpair()
    host,client=Peer(a,'host'),Peer(b,'client')
    out=[]
    def run_host():
        host.handshake('abc','session')
        host.barrier('practice',1,'pre_fixation')
        out.append(host.exchange_response('practice',1,'yes',.4))
    thread=threading.Thread(target=run_host)
    thread.start()
    client.handshake('abc','session')
    client.barrier('practice',1,'pre_fixation')
    got=client.exchange_response('practice',1,'no',.6)
    thread.join(timeout=3)
    assert not thread.is_alive()
    assert got['response']=='yes' and out[0]['response']=='no'
    host.close();client.close()
