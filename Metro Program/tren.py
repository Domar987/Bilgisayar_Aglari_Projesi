import random
import time

import client

class Tren():
    def __init__(self,isim:str,hiz:float, durak:str):
        self.ip='localhost'#os.environ["REMOTE_ADDR"]
        self.isim=isim
        self.hiz = hiz
        self.durak = durak
        self.port=8080
    def hizGonder(self):
        client.connectToServer(f"{self.isim}-HG-{self.hiz}")
    def konumIste(self):
        client.connectToServer(f"{self.isim}-HI-{self.durak}")

tren = Tren("ASD.123",random.randint(0,1000)/10.0)
while True:
    tren.hizGonder()
    time.sleep(5)