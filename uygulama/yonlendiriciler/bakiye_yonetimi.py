from flask import Blueprint, g, jsonify, request
from veri.bakiye_veri import (
    bakiye_hareketleri_getir,
    bakiye_yukle,
    guncel_bakiye_getir,
)
from yonlendiriciler.ortak import giris_gerekli

bakiye_bp = Blueprint("bakiye", __name__, url_prefix="/api")


@bakiye_bp.get("/bakiye")
@giris_gerekli
def bakiye_bilgisi():
    kullanici_id = g.kullanici_id
    kaynaktan = request.args.get("kaynaktan") == "1"
    bakiye = guncel_bakiye_getir(kullanici_id, kaynaktan=kaynaktan)
    hareketler = bakiye_hareketleri_getir(kullanici_id)
    return jsonify({"bakiye": bakiye, "hareketler": hareketler})


@bakiye_bp.post("/bakiye/yukle")
@giris_gerekli
def bakiye_yukleme():
    veri = request.get_json(silent=True) or {}
    tutar = veri.get("tutar")
    try:
        tutar_sayi = float(tutar)
    except (TypeError, ValueError):
        return jsonify({"hata": "Geçerli bir tutar giriniz."}), 400

    kullanici_id = g.kullanici_id
    sonuc = bakiye_yukle(kullanici_id, tutar_sayi)
    guncel_bakiye = guncel_bakiye_getir(kullanici_id, kaynaktan=True)
    return jsonify(
        {
            "mesaj": "Bakiye başarıyla yüklendi.",
            "hareket_id": sonuc["hareket_id"],
            "bakiye": guncel_bakiye,
        }
    )
