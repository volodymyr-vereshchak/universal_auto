import socket
import threading
import os



UDP = 44300
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


def listen(sock: socket.socket):
    while True:
        msg = sock.recv(UDP)
        print('\r\r' + msg.decode('ascii') + '\n' + f'you: ', end='')


def connect(host: str = '127.0.0.1', port: int = 3000):

    sock.connect((host, port))

    threading.Thread(target=listen, args=(sock,), daemon=True).start()

    sock.send('__join'.encode('ascii'))

    while True:
        msg = input(f'you: ')
        sock.send(msg.encode('ascii'))


if __name__ == '__main__':
    os.system('clear')
    print('Welcome to chat!')
    connect()