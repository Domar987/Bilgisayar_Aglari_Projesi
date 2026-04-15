import json
import socket

userspath = "usersdata.json"
fopen = open(userspath,"r")
udatabase = json.load(fopen)

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(('127.0.0.1',8080))

def getMsg():
    s.listen()
    sock,addr=s.accept()
    while True:
        print(addr)
        data=sock.recv(1024)
        if not data:
            break
        else:
            readMsg(sock,data.decode())
        #sock.sendall(data)
    sock.close()

def readMsg(sock,msg:str):
    msgicerik = msg.split("-")
    if msgicerik[2][0]=='B':
        if msgicerik[2][1]=='Y':
            miktar = eval(msgicerik[3])
        elif msgicerik[2][1]=='S':
            for i in udatabase:
                if i["isim"] == msgicerik[0] and i["sifre"] == msgicerik[1]:
                    sock.sendall("test")
    elif msgicerik[3][0]=='A':
        pass