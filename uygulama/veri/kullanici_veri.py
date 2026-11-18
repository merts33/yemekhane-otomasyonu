from veri.veritabani import okuma_baglantisi, yazma_baglantisi


def eposta_ile_kullanici_bul(eposta):
    baglanti = okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT id, ad, soyad, eposta, sifre_hash, rol, ogrenci_no, bakiye, aktif "
                "FROM kullanicilar WHERE eposta = %s",
                (eposta,),
            )
            return imlec.fetchone()
    finally:
        baglanti.close()


def id_ile_kullanici_bul(kullanici_id, kaynaktan=False):
    baglanti = yazma_baglantisi() if kaynaktan else okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT id, ad, soyad, eposta, rol, ogrenci_no, bakiye, aktif "
                "FROM kullanicilar WHERE id = %s",
                (kullanici_id,),
            )
            return imlec.fetchone()
    finally:
        baglanti.close()
