from datetime import date, timedelta
from flask import Blueprint, g, jsonify, request
from veri.kullanici_veri import kullanici_alerjen_idleri_getir
from veri.menu_veri import (
    gunun_menusu_getir,
    haftalik_menuler_getir,
    ogunleri_getir,
    yemekhaneleri_getir,
    yemekleri_getir,
)
from yonlendiriciler.ortak import giris_gerekli

menu_bp = Blueprint("menu", __name__, url_prefix="/api")


@menu_bp.get("/yemekhaneler")
@giris_gerekli
def yemekhaneler():
    return jsonify({"yemekhaneler": yemekhaneleri_getir()})


@menu_bp.get("/ogunler")
@giris_gerekli
def ogunler():
    return jsonify({"ogunler": ogunleri_getir()})


@menu_bp.get("/yemekler")
@giris_gerekli
def yemekler():
    return jsonify({"yemekler": yemekleri_getir()})


@menu_bp.get("/menuler/gunluk")
@giris_gerekli
def gunun_menusu():
    yemekhane_id = request.args.get("yemekhane_id", default=1, type=int)
    ogun_id = request.args.get("ogun_id", default=2, type=int)
    tarih = request.args.get("tarih") or date.today().isoformat()
    menu = gunun_menusu_getir(yemekhane_id, ogun_id, tarih)
    if menu:
        kullanici_alerjenleri = set(kullanici_alerjen_idleri_getir(g.kullanici_id))
        menu = dict(menu)
        yemekler = []
        for y in menu["yemekler"]:
            y_kopya = dict(y)
            y_kopya["alerjen_uyarisi"] = bool(
                set(y_kopya.get("alerjen_id_listesi", [])) & kullanici_alerjenleri
            )
            yemekler.append(y_kopya)
        menu["yemekler"] = yemekler
    return jsonify({"menu": menu})


@menu_bp.get("/menuler/haftalik")
@giris_gerekli
def haftalik_menuler():
    yemekhane_id = request.args.get("yemekhane_id", default=1, type=int)
    bugun = date.today()
    baslangic = request.args.get("baslangic") or bugun.isoformat()
    bitis = request.args.get("bitis") or (bugun + timedelta(days=6)).isoformat()
    menuler = haftalik_menuler_getir(
        yemekhane_id, baslangic, bitis, g.kullanici_id, g.rol
    )
    return jsonify({"menuler": menuler})
