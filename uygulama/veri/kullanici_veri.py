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


def alerjenleri_listele():
    baglanti = okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute("SELECT id, ad FROM alerjenler ORDER BY id")
            return imlec.fetchall()
    finally:
        baglanti.close()


def kullanici_alerjen_idleri_getir(kullanici_id, kaynaktan=False):
    baglanti = yazma_baglantisi() if kaynaktan else okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT alerjen_id FROM kullanici_alerjenleri WHERE kullanici_id = %s ORDER BY alerjen_id",
                (kullanici_id,),
            )
            return [s["alerjen_id"] for s in imlec.fetchall()]
    finally:
        baglanti.close()


def kullanici_alerjenlerini_guncelle(kullanici_id, alerjen_idler):
    baglanti = yazma_baglantisi(otomatik_onay=False)
    try:
        baglanti.begin()
        with baglanti.cursor() as imlec:
            imlec.execute(
                "DELETE FROM kullanici_alerjenleri WHERE kullanici_id = %s",
                (kullanici_id,),
            )
            for alerjen_id in alerjen_idler:
                imlec.execute(
                    "INSERT INTO kullanici_alerjenleri (kullanici_id, alerjen_id) VALUES (%s, %s)",
                    (kullanici_id, alerjen_id),
                )
        baglanti.commit()
    except Exception:
        baglanti.rollback()
        raise
    finally:
        baglanti.close()
