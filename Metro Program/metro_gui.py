#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Istanbul Metro - Akilli Ulasim Sistemi
Socket entegrasyonlu masaustu GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import io, math, time, socket, threading, os
from PIL import Image, ImageTk, ImageDraw

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

BG_IMAGE_CANDIDATES = [
    "kiz_kulesi.jpeg", "kiz_kulesi.jpg", "kiz_kulesi.png",
    "background.jpg", "background.png",
]

ARAMA_KLASORLERI = [
    SCRIPT_DIR, os.getcwd(),
    os.path.expanduser("~"),
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Downloads"),
]

GORSEL_UZANTILARI = {".jpeg", ".jpg", ".png", ".bmp", ".webp"}


def gorsel_yolu_bul():
    for klasor in ARAMA_KLASORLERI:
        for isim in BG_IMAGE_CANDIDATES:
            tam_yol = os.path.join(klasor, isim)
            if os.path.isfile(tam_yol):
                return tam_yol
    for klasor in ARAMA_KLASORLERI:
        if not os.path.isdir(klasor):
            continue
        try:
            dosyalar = os.listdir(klasor)
        except PermissionError:
            continue
        resimler = [f for f in dosyalar if os.path.splitext(f)[1].lower() in GORSEL_UZANTILARI]
        oncelikli = [f for f in resimler if f.lower().startswith(("kiz", "kız", "k"))]
        secilen = oncelikli[0] if oncelikli else (resimler[0] if resimler else None)
        if secilen:
            return os.path.join(klasor, secilen)
    return None


# ─────────────────────────────────────────────────────
#  SOCKET CLIENT - DÜZELTILDI
# ─────────────────────────────────────────────────────
SERVER_HOST = "localhost"
SERVER_PORT = 8080


def socket_gonder(msg: str, timeout: float = 3.0) -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((SERVER_HOST, SERVER_PORT))
        s.sendall(msg.encode())
        data = s.recv(4096)
        s.close()
        return data.decode().strip()
    except ConnectionRefusedError:
        return "HATA:Sunucuya_baglanilmadi"
    except socket.timeout:
        return "HATA:Zaman_asimi"
    except Exception as e:
        return f"HATA:{e}"


def cmd_bakiye_sorgu(isim, sifre):
    return socket_gonder(f"{isim}-{sifre}-BS")


def cmd_bakiye_yukle(isim, sifre, miktar):
    return socket_gonder(f"{isim}-{sifre}-BY-{miktar}")


def cmd_menu_iste(isim, sifre):
    return socket_gonder(f"{isim}-{sifre}-M")


def cmd_tren_hiz(tren_id, hiz):
    return socket_gonder(f"{tren_id}-HG-{hiz}")


def cmd_tren_konum(tren_id, durak):
    return socket_gonder(f"{tren_id}-HI-{durak}")


# ─────────────────────────────────────────────────────
#  YEREL KULLANICI VERITABANI
# ─────────────────────────────────────────────────────
YEREL_KULLANICILAR = {
    "aasd": {"sifre": "1234", "ad_soyad": "Ali Aslan", "email": "ali@metro.ist", "bakiye": 125.0, "kart": "4821-7390"},
    "admin": {"sifre": "admin", "ad_soyad": "Admin Kullanici", "email": "admin@metro.ist", "bakiye": 500.0,
              "kart": "0000-0001"},
}

# ─────────────────────────────────────────────────────
#  ISTASYONLAR - BOĞAZ DÜZELTMESİ
#  Boğaz x=348-398 arasında. Duraklar bu bölgeden kaçırıldı.
# ─────────────────────────────────────────────────────
ISTASYONLAR = [
    # M1 - Kırmızı hat (Havalimanı → Yenikapı) - sol taraf, Boğaz altında
    {"id": "m1s1", "isim": "Havalimani", "hat": "M1", "renk": "#c0392b", "x": 55, "y": 520, "lat": 40.976,
     "lon": 28.814, "km": 0, "sefer": 4, "yog": "Yogun", "fac": ["Asansor", "Engelli", "Otopark", "Bagaj"],
     "aktarma": []},
    {"id": "m1s2", "isim": "Sefakoy", "hat": "M1", "renk": "#c0392b", "x": 118, "y": 520, "lat": 40.998, "lon": 28.830,
     "km": 4.2, "sefer": 6, "yog": "Orta", "fac": ["Asansor", "Engelli"], "aktarma": []},
    {"id": "m1s3", "isim": "Bahcelievler", "hat": "M1", "renk": "#c0392b", "x": 183, "y": 478, "lat": 41.002,
     "lon": 28.843, "km": 8.1, "sefer": 8, "yog": "Az", "fac": ["Asansor"], "aktarma": []},
    {"id": "m1s4", "isim": "Merter", "hat": "M1", "renk": "#c0392b", "x": 248, "y": 438, "lat": 41.003, "lon": 28.875,
     "km": 11.4, "sefer": 5, "yog": "Cok Yogun", "fac": ["Asansor", "Engelli", "Bufe"], "aktarma": ["M3"]},
    {"id": "m1s5", "isim": "Yenibosna", "hat": "M1", "renk": "#c0392b", "x": 308, "y": 398, "lat": 41.006,
     "lon": 28.896, "km": 14.7, "sefer": 3, "yog": "Orta", "fac": ["Asansor", "Engelli"], "aktarma": []},
    # Yenikapı: Boğazın soluna alındı (x=330, Boğaz 348-398 arası)
    {"id": "m1s6", "isim": "Yenikapi", "hat": "M1", "renk": "#c0392b", "x": 330, "y": 375, "lat": 41.004, "lon": 28.951,
     "km": 18.3, "sefer": 7, "yog": "Cok Yogun", "fac": ["Asansor", "Engelli", "AVM", "Bufe"], "aktarma": ["M2"]},

    # M2 - Mavi hat (Hacıosman → Haliç) - ağırlıklı sol+Boğaz sol
    {"id": "m2s1", "isim": "Haciosman", "hat": "M2", "renk": "#2471a3", "x": 80, "y": 58, "lat": 41.112, "lon": 29.030,
     "km": 0, "sefer": 9, "yog": "Az", "fac": ["Asansor", "Otopark"], "aktarma": []},
    {"id": "m2s2", "isim": "Darussafaka", "hat": "M2", "renk": "#2471a3", "x": 80, "y": 133, "lat": 41.105,
     "lon": 29.026, "km": 2.8, "sefer": 5, "yog": "Orta", "fac": ["Asansor", "Engelli"], "aktarma": []},
    {"id": "m2s3", "isim": "Ataturk Oto.", "hat": "M2", "renk": "#2471a3", "x": 130, "y": 188, "lat": 41.097,
     "lon": 29.023, "km": 5.2, "sefer": 4, "yog": "Orta", "fac": ["Asansor", "Engelli", "Otopark"], "aktarma": ["M3"]},
    {"id": "m2s4", "isim": "4.Levent", "hat": "M2", "renk": "#2471a3", "x": 210, "y": 238, "lat": 41.082, "lon": 29.013,
     "km": 9.0, "sefer": 3, "yog": "Yogun", "fac": ["Asansor", "Engelli", "Bufe"], "aktarma": []},
    {"id": "m2s5", "isim": "Levent", "hat": "M2", "renk": "#2471a3", "x": 290, "y": 275, "lat": 41.076, "lon": 29.010,
     "km": 11.8, "sefer": 6, "yog": "Yogun", "fac": ["Asansor", "Engelli", "AVM"], "aktarma": []},
    # Gayrettepe: Boğazın soluna (x=332)
    {"id": "m2s6", "isim": "Gayrettepe", "hat": "M2", "renk": "#2471a3", "x": 332, "y": 295, "lat": 41.068,
     "lon": 29.001, "km": 14.5, "sefer": 4, "yog": "Cok Yogun", "fac": ["Asansor", "Engelli", "Bufe"], "aktarma": []},
    # Şişli: Boğazın soluna (x=332)
    {"id": "m2s7", "isim": "Sisli", "hat": "M2", "renk": "#2471a3", "x": 332, "y": 318, "lat": 41.061, "lon": 28.987,
     "km": 17.1, "sefer": 5, "yog": "Yogun", "fac": ["Asansor", "Engelli", "AVM"], "aktarma": []},
    # Taksim: Boğazın sağına (x=420) - Taksim Avrupa yakasında ama Boğaz çizgisi sağında gösterilecek
    {"id": "m2s8", "isim": "Taksim", "hat": "M2", "renk": "#2471a3", "x": 420, "y": 295, "lat": 41.037, "lon": 28.985,
     "km": 19.8, "sefer": 2, "yog": "Cok Yogun", "fac": ["Asansor", "Engelli", "Bufe", "Danisma"], "aktarma": []},
    {"id": "m2s9", "isim": "Osmanbey", "hat": "M2", "renk": "#2471a3", "x": 490, "y": 258, "lat": 41.047, "lon": 28.998,
     "km": 21.3, "sefer": 7, "yog": "Orta", "fac": ["Asansor", "Engelli"], "aktarma": []},
    {"id": "m2s10", "isim": "Sishane", "hat": "M2", "renk": "#2471a3", "x": 555, "y": 218, "lat": 41.028, "lon": 28.972,
     "km": 23.0, "sefer": 5, "yog": "Orta", "fac": ["Asansor", "Engelli", "Bufe"], "aktarma": []},
    {"id": "m2s11", "isim": "Halic", "hat": "M2", "renk": "#2471a3", "x": 618, "y": 188, "lat": 41.032, "lon": 28.952,
     "km": 25.5, "sefer": 6, "yog": "Az", "fac": ["Asansor", "Engelli"], "aktarma": []},

    # M3 - Yeşil hat (Kirazlı → Bağcılar) - tamamen sol
    {"id": "m3s1", "isim": "Kirazli", "hat": "M3", "renk": "#1e8449", "x": 130, "y": 272, "lat": 41.054, "lon": 28.800,
     "km": 0, "sefer": 8, "yog": "Az", "fac": ["Asansor", "Otopark"], "aktarma": []},
    {"id": "m3s2", "isim": "Bagcilar M.", "hat": "M3", "renk": "#1e8449", "x": 135, "y": 358, "lat": 41.044,
     "lon": 28.820, "km": 3.5, "sefer": 4, "yog": "Orta", "fac": ["Asansor", "Engelli"], "aktarma": []},
    {"id": "m3s3", "isim": "Gungoren", "hat": "M3", "renk": "#1e8449", "x": 150, "y": 448, "lat": 41.028, "lon": 28.843,
     "km": 6.8, "sefer": 6, "yog": "Orta", "fac": ["Asansor", "Engelli", "Bufe"], "aktarma": []},
    {"id": "m3s4", "isim": "Bagcilar", "hat": "M3", "renk": "#1e8449", "x": 170, "y": 540, "lat": 41.009, "lon": 28.836,
     "km": 9.2, "sefer": 9, "yog": "Az", "fac": ["Asansor"], "aktarma": []},

    # M4 - Turuncu hat (Kadıköy → Göztepe) - Boğazın SAĞINDA (Anadolu yakası)
    {"id": "m4s1", "isim": "Kadikoy", "hat": "M4", "renk": "#d35400", "x": 455, "y": 355, "lat": 40.990, "lon": 29.028,
     "km": 0, "sefer": 3, "yog": "Cok Yogun", "fac": ["Asansor", "Engelli", "AVM", "Bufe", "Danisma"], "aktarma": []},
    {"id": "m4s2", "isim": "Ayrilik Cesmesi", "hat": "M4", "renk": "#d35400", "x": 480, "y": 420, "lat": 41.000,
     "lon": 29.055, "km": 2.1, "sefer": 5, "yog": "Yogun", "fac": ["Asansor", "Engelli", "Bufe"], "aktarma": ["M5"]},
    {"id": "m4s3", "isim": "Unalan", "hat": "M4", "renk": "#d35400", "x": 492, "y": 485, "lat": 41.008, "lon": 29.070,
     "km": 4.5, "sefer": 7, "yog": "Orta", "fac": ["Asansor", "Engelli"], "aktarma": []},
    {"id": "m4s4", "isim": "Goztepe", "hat": "M4", "renk": "#d35400", "x": 505, "y": 555, "lat": 41.014, "lon": 29.087,
     "km": 7.0, "sefer": 4, "yog": "Orta", "fac": ["Asansor", "Engelli", "Otopark"], "aktarma": []},

    # M5 - Mor hat (Üsküdar → Altunizade) - Boğazın SAĞINDA (Anadolu yakası)
    {"id": "m5s1", "isim": "Uskudar", "hat": "M5", "renk": "#7d3c98", "x": 523, "y": 320, "lat": 41.023, "lon": 29.015,
     "km": 0, "sefer": 5, "yog": "Yogun", "fac": ["Asansor", "Engelli", "Bufe", "Danisma"], "aktarma": []},
    {"id": "m5s2", "isim": "Fistikhagaci", "hat": "M5", "renk": "#7d3c98", "x": 558, "y": 382, "lat": 41.012,
     "lon": 29.042, "km": 2.4, "sefer": 8, "yog": "Az", "fac": ["Asansor", "Engelli"], "aktarma": []},
    {"id": "m5s3", "isim": "Baglarbasi", "hat": "M5", "renk": "#7d3c98", "x": 578, "y": 455, "lat": 41.003,
     "lon": 29.054, "km": 4.8, "sefer": 6, "yog": "Orta", "fac": ["Asansor", "Engelli", "Bufe"], "aktarma": []},
    {"id": "m5s4", "isim": "Altunizade", "hat": "M5", "renk": "#7d3c98", "x": 590, "y": 530, "lat": 40.994,
     "lon": 29.065, "km": 7.3, "sefer": 4, "yog": "Orta", "fac": ["Asansor", "Engelli", "Otopark"], "aktarma": []},
]

# Hat çizgi koordinatları da güncellendi
HAT_CIZGILERI = {
    "M1": {"renk": "#c0392b", "pts": [(55, 520), (118, 520), (183, 478), (248, 438), (308, 398), (330, 375)]},
    "M2": {"renk": "#2471a3",
           "pts": [(80, 58), (80, 133), (130, 188), (210, 238), (290, 275), (332, 295), (332, 318), (420, 295),
                   (490, 258), (555, 218), (618, 188)]},
    "M3": {"renk": "#1e8449", "pts": [(130, 188), (130, 272), (135, 358), (150, 448), (170, 540)]},
    "M4": {"renk": "#d35400", "pts": [(420, 295), (455, 355), (480, 420), (492, 485), (505, 555)]},
    "M5": {"renk": "#7d3c98", "pts": [(420, 295), (523, 320), (558, 382), (578, 455), (590, 530)]},
}

HAT_RENKLERI = {"M1": "#c0392b", "M2": "#2471a3", "M3": "#1e8449", "M4": "#d35400", "M5": "#7d3c98"}
YOG_RENK = {"Az": "#27ae60", "Orta": "#f39c12", "Yogun": "#e67e22", "Cok Yogun": "#c0392b"}

BG = "#07091a"
GOLD = "#c9a84c"
GOLD_L = "#e8c96d"
GOLD_D = "#6a5420"
TEXT = "#f0ead6"
TEXT_M = "#9a8f7a"
PANEL = "#0d1120"
CARD = "#111628"
SEP_C = "#1e2540"
GREEN = "#27ae60"
RED = "#c0392b"


def haversine(la1, lo1, la2, lo2):
    R = 6371
    dlat = math.radians(la2 - la1);
    dlon = math.radians(lo2 - lo1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def sep_line(parent):
    tk.Frame(parent, bg=GOLD_D, height=1).pack(fill="x", padx=12, pady=5)


def _bg_gorsel_yukle(genislik=920, yukseklik=590):
    yol = gorsel_yolu_bul()
    if yol:
        try:
            img = Image.open(yol).convert("RGB").resize((genislik, yukseklik), Image.LANCZOS)
        except Exception:
            img = _fallback_bg(genislik, yukseklik)
    else:
        img = _fallback_bg(genislik, yukseklik)

    overlay = Image.new("RGB", (genislik, yukseklik), (5, 8, 22))
    img = Image.blend(img, overlay, 0.45)

    mask = Image.new("RGBA", (genislik, yukseklik), (0, 0, 0, 0))
    draw = ImageDraw.Draw(mask)
    for i in range(420):
        a = int(210 * (i / 420))
        draw.rectangle([genislik - 420 + i, 0, genislik - 420 + i + 1, yukseklik], fill=(5, 8, 22, a))

    result = Image.alpha_composite(img.convert("RGBA"), mask).convert("RGB")
    return ImageTk.PhotoImage(result)


def _fallback_bg(genislik, yukseklik):
    img = Image.new("RGB", (genislik, yukseklik), (5, 8, 22))
    draw = ImageDraw.Draw(img)
    for y in range(yukseklik):
        r = int(5 + 15 * (y / yukseklik))
        g = int(8 + 10 * (y / yukseklik))
        b = int(22 + 30 * (y / yukseklik))
        draw.line([(0, y), (genislik, y)], fill=(r, g, b))
    draw.ellipse([100, 350, 400, 600], fill=(8, 15, 35))
    return img


# ══════════════════════════════════════════════════════
#  KAYIT EKRANI
# ══════════════════════════════════════════════════════
class KayitEkrani(tk.Toplevel):
    def __init__(self, master, on_kayit):
        super().__init__(master)
        self.on_kayit = on_kayit
        self.title("Istanbul Metro - Yeni Hesap Olustur")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()
        self._olustur()

    def _olustur(self):
        # Başlık
        ust = tk.Frame(self, bg="#0c1022")
        ust.pack(fill="x", pady=0)

        tk.Label(ust, text="YENİ HESAP OLUŞTUR", bg="#0c1022",
                 fg=GOLD_L, font=("Georgia", 14, "bold")).pack(pady=(22, 4))
        tk.Label(ust, text="Istanbul Metro IstanbulKart sistemi", bg="#0c1022",
                 fg=TEXT_M, font=("Helvetica", 9)).pack(pady=(0, 14))
        tk.Frame(ust, bg=GOLD_D, height=1).pack(fill="x", padx=24)

        # Form
        frm = tk.Frame(self, bg=BG)
        frm.pack(fill="both", expand=True, padx=36, pady=18)

        self.v_kul = tk.StringVar()
        self.v_sifre = tk.StringVar()
        self.v_sifre2 = tk.StringVar()
        self.v_isim = tk.StringVar()
        self.v_email = tk.StringVar()
        self.v_bakiye = tk.StringVar(value="50")

        alanlar = [
            ("KULLANICI ADI *", self.v_kul, None),
            ("ŞİFRE *", self.v_sifre, "*"),
            ("ŞİFRE TEKRAR *", self.v_sifre2, "*"),
            ("AD SOYAD *", self.v_isim, None),
            ("E-POSTA", self.v_email, None),
            ("BAŞLANGIÇ BAKİYESİ (TL)", self.v_bakiye, None),
        ]

        for lbl, var, show in alanlar:
            tk.Label(frm, text=lbl, bg=BG, fg=GOLD_D,
                     font=("Helvetica", 8)).pack(anchor="w", pady=(6, 2))
            e = tk.Entry(frm, textvariable=var, bg="#111a30", fg=TEXT,
                         insertbackground=GOLD, relief="flat", font=("Helvetica", 11),
                         highlightthickness=1, highlightcolor=GOLD,
                         highlightbackground=GOLD_D, bd=7)
            if show:
                e.configure(show=show)
            e.pack(fill="x", pady=(0, 2))

        self.hata_lbl = tk.Label(frm, text="", bg=BG,
                                 fg="#e74c3c", font=("Helvetica", 9), wraplength=380, justify="left")
        self.hata_lbl.pack(pady=6, anchor="w")

        # Butonlar
        btn_f = tk.Frame(frm, bg=BG)
        btn_f.pack(fill="x", pady=(4, 0))

        tk.Button(btn_f, text="HESAP OLUŞTUR",
                  bg=GOLD, fg=BG, font=("Helvetica", 11, "bold"),
                  relief="flat", cursor="hand2", pady=10,
                  activebackground=GOLD_L, activeforeground=BG,
                  command=self._kayit_yap).pack(fill="x")

        tk.Button(btn_f, text="Geri Dön",
                  bg=CARD, fg=TEXT_M, font=("Helvetica", 9),
                  relief="flat", cursor="hand2", pady=7,
                  activebackground="#1a2240", activeforeground=TEXT,
                  command=self.destroy).pack(fill="x", pady=(6, 0))

    def _kayit_yap(self):
        kul = self.v_kul.get().strip()
        sifre = self.v_sifre.get().strip()
        sifre2 = self.v_sifre2.get().strip()
        isim = self.v_isim.get().strip()
        email = self.v_email.get().strip()
        bakiye_str = self.v_bakiye.get().strip().replace(",", ".")

        # Doğrulama
        if not kul or not sifre or not isim:
            self.hata_lbl.config(text="⚠ Kullanici adi, sifre ve ad soyad zorunludur.")
            return
        if len(kul) < 3:
            self.hata_lbl.config(text="⚠ Kullanici adi en az 3 karakter olmalidir.")
            return
        if kul in YEREL_KULLANICILAR:
            self.hata_lbl.config(text="⚠ Bu kullanici adi zaten kayitli!")
            return
        if len(sifre) < 4:
            self.hata_lbl.config(text="⚠ Sifre en az 4 karakter olmalidir.")
            return
        if sifre != sifre2:
            self.hata_lbl.config(text="⚠ Sifreler eslesmiyor!")
            return
        try:
            bakiye = float(bakiye_str)
            if bakiye < 0:
                raise ValueError
        except ValueError:
            self.hata_lbl.config(text="⚠ Gecerli bir baslangic bakiyesi girin.")
            return

        # Kart numarası üret
        import random
        kart = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

        YEREL_KULLANICILAR[kul] = {
            "sifre": sifre,
            "ad_soyad": isim,
            "email": email,
            "bakiye": bakiye,
            "kart": kart,
        }

        # Server'a da kaydet (varsa)
        def _sunucu_kayit():
            # Sunucu kayıt protokolü yok ama bakiye sorgu ile test edilebilir
            yanit = socket_gonder(f"{kul}-{sifre}-BS")
            print(f"[Kayit] Sunucu yaniti: {yanit}")

        threading.Thread(target=_sunucu_kayit, daemon=True).start()

        self.destroy()
        self.on_kayit(kul)


# ══════════════════════════════════════════════════════
#  GİRİŞ EKRANI
# ══════════════════════════════════════════════════════
class LoginEkrani(tk.Toplevel):
    def __init__(self, master, on_login):
        super().__init__(master)
        self.on_login = on_login
        self.title("Istanbul Metro - Giris")
        self.geometry("920x590")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()
        self.bg_photo = _bg_gorsel_yukle(920, 590)
        self._olustur()

    def _olustur(self):
        cv = tk.Canvas(self, width=920, height=590, highlightthickness=0)
        cv.pack()
        cv.create_image(0, 0, image=self.bg_photo, anchor="nw")
        cv.create_text(230, 540, text="Kiz Kulesi - Istanbul Bogazi",
                       font=("Georgia", 10, "italic"), fill=GOLD, anchor="center")

        panel = tk.Frame(cv, bg="#0c1022", bd=0)
        cv.create_window(250, 295, window=panel, width=365, height=510)

        # Logo
        lf = tk.Frame(panel, bg="#0c1022")
        lf.pack(pady=(22, 0))
        lc = tk.Canvas(lf, width=54, height=54, bg="#0c1022", highlightthickness=0)
        lc.pack()
        lc.create_oval(2, 2, 52, 52, outline=GOLD, width=2, fill="#151f38")
        lc.create_rectangle(7, 22, 47, 32, fill=GOLD, outline="")
        lc.create_oval(10, 18, 22, 36, fill=GOLD, outline="")
        lc.create_oval(32, 18, 44, 36, fill=GOLD, outline="")
        lc.create_oval(13, 22, 19, 32, fill="#151f38", outline="")
        lc.create_oval(35, 22, 41, 32, fill="#151f38", outline="")
        lc.create_rectangle(25, 10, 29, 44, fill=GOLD, outline="")

        tk.Label(panel, text="ISTANBUL METRO", bg="#0c1022",
                 fg=GOLD_L, font=("Georgia", 15, "bold")).pack(pady=(10, 2))
        tk.Label(panel, text="AKILLI ULASIM SISTEMI", bg="#0c1022",
                 fg=TEXT_M, font=("Helvetica", 8)).pack()

        tk.Frame(panel, bg=GOLD_D, height=1).pack(fill="x", padx=28, pady=12)

        # Sunucu durum
        self.srv_frame = tk.Frame(panel, bg="#0c1022")
        self.srv_frame.pack(pady=(0, 6))
        self.srv_dot = tk.Canvas(self.srv_frame, width=10, height=10, bg="#0c1022", highlightthickness=0)
        self.srv_dot.pack(side="left", padx=(0, 6))
        self.srv_dot.create_oval(1, 1, 9, 9, fill="#888", outline="", tags="dot")
        self.srv_lbl = tk.Label(self.srv_frame, text="Sunucu kontrol ediliyor...",
                                bg="#0c1022", fg=TEXT_M, font=("Helvetica", 8))
        self.srv_lbl.pack(side="left")

        frm = tk.Frame(panel, bg="#0c1022")
        frm.pack(padx=32, fill="x")

        tk.Label(frm, text="KULLANICI ADI", bg="#0c1022", fg=GOLD_D, font=("Helvetica", 8)).pack(anchor="w")
        self.u_var = tk.StringVar(value="aasd")
        self._entry(frm, self.u_var).pack(fill="x", pady=(4, 10))

        tk.Label(frm, text="SIFRE", bg="#0c1022", fg=GOLD_D, font=("Helvetica", 8)).pack(anchor="w")
        self.p_var = tk.StringVar(value="1234")
        pe = self._entry(frm, self.p_var, show="*")
        pe.pack(fill="x", pady=(4, 4))
        pe.bind("<Return>", lambda e: self._giris())

        self.hata_lbl = tk.Label(frm, text="", bg="#0c1022", fg="#e74c3c", font=("Helvetica", 9))
        self.hata_lbl.pack(pady=4)

        tk.Button(frm, text="SISTEME GIRIS YAP",
                  bg=GOLD, fg=BG, font=("Helvetica", 11, "bold"),
                  relief="flat", cursor="hand2", pady=10,
                  activebackground=GOLD_L, activeforeground=BG,
                  command=self._giris).pack(fill="x", pady=4)

        tk.Frame(frm, bg=GOLD_D, height=1).pack(fill="x", pady=8)

        tk.Button(frm, text="✦  Yeni Hesap Olustur  ✦",
                  bg="#1a3a5c", fg="#5dade2", font=("Helvetica", 10, "bold"),
                  relief="flat", cursor="hand2", pady=9,
                  highlightthickness=1, highlightbackground="#2e6da4",
                  activebackground="#215a8a", activeforeground="#aee6ff",
                  command=self._kayit_ac).pack(fill="x", pady=2)

        tk.Label(panel, text="Demo: aasd / 1234",
                 bg="#0c1022", fg=TEXT_M, font=("Helvetica", 9)).pack(pady=(8, 0))

        threading.Thread(target=self._srv_kontrol, daemon=True).start()

    def _entry(self, p, var, show=None):
        e = tk.Entry(p, textvariable=var, bg="#111a30", fg=TEXT,
                     insertbackground=GOLD, relief="flat", font=("Helvetica", 12),
                     highlightthickness=1, highlightcolor=GOLD,
                     highlightbackground=GOLD_D, bd=8)
        if show:
            e.configure(show=show)
        return e

    def _kayit_ac(self):
        KayitEkrani(self, self._kayit_basarili)

    def _kayit_basarili(self, kul):
        self.u_var.set(kul)
        self.p_var.set(YEREL_KULLANICILAR[kul]["sifre"])
        self.hata_lbl.config(text=f"✓ Hesap olusturuldu! Giris yapiliyor...", fg=GREEN)
        self.after(800, self._giris)

    def _srv_kontrol(self):
        yanit = socket_gonder("PING", timeout=1.5)
        if yanit.startswith("HATA"):
            self.after(0, lambda: self._srv_durum(False))
        else:
            self.after(0, lambda: self._srv_durum(True))

    def _srv_durum(self, bagli):
        try:
            self.srv_dot.delete("dot")
            renk = GREEN if bagli else "#e74c3c"
            self.srv_dot.create_oval(1, 1, 9, 9, fill=renk, outline="", tags="dot")
            self.srv_lbl.config(
                text="Sunucu bagli" if bagli else "Sunucu kapali (yerel mod)",
                fg=GREEN if bagli else "#e67e22"
            )
        except Exception:
            pass

    def _giris(self):
        u = self.u_var.get().strip()
        p = self.p_var.get().strip()
        threading.Thread(target=self._giris_async, args=(u, p), daemon=True).start()

    def _giris_async(self, u, p):
        yanit = cmd_bakiye_sorgu(u, p)
        if yanit.startswith("HATA"):
            if u in YEREL_KULLANICILAR and YEREL_KULLANICILAR[u]["sifre"] == p:
                self.after(0, lambda: self._giris_basarili(u))
            else:
                self.after(0, lambda: self.hata_lbl.config(text="Kullanici adi veya sifre hatali!"))
        else:
            if u in YEREL_KULLANICILAR:
                try:
                    if ":" in yanit:
                        bak = float(yanit.split(":")[-1].strip().replace(" TL", ""))
                        YEREL_KULLANICILAR[u]["bakiye"] = bak
                except:
                    pass
            self.after(0, lambda: self._giris_basarili(u))

    def _giris_basarili(self, u):
        try:
            self.destroy()
            self.on_login(u)
        except Exception:
            pass


# ══════════════════════════════════════════════════════
#  ANA PENCERE
# ══════════════════════════════════════════════════════
class MetroApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Istanbul Metro - Akilli Ulasim Sistemi")
        self.root.geometry("1200x720")
        self.root.minsize(1000, 640)
        self.root.configure(bg=BG)

        self.aktif_kul = None
        self.secili_ist = None
        self.sunucu_bagli = False

        self.root.withdraw()
        LoginEkrani(self.root, self._giris_basarili)
        self.root.mainloop()

    def _giris_basarili(self, kullanici):
        self.aktif_kul = kullanici
        self.root.deiconify()
        # Önceki UI widget'larını temizle (çıkış → giriş döngüsünde çift pencere önlemi)
        for widget in self.root.winfo_children():
            widget.destroy()
        self._ui_olustur()
        self._profil_guncelle()
        self._harita_ciz()
        self._saat_baslat()
        self._sunucu_ping_dongu()

    def _ui_olustur(self):
        self._navbar()
        ana = tk.Frame(self.root, bg=BG)
        ana.pack(fill="both", expand=True)
        self._sol_panel(ana)
        tk.Frame(ana, bg=GOLD_D, width=1).pack(side="left", fill="y")
        self._harita_alani(ana)

    def _navbar(self):
        nb = tk.Frame(self.root, bg="#08091e", height=50)
        nb.pack(fill="x");
        nb.pack_propagate(False)

        sol = tk.Frame(nb, bg="#08091e")
        sol.pack(side="left", padx=18)
        self.canli_cv = tk.Canvas(sol, width=10, height=10, bg="#08091e", highlightthickness=0)
        self.canli_cv.pack(side="left", padx=(0, 8), pady=20)
        self.canli_cv.create_oval(1, 1, 9, 9, fill=GREEN, outline="", tags="dot")
        tk.Label(sol, text="ISTANBUL METRO", bg="#08091e",
                 fg=GOLD_L, font=("Georgia", 13, "bold")).pack(side="left")

        sag = tk.Frame(nb, bg="#08091e")
        sag.pack(side="right", padx=18)

        tk.Button(sag, text="Cikis", bg="#08091e", fg=TEXT_M,
                  relief="flat", cursor="hand2", font=("Helvetica", 10),
                  activeforeground=RED, command=self._cikis).pack(side="right", pady=12, padx=6)

        self.kul_lbl = tk.Label(sag, bg="#151d35", fg=TEXT,
                                font=("Helvetica", 10), padx=12, pady=5)
        self.kul_lbl.pack(side="right", padx=6, pady=10)

        self.saat_lbl = tk.Label(sag, bg="#08091e", fg=TEXT_M, font=("Courier", 10))
        self.saat_lbl.pack(side="right", padx=14)

        self.skt_frame = tk.Frame(sag, bg="#08091e")
        self.skt_frame.pack(side="right", padx=10)
        self.skt_dot = tk.Canvas(self.skt_frame, width=10, height=10, bg="#08091e", highlightthickness=0)
        self.skt_dot.pack(side="left", padx=(0, 5), pady=20)
        self.skt_dot.create_oval(1, 1, 9, 9, fill="#888", outline="", tags="dot")
        self.skt_lbl = tk.Label(self.skt_frame, text="Socket", bg="#08091e",
                                fg=TEXT_M, font=("Helvetica", 8))
        self.skt_lbl.pack(side="left")

    def _sol_panel(self, parent):
        self.sol = tk.Frame(parent, bg=PANEL, width=290)
        self.sol.pack(side="left", fill="y")
        self.sol.pack_propagate(False)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("M.TNotebook", background=PANEL, borderwidth=0, tabmargins=0)
        style.configure("M.TNotebook.Tab", background=PANEL, foreground=TEXT_M,
                        font=("Helvetica", 9), padding=[12, 7])
        style.map("M.TNotebook.Tab",
                  background=[("selected", CARD)], foreground=[("selected", GOLD)])

        self.nb = ttk.Notebook(self.sol, style="M.TNotebook")
        self.nb.pack(fill="both", expand=True)

        pf = tk.Frame(self.nb, bg=PANEL)
        self.nb.add(pf, text="  Profil  ")
        self._profil_sekmesi(pf)

        df = tk.Frame(self.nb, bg=PANEL)
        self.nb.add(df, text="  Durak  ")
        self.durak_frame = df
        self._durak_placeholder()

        sf = tk.Frame(self.nb, bg=PANEL)
        self.nb.add(sf, text="  Socket  ")
        self._socket_sekmesi(sf)

    def _profil_sekmesi(self, parent):
        ust = tk.Frame(parent, bg=PANEL)
        ust.pack(fill="x", padx=16, pady=14)
        self.av_cv = tk.Canvas(ust, width=50, height=50, bg=PANEL, highlightthickness=0)
        self.av_cv.pack(side="left")
        bilgi = tk.Frame(ust, bg=PANEL)
        bilgi.pack(side="left", padx=12)
        self.isim_lbl = tk.Label(bilgi, bg=PANEL, fg=TEXT, font=("Georgia", 12, "bold"))
        self.isim_lbl.pack(anchor="w")
        self.kart_lbl = tk.Label(bilgi, bg=PANEL, fg=TEXT_M, font=("Helvetica", 9))
        self.kart_lbl.pack(anchor="w")

        sep_line(parent)

        bkf = tk.Frame(parent, bg=CARD)
        bkf.pack(fill="x", padx=12, pady=6)
        bki = tk.Frame(bkf, bg=CARD)
        bki.pack(padx=14, pady=10)
        tk.Label(bki, text="KART BAKIYESi", bg=CARD, fg=TEXT_M, font=("Helvetica", 8)).pack(anchor="w")
        self.bakiye_lbl = tk.Label(bki, bg=CARD, fg=GOLD_L, font=("Georgia", 22, "bold"))
        self.bakiye_lbl.pack(anchor="w")
        tk.Label(bki, text="IstanbulKart", bg=CARD, fg=TEXT_M, font=("Helvetica", 8)).pack(anchor="w")

        ykf = tk.Frame(bki, bg=CARD)
        ykf.pack(fill="x", pady=(10, 0))
        self.yukle_var = tk.StringVar()
        tk.Entry(ykf, textvariable=self.yukle_var, bg="#0d1528", fg=TEXT,
                 insertbackground=GOLD, relief="flat", font=("Helvetica", 11),
                 highlightthickness=1, highlightbackground=GOLD_D,
                 highlightcolor=GOLD, width=8, bd=6).pack(side="left", padx=(0, 6))
        tk.Button(ykf, text="Yukle", bg=GOLD, fg=BG,
                  relief="flat", cursor="hand2", font=("Helvetica", 9, "bold"),
                  activebackground=GOLD_L, pady=5, padx=8,
                  command=self._bakiye_yukle).pack(side="left")

        self.yukle_msg = tk.Label(bki, text="", bg=CARD, fg=GREEN, font=("Helvetica", 8))
        self.yukle_msg.pack(anchor="w")

        sep_line(parent)

        tk.Label(parent, text="BILGILERI DUZENLE", bg=PANEL,
                 fg=GOLD_D, font=("Helvetica", 8)).pack(anchor="w", padx=16, pady=(6, 4))

        frm = tk.Frame(parent, bg=PANEL)
        frm.pack(fill="x", padx=16)

        self.efn = tk.StringVar()
        self.efm = tk.StringVar()
        self.eps = tk.StringVar()

        for lbl, var, show in [
            ("Ad Soyad", self.efn, None),
            ("E-Posta", self.efm, None),
            ("Yeni Sifre", self.eps, "*"),
        ]:
            tk.Label(frm, text=lbl, bg=PANEL, fg=TEXT_M, font=("Helvetica", 9)).pack(anchor="w", pady=(5, 2))
            e = tk.Entry(frm, textvariable=var, bg="#0d1528", fg=TEXT,
                         insertbackground=GOLD, relief="flat", font=("Helvetica", 11),
                         highlightthickness=1, highlightbackground=GOLD_D,
                         highlightcolor=GOLD, bd=6)
            if show: e.configure(show=show)
            e.pack(fill="x", pady=(0, 2))

        self.kaydet_msg = tk.Label(frm, text="", bg=PANEL, fg=GREEN, font=("Helvetica", 9))
        self.kaydet_msg.pack(pady=3)

        tk.Button(frm, text="Degisiklikleri Kaydet",
                  bg=CARD, fg=GOLD, relief="flat", cursor="hand2",
                  font=("Helvetica", 10), pady=7,
                  highlightthickness=1, highlightbackground=GOLD_D,
                  activebackground="#1a2240", activeforeground=GOLD_L,
                  command=self._profil_kaydet).pack(fill="x", pady=6)

    def _socket_sekmesi(self, parent):
        tk.Label(parent, text="SOCKET TEST KONSOLU", bg=PANEL,
                 fg=GOLD, font=("Helvetica", 9)).pack(anchor="w", padx=14, pady=(14, 6))

        # Log alanı + scrollbar
        log_f = tk.Frame(parent, bg="#060910")
        log_f.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        log_sb = tk.Scrollbar(log_f, orient="vertical",
                              bg=CARD, troughcolor="#060910", activebackground=GOLD,
                              width=10, bd=0, highlightthickness=0)
        log_sb.pack(side="right", fill="y")
        self.log_text = tk.Text(log_f, bg="#060910", fg="#00ff88",
                                font=("Courier", 9), relief="flat", state="disabled",
                                insertbackground=GREEN, wrap="word", bd=0,
                                yscrollcommand=log_sb.set)
        self.log_text.pack(fill="both", expand=True, padx=6, pady=6)
        log_sb.config(command=self.log_text.yview)

        sep_line(parent)

        tk.Label(parent, text="KOMUT GONDER", bg=PANEL,
                 fg=GOLD_D, font=("Helvetica", 8)).pack(anchor="w", padx=14, pady=(4, 4))

        cmd_f = tk.Frame(parent, bg=PANEL)
        cmd_f.pack(fill="x", padx=12, pady=(0, 6))
        self.cmd_var = tk.StringVar()
        cmd_entry = tk.Entry(cmd_f, textvariable=self.cmd_var, bg="#060910", fg=GREEN,
                             insertbackground=GREEN, relief="flat", font=("Courier", 10),
                             highlightthickness=1, highlightbackground=GOLD_D,
                             bd=6)
        cmd_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        cmd_entry.bind("<Return>", lambda e: self._manuel_komut())
        tk.Button(cmd_f, text="Gonder", bg=CARD, fg=GOLD,
                  relief="flat", cursor="hand2", font=("Helvetica", 9),
                  command=self._manuel_komut).pack(side="left")

        sep_line(parent)

        tk.Label(parent, text="HAZIR KOMUTLAR", bg=PANEL,
                 fg=GOLD_D, font=("Helvetica", 8)).pack(anchor="w", padx=14, pady=(4, 4))

        # Scrollable buton alanı
        btn_container = tk.Frame(parent, bg=PANEL)
        btn_container.pack(fill="both", padx=12, pady=(0, 6))

        btn_canvas = tk.Canvas(btn_container, bg=PANEL, highlightthickness=0,
                               height=160)
        btn_sb = tk.Scrollbar(btn_container, orient="vertical",
                              bg=CARD, troughcolor=PANEL, activebackground=GOLD,
                              width=10, bd=0, highlightthickness=0)
        btn_sb.pack(side="right", fill="y")
        btn_canvas.pack(side="left", fill="both", expand=True)
        btn_canvas.configure(yscrollcommand=btn_sb.set)
        btn_sb.configure(command=btn_canvas.yview)

        btnf = tk.Frame(btn_canvas, bg=PANEL)
        btn_canvas_win = btn_canvas.create_window((0, 0), window=btnf, anchor="nw")

        def _on_frame_config(e):
            btn_canvas.configure(scrollregion=btn_canvas.bbox("all"))

        def _on_canvas_resize(e):
            btn_canvas.itemconfig(btn_canvas_win, width=e.width)

        btnf.bind("<Configure>", _on_frame_config)
        btn_canvas.bind("<Configure>", _on_canvas_resize)

        # Fare tekerleği desteği
        def _on_mousewheel(e):
            btn_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        btn_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        u = self.aktif_kul
        p = YEREL_KULLANICILAR.get(u, {}).get("sifre", "")
        hazir = [
            ("Bakiye Sorgula", f"{u}-{p}-BS"),
            ("Bakiye Yukle +50", f"{u}-{p}-BY-50"),
            ("Menu Iste", f"{u}-{p}-M"),
            ("Tren Hizi Guncelle", "ASD.123-HG-85.5"),
            ("Tren Konum Sorgula", "ASD.123-HI-Taksim"),
            ("Ping", "PING"),
        ]
        for isim, cmd in hazir:
            tk.Button(btnf, text=isim, bg=CARD, fg=TEXT_M,
                      relief="flat", cursor="hand2", font=("Helvetica", 9),
                      pady=5, activeforeground=GOLD, activebackground="#1a2240",
                      anchor="w", padx=8,
                      command=lambda c=cmd: self._socket_gonder_log(c)
                      ).pack(fill="x", pady=2)

    def _socket_log(self, mesaj):
        try:
            self.log_text.configure(state="normal")
            ts = time.strftime("%H:%M:%S")
            self.log_text.insert("end", f"[{ts}] {mesaj}\n")
            self.log_text.configure(state="disabled")
            self.log_text.see("end")
        except Exception:
            pass

    def _socket_gonder_log(self, cmd):
        self._socket_log(f">>> {cmd}")

        def _is():
            yanit = socket_gonder(cmd)
            self.root.after(0, lambda y=yanit: self._socket_log(f"<<< {y}"))

        threading.Thread(target=_is, daemon=True).start()

    def _manuel_komut(self):
        cmd = self.cmd_var.get().strip()
        if cmd:
            self._socket_gonder_log(cmd)
            self.cmd_var.set("")

    def _durak_placeholder(self):
        for w in self.durak_frame.winfo_children():
            w.destroy()
        tk.Label(self.durak_frame,
                 text="<-- Haritadan bir\nduraga tiklayin",
                 bg=PANEL, fg=TEXT_M,
                 font=("Helvetica", 11), justify="center").pack(expand=True)

    def _harita_alani(self, parent):
        sag = tk.Frame(parent, bg=BG)
        sag.pack(side="left", fill="both", expand=True)

        ust = tk.Frame(sag, bg="#060818", height=30)
        ust.pack(fill="x");
        ust.pack_propagate(False)
        tk.Label(ust, text="ISTANBUL METRO AGI", bg="#060818",
                 fg=TEXT_M, font=("Helvetica", 8)).pack(side="left", padx=14, pady=7)

        self.harita = tk.Canvas(sag, bg="#050810", highlightthickness=0, cursor="crosshair")
        self.harita.pack(fill="both", expand=True)
        self.harita.bind("<Configure>", lambda e: self._harita_ciz())

        self._legend(sag)

    def _legend(self, parent):
        leg = tk.Frame(parent, bg="#09091f")
        leg.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        tk.Label(leg, text="METRO HATLARI", bg="#09091f",
                 fg=GOLD, font=("Helvetica", 8)).pack(anchor="w", padx=10, pady=(8, 4))
        for hat, (renk, isim) in {
            "M1": ("#c0392b", "Havalimani"), "M2": ("#2471a3", "Yenikapi-Haciosman"),
            "M3": ("#1e8449", "Kirazli-Bagcilar"), "M4": ("#d35400", "Kadikoy-Sabiha"),
            "M5": ("#7d3c98", "Uskudar-Cekmekoy")
        }.items():
            r = tk.Frame(leg, bg="#09091f")
            r.pack(fill="x", padx=10, pady=2)
            c = tk.Canvas(r, width=22, height=6, bg="#09091f", highlightthickness=0)
            c.pack(side="left", padx=(0, 6))
            c.create_rectangle(0, 1, 22, 5, fill=renk, outline="")
            tk.Label(r, text=f"{hat}  {isim}", bg="#09091f",
                     fg=TEXT_M, font=("Helvetica", 9)).pack(side="left")
        tk.Frame(leg, bg="#09091f", height=6).pack()

    def _harita_ciz(self):
        c = self.harita
        c.delete("all")
        W = c.winfo_width() or 880
        H = c.winfo_height() or 640

        for x in range(0, W, 80):
            c.create_line(x, 0, x, H, fill="#0b0f20", width=1)
        for y in range(0, H, 80):
            c.create_line(0, y, W, y, fill="#0b0f20", width=1)

        # Boğaz şeridi (x=348-398)
        c.create_rectangle(348, 0, 398, H, fill="#0b1c30", outline="")
        c.create_text(373, H // 2, text="B O G A Z",
                      fill="#1a3a5c", font=("Helvetica", 8), angle=90)

        for hat, bilgi in HAT_CIZGILERI.items():
            pts = bilgi["pts"]
            flat = [v for p in pts for v in p]
            c.create_line(*flat, fill=bilgi["renk"], width=5,
                          capstyle="round", joinstyle="round", smooth=False)

        for ist in ISTASYONLAR:
            self._ist_ciz(c, ist)

    def _ist_ciz(self, c, ist):
        x, y = ist["x"], ist["y"]
        r = 9
        secili = self.secili_ist and self.secili_ist["id"] == ist["id"]

        if ist["aktarma"]:
            c.create_oval(x - r - 5, y - r - 5, x + r + 5, y + r + 5,
                          outline=GOLD, width=1.5, dash=(4, 3))
        gr = r + 5 if secili else r + 3
        c.create_oval(x - gr, y - gr, x + gr, y + gr,
                      fill=ist["renk"], outline="", stipple="gray25")
        rr = r + 2 if secili else r
        c.create_oval(x - rr, y - rr, x + rr, y + rr,
                      fill="#050810", outline=ist["renk"], width=3 if secili else 2)
        dr = 5 if ist["aktarma"] else 3
        c.create_oval(x - dr, y - dr, x + dr, y + dr, fill=ist["renk"], outline="")
        if secili:
            c.create_oval(x - r - 3, y - r - 3, x + r + 3, y + r + 3, outline=GOLD_L, width=2)

        c.create_text(x + 14, y + 1, text=ist["isim"],
                      font=("Helvetica", 8, "bold" if secili else "normal"),
                      fill=GOLD_L if secili else "#b8a870", anchor="w")

        hit = c.create_oval(x - 14, y - 14, x + 14, y + 14, fill="", outline="")
        c.tag_bind(hit, "<Button-1>", lambda e, i=ist: self._ist_sec(i))
        c.tag_bind(hit, "<Enter>", lambda e: self.harita.config(cursor="hand2"))
        c.tag_bind(hit, "<Leave>", lambda e: self.harita.config(cursor="crosshair"))

    def _ist_sec(self, ist):
        self.secili_ist = ist
        self._harita_ciz()
        self._durak_bilgi_goster(ist)
        self.nb.select(1)
        threading.Thread(
            target=lambda: self._socket_log(
                f"Durak secildi: {ist['isim']} | Socket: {socket_gonder('PING', 1.0)}"
            ), daemon=True
        ).start()

    def _durak_bilgi_goster(self, ist):
        for w in self.durak_frame.winfo_children():
            w.destroy()

        bf = tk.Frame(self.durak_frame, bg=PANEL)
        bf.pack(fill="x", padx=14, pady=12)
        tk.Frame(bf, bg=ist["renk"], width=4).pack(side="left", fill="y", padx=(0, 10))
        bi = tk.Frame(bf, bg=PANEL)
        bi.pack(side="left")
        tk.Label(bi, text=ist["isim"], bg=PANEL, fg=TEXT,
                 font=("Georgia", 14, "bold")).pack(anchor="w")
        tk.Label(bi, text=f"{ist['hat']} Hatti", bg=PANEL,
                 fg=ist["renk"], font=("Helvetica", 9)).pack(anchor="w")

        sep_line(self.durak_frame)

        kart = tk.Frame(self.durak_frame, bg=CARD)
        kart.pack(fill="x", padx=12, pady=4)

        d = haversine(41.0370, 28.9850, ist["lat"], ist["lon"])
        dist_s = f"{int(d * 1000)} m" if d < 1 else f"{d:.1f} km"
        yc = YOG_RENK.get(ist["yog"], TEXT_M)

        rows = [
            ("Sonraki Sefer", f"{ist['sefer']} dakika", GREEN),
            ("Yogunluk", ist["yog"], yc),
            ("Konuma Uzaklik", dist_s, TEXT),
            ("Hat Mesafesi", f"{ist['km']} km", TEXT),
            ("Koordinat", f"{ist['lat']:.4f}N {ist['lon']:.4f}E", TEXT_M),
        ]
        for i, (k, v, vc) in enumerate(rows):
            bg2 = CARD if i % 2 == 0 else "#0f1525"
            r = tk.Frame(kart, bg=bg2)
            r.pack(fill="x")
            tk.Label(r, text=k, bg=bg2, fg=TEXT_M, font=("Helvetica", 9),
                     width=15, anchor="w").pack(side="left", padx=10, pady=6)
            tk.Label(r, text=v, bg=bg2, fg=vc,
                     font=("Helvetica", 9, "bold"), anchor="w").pack(side="left")

        if ist["aktarma"]:
            sep_line(self.durak_frame)
            af = tk.Frame(self.durak_frame, bg=PANEL)
            af.pack(fill="x", padx=14)
            tk.Label(af, text="AKTARMA", bg=PANEL, fg=GOLD_D,
                     font=("Helvetica", 8)).pack(anchor="w", pady=(4, 4))
            for a in ist["aktarma"]:
                ar = HAT_RENKLERI.get(a, GOLD)
                tk.Label(af, text=f"  {a} Hatti  ", bg=ar, fg="white",
                         font=("Helvetica", 9, "bold"), padx=4, pady=4
                         ).pack(side="left", padx=(0, 6))

        sep_line(self.durak_frame)
        ff = tk.Frame(self.durak_frame, bg=PANEL)
        ff.pack(fill="x", padx=14, pady=4)
        tk.Label(ff, text="IMKANLAR", bg=PANEL, fg=GOLD_D,
                 font=("Helvetica", 8)).pack(anchor="w", pady=(4, 6))
        gr = tk.Frame(ff, bg=PANEL)
        gr.pack(fill="x")
        for i, f in enumerate(ist["fac"]):
            tk.Label(gr, text=f"  {f}  ", bg="#0f1e35", fg="#5dade2",
                     font=("Helvetica", 8), pady=3,
                     highlightthickness=1, highlightbackground="#1a3a5c"
                     ).grid(row=i // 2, column=i % 2, padx=3, pady=3, sticky="w")

        sep_line(self.durak_frame)
        isim_kap = ist["isim"]
        tk.Button(self.durak_frame,
                  text=f"  {isim_kap} Duragina Rota Planla ->",
                  bg=CARD, fg=RED, relief="flat", cursor="hand2",
                  font=("Helvetica", 10), pady=9,
                  highlightthickness=1, highlightbackground="#5a1010",
                  command=lambda: messagebox.showinfo(
                      "Rota", f"{isim_kap} duragina rota hesaplaniyor...")
                  ).pack(fill="x", padx=12, pady=8)

    def _profil_guncelle(self):
        u = YEREL_KULLANICILAR.get(self.aktif_kul, {})
        ini = "".join(w[0] for w in u.get("ad_soyad", "??").split()).upper()[:2]
        self.av_cv.delete("all")
        self.av_cv.create_oval(1, 1, 49, 49, fill=GOLD, outline=GOLD_D, width=2)
        self.av_cv.create_text(25, 26, text=ini, fill=BG, font=("Georgia", 15, "bold"))
        self.isim_lbl.config(text=u.get("ad_soyad", ""))
        self.kart_lbl.config(text=f"Kart #{u.get('kart', '')}")
        self.bakiye_lbl.config(text=f"TL {u.get('bakiye', 0):.2f}")
        self.kul_lbl.config(text=f"  {ini}  {self.aktif_kul}  ")
        self.efn.set(u.get("ad_soyad", ""))
        self.efm.set(u.get("email", ""))

    def _profil_kaydet(self):
        u = YEREL_KULLANICILAR[self.aktif_kul]
        fn = self.efn.get().strip()
        fm = self.efm.get().strip()
        ps = self.eps.get().strip()
        if fn: u["ad_soyad"] = fn
        if fm: u["email"] = fm
        if ps: u["sifre"] = ps; self.eps.set("")
        self._profil_guncelle()
        self.kaydet_msg.config(text="Kaydedildi!", fg=GREEN)
        self.root.after(2500, lambda: self.kaydet_msg.config(text=""))

    def _bakiye_yukle(self):
        txt = self.yukle_var.get().strip().replace(",", ".")
        try:
            m = float(txt)
            if m < 10: raise ValueError
        except ValueError:
            self.yukle_msg.config(text="Min. 10 TL!", fg=RED)
            self.root.after(2000, lambda: self.yukle_msg.config(text=""))
            return
        u = self.aktif_kul
        p = YEREL_KULLANICILAR[u]["sifre"]
        self.yukle_var.set("")

        def _is():
            yanit = cmd_bakiye_yukle(u, p, m)
            self._socket_log(f"Bakiye yukle {m} TL -> {yanit}")
            YEREL_KULLANICILAR[u]["bakiye"] += m
            self.root.after(0, self._profil_guncelle)
            msg = "Yuklendi!" if not yanit.startswith("HATA") else "Yukle OK (yerel)"
            self.root.after(0, lambda: self.yukle_msg.config(text=msg, fg=GREEN))
            self.root.after(2500, lambda: self.yukle_msg.config(text=""))

        threading.Thread(target=_is, daemon=True).start()

    def _cikis(self):
        if messagebox.askyesno("Cikis", "Cikis yapmak istiyor musunuz?"):
            self.root.withdraw()
            self.aktif_kul = None
            LoginEkrani(self.root, self._giris_basarili)

    def _saat_baslat(self):
        self._saat_tick()

    def _saat_tick(self):
        try:
            self.saat_lbl.config(text=time.strftime("%H:%M:%S"))
            self.root.after(1000, self._saat_tick)
        except Exception:
            pass

    def _sunucu_ping_dongu(self):
        def _ping():
            yanit = socket_gonder("PING", 1.5)
            bagli = not yanit.startswith("HATA")
            self.sunucu_bagli = bagli
            try:
                renk = GREEN if bagli else "#e74c3c"
                self.skt_dot.delete("dot")
                self.skt_dot.create_oval(1, 1, 9, 9, fill=renk, outline="", tags="dot")
                self.skt_lbl.config(
                    text="Bagli" if bagli else "Kapali",
                    fg=GREEN if bagli else "#e74c3c"
                )
            except Exception:
                pass
            try:
                self.root.after(10000, self._sunucu_ping_dongu)
            except Exception:
                pass

        threading.Thread(target=_ping, daemon=True).start()


if __name__ == "__main__":
    MetroApp()