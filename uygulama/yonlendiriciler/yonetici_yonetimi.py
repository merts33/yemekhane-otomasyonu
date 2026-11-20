from flask import Blueprint, jsonify, request
from veri.yonetici_veri import (
    menu_guncelle,
    menu_olustur,
    menu_raporu_getir,
    menu_yemek_idleri_getir,
)
from yonlendiriciler.ortak import yonetici_gerekli

yonetici_bp = Blueprint("yonetici", __name__, url_prefix="/api/yonetici")


@yonetici_bp.get("/rapor")
@yonetici_gerekli
def rapor():
    return jsonify({"menuler": menu_raporu_getir()})


@yonetici_bp.get("/menuler/<int:menu_id>/yemekler")
@yonetici_gerekli
def menu_yemekleri(menu_id):
    return jsonify({"yemek_idler": menu_yemek_idleri_getir(menu_id)})


@yonetici_bp.post("/menuler")
@yonetici_gerekli
def yeni_menu():
    veri = request.get_json(silent=True) or {}
    yemekhane_id = veri.get("yemekhane_id")
    tarih = veri.get("tarih")
    ogun_id = veri.get("ogun_id")
    ogrenci_fiyati = veri.get("ogrenci_fiyati")
    personel_fiyati = veri.get("personel_fiyati")
    yemek_idler = veri.get("yemek_idler") or []

    if not yemekhane_id or not tarih or not ogun_id or not yemek_idler:
        return jsonify({"hata": "Yemekhane, tarih, öğün ve yemek seçimi zorunludur."}), 400

    menu_id = menu_olustur(
        int(yemekhane_id),
        tarih,
        int(ogun_id),
        float(ogrenci_fiyati),
        float(personel_fiyati),
        [int(y) for y in yemek_idler],
    )
    return jsonify({"mesaj": "Menü oluşturuldu.", "menu_id": menu_id}), 201


@yonetici_bp.put("/menuler/<int:menu_id>")
@yonetici_gerekli
def menu_duzenle(menu_id):
    veri = request.get_json(silent=True) or {}
    ogrenci_fiyati = veri.get("ogrenci_fiyati")
    personel_fiyati = veri.get("personel_fiyati")
    yemek_idler = veri.get("yemek_idler") or []

    if ogrenci_fiyati is None or personel_fiyati is None or not yemek_idler:
        return jsonify({"hata": "Fiyatlar ve yemek listesi zorunludur."}), 400

    menu_guncelle(
        menu_id,
        float(ogrenci_fiyati),
        float(personel_fiyati),
        [int(y) for y in yemek_idler],
    )
    return jsonify({"mesaj": "Menü güncellendi."})
