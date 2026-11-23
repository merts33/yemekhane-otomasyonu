from veri.veritabani import okuma_baglantisi, yordam_cagir


def rezervasyon_yap(kullanici_id, menu_id, porsiyon="tam"):
    return yordam_cagir("sp_rezervasyon_yap", (kullanici_id, menu_id, porsiyon))


def rezervasyon_iptal(kullanici_id, rezervasyon_id):
    return yordam_cagir("sp_rezervasyon_iptal", (kullanici_id, rezervasyon_id))


def kullanici_rezervasyonlari_getir(kullanici_id):
    baglanti = okuma_baglantisi()
    try:
        with baglanti.cursor() as imlec:
            imlec.execute(
                "SELECT r.id AS rezervasyon_id, r.menu_id, r.durum, r.porsiyon, r.ucret, "
                "DATE_FORMAT(m.tarih, '%%Y-%%m-%%d') AS tarih, "
                "yh.ad AS yemekhane, o.ad AS ogun, "
                "DATE_FORMAT(TIMESTAMP(m.tarih, o.son_saat), '%%Y-%%m-%%d %%H:%%i') AS rezervasyon_son, "
                "IF(r.durum = 'aktif' AND NOW() < TIMESTAMP(m.tarih, o.son_saat), 1, 0) AS iptal_edilebilir, "
                "IF(r.durum = 'kullanildi' AND d.id IS NULL, 1, 0) AS degerlendirilebilir, "
                "d.puan AS verilen_puan, d.yorum AS verilen_yorum "
                "FROM rezervasyonlar r "
                "JOIN menuler m ON m.id = r.menu_id "
                "JOIN yemekhaneler yh ON yh.id = m.yemekhane_id "
                "JOIN ogunler o ON o.id = m.ogun_id "
                "LEFT JOIN degerlendirmeler d ON d.menu_id = r.menu_id AND d.kullanici_id = r.kullanici_id "
                "WHERE r.kullanici_id = %s "
                "ORDER BY m.tarih DESC, o.sira DESC",
                (kullanici_id,),
            )
            satirlar = imlec.fetchall()
            sonuclar = []
            for s in satirlar:
                sonuclar.append(
                    {
                        "rezervasyon_id": s["rezervasyon_id"],
                        "menu_id": s["menu_id"],
                        "durum": s["durum"],
                        "porsiyon": s["porsiyon"],
                        "ucret": float(s["ucret"]),
                        "tarih": s["tarih"],
                        "yemekhane": s["yemekhane"],
                        "ogun": s["ogun"],
                        "rezervasyon_son": s["rezervasyon_son"],
                        "iptal_edilebilir": bool(s["iptal_edilebilir"]),
                        "degerlendirilebilir": bool(s["degerlendirilebilir"]),
                        "verilen_puan": s["verilen_puan"],
                        "verilen_yorum": s["verilen_yorum"],
                    }
                )
            return sonuclar
    finally:
        baglanti.close()
