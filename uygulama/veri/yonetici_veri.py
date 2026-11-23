import pymysql
from veri.onbellek import menu_onbellegi_sil
from veri.veritabani import IsKuraliHatasi, okuma_baglantisi, yazma_baglantisi


def menu_olustur(yemekhane_id, tarih, ogun_id, ogrenci_fiyati, personel_fiyati, yemek_idler):
    baglanti = yazma_baglantisi(otomatik_onay=False)
    try:
        baglanti.begin()
        with baglanti.cursor() as imlec:
            imlec.execute(
                "INSERT INTO menuler (yemekhane_id, tarih, ogun_id, ogrenci_fiyati, personel_fiyati) "
                "VALUES (%s, %s, %s, %s, %s)",
                (yemekhane_id, tarih, ogun_id, ogrenci_fiyati, personel_fiyati),
            )
            menu_id = imlec.lastrowid
            for yemek_id in yemek_idler:
                imlec.execute(
                    "INSERT INTO menu_yemekleri (menu_id, yemek_id) VALUES (%s, %s)",
                    (menu_id, yemek_id),
                )
        baglanti.commit()
        return menu_id
    except pymysql.MySQLError as hata:
        baglanti.rollback()
        hata_kodu = hata.args[0] if hata.args else 0
        if hata_kodu == 1062:
            raise IsKuraliHatasi("Bu yemekhane, tarih ve öğün için zaten bir menü mevcut.")
        if hata_kodu == 3819:
            raise IsKuraliHatasi("Fiyatlar negatif olamaz.")
        raise
    except Exception:
        baglanti.rollback()
        raise
    finally:
        baglanti.close()


def menu_guncelle(menu_id, ogrenci_fiyati, personel_fiyati, yemek_idler):
    baglanti = yazma_baglantisi(otomatik_onay=False)
    try:
        baglanti.begin()
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT yemekhane_id, DATE_FORMAT(tarih, '%%Y-%%m-%%d') AS tarih, ogun_id "
                "FROM menuler WHERE id = %s",
                (menu_id,),
            )
            menu_bilgi = imlec.fetchone()
            if not menu_bilgi:
                raise IsKuraliHatasi("Güncellenecek menü bulunamadı.")

            imlec.execute(
                "UPDATE menuler SET ogrenci_fiyati = %s, personel_fiyati = %s WHERE id = %s",
                (ogrenci_fiyati, personel_fiyati, menu_id),
            )
            imlec.execute("DELETE FROM menu_yemekleri WHERE menu_id = %s", (menu_id,))
            for yemek_id in yemek_idler:
                imlec.execute(
                    "INSERT INTO menu_yemekleri (menu_id, yemek_id) VALUES (%s, %s)",
                    (menu_id, yemek_id),
                )
        baglanti.commit()
        menu_onbellegi_sil(
            menu_bilgi["yemekhane_id"], menu_bilgi["tarih"], menu_bilgi["ogun_id"]
        )
    except pymysql.MySQLError as hata:
        baglanti.rollback()
        hata_kodu = hata.args[0] if hata.args else 0
        if hata_kodu == 3819:
            raise IsKuraliHatasi("Fiyatlar negatif olamaz.")
        raise
    except Exception:
        baglanti.rollback()
        raise
    finally:
        baglanti.close()


def menu_raporu_getir():
    baglanti = okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT d.menu_id, DATE_FORMAT(d.tarih, '%%Y-%%m-%%d') AS tarih, "
                "d.yemekhane_id, d.yemekhane, d.ogun_id, d.ogun, "
                "m.ogrenci_fiyati, m.personel_fiyati, "
                "d.kapasite, d.rezerve, d.bos_yer, d.doluluk_yuzde, "
                "p.oy_sayisi, p.ortalama_puan "
                "FROM v_menu_doluluk d "
                "JOIN menuler m ON m.id = d.menu_id "
                "JOIN v_menu_puan p ON p.menu_id = d.menu_id "
                "ORDER BY d.tarih DESC, d.yemekhane_id, d.ogun_id "
                "LIMIT 60"
            )
            satirlar = imlec.fetchall()
            return [
                {
                    "menu_id": s["menu_id"],
                    "tarih": s["tarih"],
                    "yemekhane_id": s["yemekhane_id"],
                    "yemekhane": s["yemekhane"],
                    "ogun_id": s["ogun_id"],
                    "ogun": s["ogun"],
                    "ogrenci_fiyati": float(s["ogrenci_fiyati"]),
                    "personel_fiyati": float(s["personel_fiyati"]),
                    "kapasite": int(s["kapasite"]),
                    "rezerve": int(s["rezerve"]),
                    "bos_yer": int(s["bos_yer"]),
                    "doluluk_yuzde": float(s["doluluk_yuzde"]),
                    "oy_sayisi": int(s["oy_sayisi"]),
                    "ortalama_puan": (
                        float(s["ortalama_puan"])
                        if s["ortalama_puan"] is not None
                        else None
                    ),
                }
                for s in satirlar
            ]
    finally:
        baglanti.close()


def menu_yemek_idleri_getir(menu_id):
    baglanti = okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT yemek_id FROM menu_yemekleri WHERE menu_id = %s",
                (menu_id,),
            )
            return [s["yemek_id"] for s in imlec.fetchall()]
    finally:
        baglanti.close()
