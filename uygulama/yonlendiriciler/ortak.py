from functools import wraps
from flask import jsonify, session


def giris_gerekli(fonksiyon):
    @wraps(fonksiyon)
    def sarmalayici(*args, **kwargs):
        if "kullanici_id" not in session:
            return jsonify({"hata": "Oturum açmanız gerekiyor."}), 401
        return fonksiyon(*args, **kwargs)

    return sarmalayici


def yonetici_gerekli(fonksiyon):
    @wraps(fonksiyon)
    def sarmalayici(*args, **kwargs):
        if "kullanici_id" not in session:
            return jsonify({"hata": "Oturum açmanız gerekiyor."}), 401
        if session.get("rol") != "yonetici":
            return jsonify({"hata": "Bu işlem için yönetici yetkisi gerekir."}), 403
        return fonksiyon(*args, **kwargs)

    return sarmalayici
