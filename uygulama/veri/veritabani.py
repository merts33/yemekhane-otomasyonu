import os
import pymysql


class IsKuraliHatasi(Exception):
    pass


def _baglanti_olustur(sunucu, otomatik_onay=True):
    return pymysql.connect(
        host=sunucu,
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ.get("DB_KULLANICI", "yemekhane_app"),
        password=os.environ.get("DB_SIFRE", "Uyg_2026"),
        database=os.environ.get("DB_ADI", "yemekhane"),
        charset="utf8mb4",
        autocommit=otomatik_onay,
        cursorclass=pymysql.cursors.DictCursor,
    )


def yazma_baglantisi(otomatik_onay=True):
    sunucu = os.environ.get("DB_YAZMA_HOST", "mysql-primary")
    return _baglanti_olustur(sunucu, otomatik_onay=otomatik_onay)


def okuma_baglantisi():
    sunucu = os.environ.get("DB_OKUMA_HOST", "mysql-replica")
    return _baglanti_olustur(sunucu, otomatik_onay=True)


def yordam_cagir(yordam_adi, parametreler):
    baglanti = yazma_baglantisi(otomatik_onay=True)
    try:
        with baglanti.cursor() as imlec:
            yer_tutucular = ", ".join(["%s"] * len(parametreler))
            sorgu = f"CALL {yordam_adi}({yer_tutucular})"
            imlec.execute(sorgu, parametreler)
            sonuc = imlec.fetchone()
            while imlec.nextset():
                pass
            return sonuc
    except pymysql.MySQLError as hata:
        hata_kodu = hata.args[0] if hata.args else 0
        if hata_kodu == 1644:
            raise IsKuraliHatasi(hata.args[1])
        if hata_kodu == 3819:
            raise IsKuraliHatasi("Girilen bilgiler kurallara uygun değil.")
        raise
    finally:
        baglanti.close()
