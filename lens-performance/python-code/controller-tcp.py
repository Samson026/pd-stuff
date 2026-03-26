import socket
from threading import Thread, Event
from queue import Queue
from websockets.server import serve
from websockets import ConnectionClosed


proxy_queue = Queue()
CLIENTS = set()
broadcast_port = 7654
recv_pd_port = 13002
ip = '0.0.0.0'

clients = []


def recv(stop: Event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = ('localhost', recv_pd_port)
    print(f'starting up on {server_address[0]} port {server_address[1]}')
    sock.bind(server_address)
    sock.listen(1)

    try:
        while not stop.is_set():
            print('waiting for a connection')
            connection, client_address = sock.accept()

            print('client connected to controller:', client_address)
            while not stop.is_set():
                data = connection.recv(16)
                proxy_queue.put(data)
                print(f'received {data}')
    except Exception as e:
        print(e)
        connection.close()

    finally:
        connection.close()


def send(stop: Event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, broadcast_port)
    print(f'starting up on {server_address[0]} port {server_address[1]}')

    try:
        sock.bind(server_address)
        sock.listen(5)
        
        while not stop.is_set():
            connection, client_address = sock.accept()
            print('client connected as sender:', client_address)
            clients.append(connection)
            print(len(clients))
    except Exception as e:
        print(e)

    for client in clients:
        client.close()
    
    sock.close()


def broadcast(stop: Event):
        while not stop.is_set():
            msg = proxy_queue.get()
            print(f'got message {msg}')
            print(len(clients))
            for client in clients:
                try:
                    client.send(msg)
                except:
                    client.close()
                    clients.remove(client)
                    print(f"removed client {client}")
                print(f"sending {msg}")


def main():
    stop = Event()
    re = Thread(target=recv, args=[stop], daemon=True)
    se = Thread(target=send, args=[stop], daemon=True)
    br = Thread(target=broadcast, args=[stop], daemon=True)
    re.start()
    se.start()
    br.start()
    re.join()
    stop.set()
    

if __name__ == '__main__':
    main()
