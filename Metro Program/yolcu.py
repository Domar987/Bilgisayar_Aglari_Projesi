import client
import os

class Yolcu():
    def __init__(self,isim:str,sifre:str):
        self.ip='localhost'#os.environ["REMOTE_ADDR"]
        self.isim=isim
        self.sifre=sifre
        self.port=8080
    def bakiyeSorgu(self):
        client.connectToServer(f"{self.isim}-{self.sifre}-BS")
    def bakiyeYukle(self,miktar):
        client.connectToServer(f"{self.isim}-{self.sifre}-BY-{miktar}")

yolcu = Yolcu("aasd","1234")
yolcu.bakiyeSorgu()
yolcu.bakiyeYukle(100)