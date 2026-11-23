from flask import Blueprint, g, jsonify, request
from veri.bakiye_veri import guncel_bakiye_getir
from veri.rezervasyon_veri import (
    kullanici_rezervasyonlari_getir,
    rezervasyon_iptal,
    rezervasyon_yap,
)
from yonlendiriciler.ortak import giris_gerekli

rezervasyon_bp = Blueprint("rezervasyon", __name__, url_prefix="/api")


@rezervasyon_bp.get("/rezervasyonlar")
@giris_gerekli
def rezervasyonlari_listele():
    liste = kullanici_rezervasyonlari_getir(g.kullanici_id)
    return jsonify({"rezervasyonlar": liste})


@rezervasyon_bp.post("/rezervasyonlar")
@giris_gerekli
def rezervasyon_olustur():
    veri = request.get_json(silent=True) or {}
    menu_id = veri.get("menu_id")
    porsiyon = veri.get("porsiyon") or "tam"
    if not menu_id:
        return jsonify({"hata": "Menü seçimi zorunludur."}), 400

    kullanici_id = g.kullanici_id
    sonuc = rezervasyon_yap(kullanici_id, int(menu_id), porsiyon)
    guncel_bakiye = guncel_bakiye_getir(kullanici_id, kaynaktan=True)
    return (
        jsonify(
            {
                "mesaj": "Rezervasyon oluşturuldu.",
                "rezervasyon_id": sonuc["rezervasyon_id"],
                "porsiyon": sonuc["porsiyon"],
                "ucret": float(sonuc["ucret"]),
                "bakiye": guncel_bakiye,
            }
        ),
        201,
    )


@rezervasyon_bp.post("/rezervasyonlar/<int:rezervasyon_id>/iptal")
@giris_gerekli
def rezervasyon_iptal_et(rezervasyon_id):
    kullanici_id = g.kullanici_id
    sonuc = rezervasyon_iptal(kullanici_id, rezervasyon_id)
    guncel_bakiye = guncel_bakiye_getir(kullanici_id, kaynaktan=True)
    return jsonify(
        {
            "mesaj": "Rezervasyon iptal edildi ve ücret iade edildi.",
            "rezervasyon_id": sonuc["rezervasyon_id"],
            "iade": float(sonuc["iade"]),
            "bakiye": guncel_bakiye,
        }
    )
