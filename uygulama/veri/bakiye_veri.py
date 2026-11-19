from veri.veritabani import okuma_baglantisi, yazma_baglantisi, yordam_cagir


def bakiye_yukle(kullanici_id, tutar):
    return yordam_cagir("sp_bakiye_yukle", (kullanici_id, tutar))


def guncel_bakiye_getir(kullanici_id, kaynaktan=False):
    baglanti = yazma_baglantisi() if kaynaktan else okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT bakiye FROM kullanicilar WHERE id = %s",
                (kullanici_id,),
            )
            satir = imlec.fetchone()
            return float(satir["bakiye"]) if satir else 0.0
    finally:
        baglanti.close()


def bakiye_hareketleri_getir(kullanici_id):
    baglanti = okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT id, tur, tutar, rezervasyon_id, aciklama, "
                "DATE_FORMAT(olusturma, '%%Y-%%m-%%d %%H:%%i') AS olusturma "
                "FROM bakiye_hareketleri "
                "WHERE kullanici_id = %s "
                "ORDER BY olusturma DESC, id DESC",
                (kullanici_id,),
            )
            satirlar = imlec.fetchall()
            return [
                {
                    "id": s["id"],
                    "tur": s["tur"],
                    "tutar": float(s["tutar"]),
                    "rezervasyon_id": s["rezervasyon_id"],
                    "aciklama": s["aciklama"] or "",
                    "olusturma": s["olusturma"],
                }
                for s in satirlar
            ]
    finally:
        baglanti.close()
