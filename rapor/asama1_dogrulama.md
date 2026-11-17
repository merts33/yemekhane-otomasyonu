# Aşama 1 · Altyapı Doğrulama Adımları

## 1. Servislerin Ayağa Kaldırılması ve Durum Kontrolü

```bash
docker compose up -d
docker compose ps -a
```

Beklenen durum: `mysql-primary`, `mysql-replica`, `redis`, `frontend` servisleri `healthy`, `replica-setup` servisi `Exited (0)`.

## 2. Replikasyon Durumunun Kontrolü

```bash
docker compose exec mysql-replica mysql -uroot -pyemekhane_kok -e "SHOW REPLICA STATUS\G"
```

`Replica_IO_Running: Yes` ve `Replica_SQL_Running: Yes` olmalıdır.

## 3. Kaynakta Yazma ve Replikadan Okuma

```bash
docker compose exec mysql-primary mysql -uyemekhane_app -pUyg_2026 yemekhane -e "CALL sp_bakiye_yukle(7, 100)"
docker compose exec mysql-replica mysql -uyemekhane_app -pUyg_2026 yemekhane -e "SELECT id, bakiye FROM kullanicilar WHERE id = 7"
```

## 4. Replikaya Yazma Denemesi (Read-Only Hatası)

```bash
docker compose exec mysql-replica mysql -uyemekhane_app -pUyg_2026 yemekhane -e "CALL sp_bakiye_yukle(7, 50)"
```

Beklenen hata: `ERROR 1290 (HY000): The MySQL server is running with the --read-only option so it cannot execute this statement`

## 5. Replika Durdurulup Başlatıldığında Değişikliklerin Yakalanması

```bash
docker compose stop mysql-replica
docker compose exec mysql-primary mysql -uyemekhane_app -pUyg_2026 yemekhane -e "CALL sp_bakiye_yukle(7, 200)"
docker compose start mysql-replica
docker compose exec mysql-replica mysql -uyemekhane_app -pUyg_2026 yemekhane -e "SELECT id, bakiye FROM kullanicilar WHERE id = 7"
```

## 6. Redis Kontrolü

```bash
docker compose exec redis redis-cli ping
```

Beklenen yanıt: `PONG`
