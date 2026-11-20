from flask import Blueprint, jsonify, request, session
from veri.degerlendirme_veri import (
    degerlendirme_ekle,
    kullanici_degerlendirmeleri_getir,
)
from yonlendiriciler.ortak import giris_gerekli

degerlendirme_bp = Blueprint("degerlendirme", __name__, url_prefix="/api")


@degerlendirme_bp.get("/degerlendirmeler")
@giris_gerekli
def degerlendirmeleri_listele():
    liste = kullanici_degerlendirmeleri_getir(session["kullanici_id"])
    return jsonify({"degerlendirmeler": liste})


@degerlendirme_bp.post("/degerlendirmeler")
@giris_gerekli
def degerlendirme_olustur():
    veri = request.get_json(silent=True) or {}
    menu_id = veri.get("menu_id")
    puan = veri.get("puan")
    yorum = (veri.get("yorum") or "").strip()

    if not menu_id or puan is None:
        return jsonify({"hata": "Menü ve puan zorunludur."}), 400

    try:
        puan_sayi = int(puan)
    except (TypeError, ValueError):
        return jsonify({"hata": "Puan tam sayı olmalıdır."}), 400

    degerlendirme_id = degerlendirme_ekle(
        session["kullanici_id"], int(menu_id), puan_sayi, yorum
    )
    return (
        jsonify(
            {
                "mesaj": "Değerlendirmeniz kaydedildi.",
                "degerlendirme_id": degerlendirme_id,
            }
        ),
        201,
    )
