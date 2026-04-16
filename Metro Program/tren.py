import random
import time

import client

class Tren():
    def __init__(self,isim:str,hiz:float):
        self.ip='localhost'#os.environ["REMOTE_ADDR"]
        self.isim=isim
        self.hiz = hiz
        self.port=8080
    def hizGonder(self):
        client.connectToServer(f"{self.isim}-HG-{self.hiz}")

tren = Tren("ASD.123",random.randint(0,1000)/10.0)
while True:
    tren.hizGonder()
    time.sleep(5)