from datetime import datetime
import json
import os
import secrets
import redis


def redis_baglantisi():
    return redis.Redis(
        host=os.environ.get("REDIS_HOST", "redis"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        decode_responses=True,
    )


def oturum_olustur(kullanici_id, rol):
    token = secrets.token_urlsafe(32)
    baglanti = redis_baglantisi()
    veri = json.dumps({"kullanici_id": kullanici_id, "rol": rol})
    baglanti.set(f"oturum:{token}", veri, ex=1800)
    return token


def oturum_getir(token):
    if not token:
        return None
    baglanti = redis_baglantisi()
    anahtar = f"oturum:{token}"
    veri = baglanti.get(anahtar)
    if not veri:
        return None
    baglanti.expire(anahtar, 1800)
    return json.loads(veri)


def oturum_sil(token):
    if not token:
        return
    baglanti = redis_baglantisi()
    baglanti.delete(f"oturum:{token}")


def menu_anahtari(yemekhane_id, tarih, ogun_id):
    return f"menu:{yemekhane_id}:{tarih}:{ogun_id}"


def menu_onbellekten_getir(yemekhane_id, tarih, ogun_id):
    baglanti = redis_baglantisi()
    anahtar = menu_anahtari(yemekhane_id, tarih, ogun_id)
    veri = baglanti.get(anahtar)
    if not veri:
        return None
    return json.loads(veri)


def menu_onbellege_yaz(yemekhane_id, tarih, ogun_id, veri):
    if not veri:
        return
    gun_sonu = datetime.strptime(tarih, "%Y-%m-%d").replace(
        hour=23, minute=59, second=59
    )
    kalan_saniye = int((gun_sonu - datetime.now()).total_seconds())
    if kalan_saniye <= 0:
        return
    baglanti = redis_baglantisi()
    anahtar = menu_anahtari(yemekhane_id, tarih, ogun_id)
    baglanti.set(anahtar, json.dumps(veri), ex=kalan_saniye)


def menu_onbellegi_sil(yemekhane_id, tarih, ogun_id):
    baglanti = redis_baglantisi()
    anahtar = menu_anahtari(yemekhane_id, tarih, ogun_id)
    baglanti.delete(anahtar)
