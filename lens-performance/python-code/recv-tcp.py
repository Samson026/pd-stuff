import socket
from threading import Thread, Event
from queue import Queue
from websockets.sync.client import connect


proxy_queue = Queue()
port = 7654
localport = 13001

def to_pd(stop: Event):
    while not stop.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            while not stop.is_set():
                msg = proxy_queue.get()
                
                sock.sendto(msg.to_bytes(2, byteorder='big'), ("localhost", localport))
        except Exception as e:
            print(e)
            sock.close()


def connect(stop: Event):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print("input ip:")
        ip = input()

        try:
            print(port)
            print(len(ip))
            print(ip)
            sock.connect((ip, port))
            print("connection successful...")
            while not stop.is_set():
                data = sock.recv(16)
                data = data.decode("utf-8")
                data = data.replace('\n', '').replace('\t','').replace('\r','').replace(';','')
                try:
                    data = int(float(data))
                    print(f"recv {data}")
                    proxy_queue.put(data)
                except Exception as e:
                    print(e)
            
            sock.close()
        except Exception as e:
            print(e)
        

def main():
    stop = Event()
    pd = Thread(target=to_pd, args=[stop], daemon=True)
    recv = Thread(target=connect, args=[stop], daemon=True)
    pd.start()
    recv.start()
    recv.join()

    stop.set()

main()
