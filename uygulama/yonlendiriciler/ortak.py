from functools import wraps
from flask import g, jsonify, request
from veri.onbellek import oturum_getir


def giris_gerekli(fonksiyon):
    @wraps(fonksiyon)
    def sarmalayici(*args, **kwargs):
        token = request.cookies.get("oturum_token")
        oturum = oturum_getir(token)
        if not oturum:
            return jsonify({"hata": "Oturum açmanız gerekiyor."}), 401
        g.kullanici_id = oturum["kullanici_id"]
        g.rol = oturum["rol"]
        g.oturum_token = token
        return fonksiyon(*args, **kwargs)

    return sarmalayici


def yonetici_gerekli(fonksiyon):
    @wraps(fonksiyon)
    def sarmalayici(*args, **kwargs):
        token = request.cookies.get("oturum_token")
        oturum = oturum_getir(token)
        if not oturum:
            return jsonify({"hata": "Oturum açmanız gerekiyor."}), 401
        if oturum.get("rol") != "yonetici":
            return jsonify({"hata": "Bu işlem için yönetici yetkisi gerekir."}), 403
        g.kullanici_id = oturum["kullanici_id"]
        g.rol = oturum["rol"]
        g.oturum_token = token
        return fonksiyon(*args, **kwargs)

    return sarmalayici
