import bcrypt
from flask import Blueprint, g, jsonify, make_response, request
from veri.kullanici_veri import eposta_ile_kullanici_bul, id_ile_kullanici_bul
from veri.onbellek import oturum_olustur, oturum_sil
from yonlendiriciler.ortak import giris_gerekli

kimlik_bp = Blueprint("kimlik", __name__, url_prefix="/api")


@kimlik_bp.post("/giris")
def giris():
    veri = request.get_json(silent=True) or {}
    eposta = (veri.get("eposta") or "").strip().lower()
    sifre = veri.get("sifre") or ""

    if not eposta or not sifre:
        return jsonify({"hata": "E-posta ve şifre zorunludur."}), 400

    kullanici = eposta_ile_kullanici_bul(eposta)
    if not kullanici:
        return jsonify({"hata": "E-posta veya şifre hatalı."}), 401

    if not kullanici["aktif"]:
        return jsonify({"hata": "Hesabınız pasif durumda."}), 403

    dogru_mu = bcrypt.checkpw(
        sifre.encode("utf-8"), kullanici["sifre_hash"].encode("utf-8")
    )
    if not dogru_mu:
        return jsonify({"hata": "E-posta veya şifre hatalı."}), 401

    token = oturum_olustur(kullanici["id"], kullanici["rol"])
    yanit = make_response(
        jsonify(
            {
                "kullanici": {
                    "id": kullanici["id"],
                    "ad": kullanici["ad"],
                    "soyad": kullanici["soyad"],
                    "eposta": kullanici["eposta"],
                    "rol": kullanici["rol"],
                    "ogrenci_no": kullanici["ogrenci_no"],
                    "bakiye": float(kullanici["bakiye"]),
                }
            }
        )
    )
    yanit.set_cookie("oturum_token", token, httponly=True, samesite="Lax")
    return yanit


@kimlik_bp.post("/cikis")
def cikis():
    token = request.cookies.get("oturum_token")
    oturum_sil(token)
    yanit = make_response(jsonify({"mesaj": "Çıkış yapıldı."}))
    yanit.delete_cookie("oturum_token")
    return yanit


@kimlik_bp.get("/ben")
@giris_gerekli
def ben():
    kaynaktan = request.args.get("kaynaktan") == "1"
    kullanici = id_ile_kullanici_bul(g.kullanici_id, kaynaktan=kaynaktan)
    if not kullanici:
        oturum_sil(g.oturum_token)
        return jsonify({"hata": "Kullanıcı bulunamadı."}), 401
    return jsonify(
        {
            "kullanici": {
                "id": kullanici["id"],
                "ad": kullanici["ad"],
                "soyad": kullanici["soyad"],
                "eposta": kullanici["eposta"],
                "rol": kullanici["rol"],
                "ogrenci_no": kullanici["ogrenci_no"],
                "bakiye": float(kullanici["bakiye"]),
            }
        }
    )
