import socket

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.bind(('127.0.0.1',8080))
s.listen()
sock,addr=s.accept()
while True:
    print(addr)
    data=sock.recv(1024)
    if not data:
        break
    sock.sendall(data)
sock.close()