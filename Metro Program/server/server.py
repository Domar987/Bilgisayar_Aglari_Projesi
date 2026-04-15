import json
import socket


def getMsg():
    print("Dinleniyor...")
    s.listen()
    sock,addr=s.accept()
    while True:
        print(f"{addr} bağlandı")
        data=sock.recv(1024)
        if not data:
            break
        else:
            print("Mesaj alındı")
            readMsg(sock,data.decode())
        #sock.sendall(data)
    sock.close()

def readMsg(sock,msg:str):
    msgicerik = msg.split("-")
    if msgicerik[2][0]=='B':
        if msgicerik[2][1]=='Y':
            print("Bakiye yükleme isteği")
            for i in udatabase:
                if i["isim"] == msgicerik[0] and i["sifre"] == msgicerik[1]:
                    i["bakiye"] += eval(msgicerik[3])
                    fwrite = open(userspath,"w")
                    json.dump(udatabase,fwrite,indent=4)
                    sock.sendall(f"{msgicerik[3]} TL yüklendi\nYeni bakiye: {i["bakiye"]} TL".encode())
        elif msgicerik[2][1]=='S':
            print("Bakiye sorgu isteği")
            for i in udatabase:
                if i["isim"] == msgicerik[0] and i["sifre"] == msgicerik[1]:
                    sock.sendall(f"Bakiye: {i["bakiye"]} TL".encode())
    elif msgicerik[3][0]=='A':
        print("Bilinmeyen istek")
        pass

userspath = "usersdata.json"
fread = open(userspath,"r")
udatabase = json.load(fread)

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(('127.0.0.1',8080))

while True:
    getMsg()