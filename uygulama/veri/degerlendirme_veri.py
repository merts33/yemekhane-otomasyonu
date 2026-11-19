import pymysql
from veri.veritabani import IsKuraliHatasi, okuma_baglantisi, yazma_baglantisi


def degerlendirme_ekle(kullanici_id, menu_id, puan, yorum):
    baglanti = yazma_baglantisi(otomatik_onay=True)
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT id FROM rezervasyonlar "
                "WHERE kullanici_id = %s AND menu_id = %s AND durum = 'kullanildi'",
                (kullanici_id, menu_id),
            )
            if not imlec.fetchone():
                raise IsKuraliHatasi("Yalnızca kullandığınız menüleri değerlendirebilirsiniz.")

            imlec.execute(
                "INSERT INTO degerlendirmeler (kullanici_id, menu_id, puan, yorum) "
                "VALUES (%s, %s, %s, %s)",
                (kullanici_id, menu_id, puan, yorum),
            )
            return imlec.lastrowid
    except pymysql.MySQLError as hata:
        hata_kodu = hata.args[0] if hata.args else 0
        if hata_kodu == 1062:
            raise IsKuraliHatasi("Bu menüyü zaten değerlendirdiniz.")
        if hata_kodu == 3819:
            raise IsKuraliHatasi("Puan 1 ile 5 arasında olmalıdır.")
        raise
    finally:
        baglanti.close()


def kullanici_degerlendirmeleri_getir(kullanici_id):
    baglanti = okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT d.id, d.menu_id, d.puan, d.yorum, "
                "DATE_FORMAT(d.olusturma, '%%Y-%%m-%%d %%H:%%i') AS olusturma, "
                "DATE_FORMAT(m.tarih, '%%Y-%%m-%%d') AS tarih, "
                "yh.ad AS yemekhane, o.ad AS ogun "
                "FROM degerlendirmeler d "
                "JOIN menuler m ON m.id = d.menu_id "
                "JOIN yemekhaneler yh ON yh.id = m.yemekhane_id "
                "JOIN ogunler o ON o.id = m.ogun_id "
                "WHERE d.kullanici_id = %s "
                "ORDER BY d.olusturma DESC",
                (kullanici_id,),
            )
            return imlec.fetchall()
    finally:
        baglanti.close()
