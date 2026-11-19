from veri.veritabani import okuma_baglantisi


def yemekhaneleri_getir():
    baglanti = okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT id, ad, konum, kapasite FROM yemekhaneler ORDER BY id"
            )
            return imlec.fetchall()
    finally:
        baglanti.close()


def ogunleri_getir():
    baglanti = okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT id, ad, sira, TIME_FORMAT(son_saat, '%%H:%%i') AS son_saat, "
                "TIME_FORMAT(servis_baslangic, '%%H:%%i') AS servis_baslangic, "
                "TIME_FORMAT(servis_bitis, '%%H:%%i') AS servis_bitis "
                "FROM ogunler ORDER BY sira"
            )
            return imlec.fetchall()
    finally:
        baglanti.close()


def yemekleri_getir():
    baglanti = okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT y.id, y.ad, y.kalori, y.vejetaryen, k.id AS kategori_id, k.ad AS kategori "
                "FROM yemekler y "
                "JOIN yemek_kategorileri k ON k.id = y.kategori_id "
                "ORDER BY k.sira, y.ad"
            )
            return imlec.fetchall()
    finally:
        baglanti.close()


def gunun_menusu_getir(yemekhane_id, ogun_id, tarih):
    baglanti = okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT menu_id, DATE_FORMAT(tarih, '%%Y-%%m-%%d') AS tarih, "
                "yemekhane_id, yemekhane, ogun_id, ogun, "
                "DATE_FORMAT(rezervasyon_son, '%%Y-%%m-%%d %%H:%%i') AS rezervasyon_son, "
                "ogrenci_fiyati, personel_fiyati, yemek_id, yemek, kategori, kalori, "
                "vejetaryen, alerjenler, alerjen_idler "
                "FROM v_menu_detay "
                "WHERE yemekhane_id = %s AND ogun_id = %s AND tarih = %s "
                "ORDER BY kategori_sira, yemek",
                (yemekhane_id, ogun_id, tarih),
            )
            satirlar = imlec.fetchall()
            if not satirlar:
                return None

            ilk = satirlar[0]
            menu_id = ilk["menu_id"]

            imlec.execute(
                "SELECT kapasite, rezerve, bos_yer, doluluk_yuzde, "
                "IF(NOW() >= rezervasyon_son, 1, 0) AS suresi_gecti "
                "FROM v_menu_doluluk WHERE menu_id = %s",
                (menu_id,),
            )
            doluluk = imlec.fetchone() or {}

            imlec.execute(
                "SELECT oy_sayisi, ortalama_puan FROM v_menu_puan WHERE menu_id = %s",
                (menu_id,),
            )
            puan = imlec.fetchone() or {}

            yemekler = []
            toplam_kalori = 0
            for s in satirlar:
                toplam_kalori += int(s["kalori"])
                yemekler.append(
                    {
                        "yemek_id": s["yemek_id"],
                        "ad": s["yemek"],
                        "kategori": s["kategori"],
                        "kalori": int(s["kalori"]),
                        "vejetaryen": bool(s["vejetaryen"]),
                        "alerjenler": s["alerjenler"] or "",
                    }
                )

            return {
                "menu_id": menu_id,
                "tarih": ilk["tarih"],
                "yemekhane_id": ilk["yemekhane_id"],
                "yemekhane": ilk["yemekhane"],
                "ogun_id": ilk["ogun_id"],
                "ogun": ilk["ogun"],
                "rezervasyon_son": ilk["rezervasyon_son"],
                "ogrenci_fiyati": float(ilk["ogrenci_fiyati"]),
                "personel_fiyati": float(ilk["personel_fiyati"]),
                "kapasite": int(doluluk.get("kapasite", 0)),
                "rezerve": int(doluluk.get("rezerve", 0)),
                "bos_yer": int(doluluk.get("bos_yer", 0)),
                "suresi_gecti": bool(doluluk.get("suresi_gecti", 0)),
                "oy_sayisi": int(puan.get("oy_sayisi", 0)),
                "ortalama_puan": (
                    float(puan["ortalama_puan"])
                    if puan.get("ortalama_puan") is not None
                    else None
                ),
                "toplam_kalori": toplam_kalori,
                "yemekler": yemekler,
            }
    finally:
        baglanti.close()


def haftalik_menuler_getir(yemekhane_id, baslangic, bitis, kullanici_id, rol):
    baglanti = okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT m.id AS menu_id, DATE_FORMAT(m.tarih, '%%Y-%%m-%%d') AS tarih, "
                "m.yemekhane_id, yh.ad AS yemekhane, m.ogun_id, o.ad AS ogun, "
                "m.ogrenci_fiyati, m.personel_fiyati, "
                "d.kapasite, d.rezerve, d.bos_yer, "
                "DATE_FORMAT(d.rezervasyon_son, '%%Y-%%m-%%d %%H:%%i') AS rezervasyon_son, "
                "IF(NOW() >= d.rezervasyon_son, 1, 0) AS suresi_gecti, "
                "p.oy_sayisi, p.ortalama_puan, "
                "r.id AS rezervasyon_id, r.durum AS rezervasyon_durumu "
                "FROM menuler m "
                "JOIN yemekhaneler yh ON yh.id = m.yemekhane_id "
                "JOIN ogunler o ON o.id = m.ogun_id "
                "JOIN v_menu_doluluk d ON d.menu_id = m.id "
                "JOIN v_menu_puan p ON p.menu_id = m.id "
                "LEFT JOIN rezervasyonlar r ON r.menu_id = m.id AND r.kullanici_id = %s "
                "WHERE m.yemekhane_id = %s AND m.tarih BETWEEN %s AND %s "
                "ORDER BY m.tarih, o.sira",
                (kullanici_id, yemekhane_id, baslangic, bitis),
            )
            satirlar = imlec.fetchall()
            sonuclar = []
            for s in satirlar:
                fiyat = s["ogrenci_fiyati"] if rol == "ogrenci" else s["personel_fiyati"]
                sonuclar.append(
                    {
                        "menu_id": s["menu_id"],
                        "tarih": s["tarih"],
                        "yemekhane_id": s["yemekhane_id"],
                        "yemekhane": s["yemekhane"],
                        "ogun_id": s["ogun_id"],
                        "ogun": s["ogun"],
                        "fiyat": float(fiyat),
                        "kapasite": int(s["kapasite"]),
                        "rezerve": int(s["rezerve"]),
                        "bos_yer": int(s["bos_yer"]),
                        "rezervasyon_son": s["rezervasyon_son"],
                        "suresi_gecti": bool(s["suresi_gecti"]),
                        "oy_sayisi": int(s["oy_sayisi"]),
                        "ortalama_puan": (
                            float(s["ortalama_puan"])
                            if s["ortalama_puan"] is not None
                            else None
                        ),
                        "rezervasyon_id": s["rezervasyon_id"],
                        "rezervasyon_durumu": s["rezervasyon_durumu"],
                    }
                )
            return sonuclar
    finally:
        baglanti.close()
