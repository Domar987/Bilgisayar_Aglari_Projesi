import json
import socket

def getMsg():
    print("Dinleniyor...")
    s.listen()
    sock, addr = s.accept()
    while True:
        print(f"{addr} bağlandı")
        data = sock.recv(1024)
        if not data:
            break
        else:
            print("Mesaj alındı")
            readMsg(sock, data.decode())
    sock.close()

def readMsg(sock, msg: str):
    msgicerik = msg.strip().split("-")

    if msg.strip() == "PING":
        sock.sendall("Ping başarılı".encode())
        return

    if len(msgicerik) >= 3:
        if msgicerik[2][0] == 'B':
            if len(msgicerik[2]) > 1 and msgicerik[2][1] == 'Y':
                print("Bakiye yükleme isteği")
                for i in udatabase:
                    if i["isim"] == msgicerik[0] and i["sifre"] == msgicerik[1]:
                        i["bakiye"] += eval(msgicerik[3])
                        with open(userspath, "w") as fwrite:
                            json.dump(udatabase, fwrite, indent=4)
                        sock.sendall(
                            f"{msgicerik[3]} TL yüklendi\nYeni bakiye: {i['bakiye']} TL".encode()
                        )
                        return
                sock.sendall("HATA: Kullanici bulunamadi".encode())

            elif len(msgicerik[2]) > 1 and msgicerik[2][1] == 'S':
                print("Bakiye sorgu isteği")
                for i in udatabase:
                    if i["isim"] == msgicerik[0] and i["sifre"] == msgicerik[1]:
                        sock.sendall(f"Bakiye: {i['bakiye']} TL".encode())
                        return
                sock.sendall("HATA: Kullanici bulunamadi".encode())

        elif msgicerik[2][0] == 'M':
            print("Menü isteği")
            sock.sendall("Menü: BS=Bakiye Sorgula, BY=Bakiye Yukle, M=Menu".encode())

    elif len(msgicerik) >= 2 and msgicerik[1][0] == 'H':
        if len(msgicerik[1]) > 1 and msgicerik[1][1] == 'G':
            print("Hız güncelleme isteği")
            for i in tdatabase:
                if i["isim"] == msgicerik[0]:
                    i["hiz"] = eval(msgicerik[2])
                    with open(tpath, "w") as fwrite:
                        json.dump(tdatabase, fwrite, indent=4)
                    sock.sendall(
                        f"{msgicerik[2]}, {i['isim']} treninin yeni hızı olarak kaydedildi".encode()
                    )
                    return
            sock.sendall("HATA: Tren bulunamadi".encode())

        elif len(msgicerik[1]) > 1 and msgicerik[1][1] == 'I':
            print("Konum isteği")
            for i in tdatabase:
                if i["isim"] == msgicerik[0]:
                    hiz = i["hiz"]
                    durak = i["durak"]
                    sock.sendall(f"Tren: {i['isim']} | Hiz: {hiz} | Durak: {durak}".encode())
                    return
            sock.sendall("HATA: Tren bulunamadi".encode())
    else:
        sock.sendall("HATA: Gecersiz komut".encode())



userspath = "kullanicilar.json"
try:
    with open(userspath, "r") as ufread:
        udatabase = json.load(ufread)
except FileNotFoundError:
    udatabase = []
    with open(userspath, "w") as f:
        json.dump(udatabase, f, indent=4)

tpath = "trenler.json"
try:
    with open(tpath, "r") as tfread:
        tdatabase = json.load(tfread)
except FileNotFoundError:
    tdatabase = []
    with open(tpath, "w") as f:
        json.dump(tdatabase, f, indent=4)

ipath = "istasyonlar.json"
try:
    with open(ipath, "r") as ifread:
        idatabase = json.load(ifread)
except FileNotFoundError:
    idatabase = []


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('127.0.0.1', 8080))

print("Metro Server başlatıldı - 127.0.0.1:8080")

while True:
    getMsg()