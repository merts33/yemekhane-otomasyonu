import os
from flask import Flask, jsonify
from veri.veritabani import IsKuraliHatasi
from yonlendiriciler.bakiye_yonetimi import bakiye_bp
from yonlendiriciler.degerlendirme_yonetimi import degerlendirme_bp
from yonlendiriciler.kimlik_yonetimi import kimlik_bp
from yonlendiriciler.menu_yonetimi import menu_bp
from yonlendiriciler.rezervasyon_yonetimi import rezervasyon_bp
from yonlendiriciler.yonetici_yonetimi import yonetici_bp

uygulama = Flask(__name__)
uygulama.secret_key = os.environ.get("OTURUM_ANAHTARI", "yemekhane_gizli_anahtar_2026")
uygulama.config["SESSION_COOKIE_HTTPONLY"] = True
uygulama.config["SESSION_COOKIE_SAMESITE"] = "Lax"

uygulama.register_blueprint(kimlik_bp)
uygulama.register_blueprint(menu_bp)
uygulama.register_blueprint(rezervasyon_bp)
uygulama.register_blueprint(bakiye_bp)
uygulama.register_blueprint(degerlendirme_bp)
uygulama.register_blueprint(yonetici_bp)


@uygulama.get("/api/")
def saglik():
    return jsonify({"durum": "calisiyor"})


@uygulama.errorhandler(IsKuraliHatasi)
def is_kurali_hatasi(hata):
    return jsonify({"hata": str(hata)}), 400


@uygulama.errorhandler(Exception)
def genel_hata(hata):
    return jsonify({"hata": "Sunucu hatası oluştu."}), 500
