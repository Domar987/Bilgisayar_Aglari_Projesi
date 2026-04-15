import socket

def connectToServer(msg:str):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(('localhost',8080))
    s.sendall(msg.encode())
    data=s.recv(1024)
    print(data.decode())
    s.close()