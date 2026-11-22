let aktifKullanici = null;
let yemekhaneler = [];
let ogunler = [];

const mesajKutusu = document.getElementById("mesaj-kutusu");
const ustCubuk = document.getElementById("ust-cubuk");
const girisBolumu = document.getElementById("giris-bolumu");
const anaBolum = document.getElementById("ana-bolum");

function mesajGoster(metin, tur = "basari") {
  mesajKutusu.textContent = metin;
  mesajKutusu.className = tur === "hata" ? "bildirim bildirim-hata" : "bildirim bildirim-basari";
}

function mesajTemizle() {
  mesajKutusu.textContent = "";
  mesajKutusu.className = "gizli";
}

function paraBicimle(tutar) {
  return Number(tutar).toFixed(2).replace(".", ",") + " TL";
}

function bakiyeGuncelle(yeniBakiye) {
  if (aktifKullanici) {
    aktifKullanici.bakiye = Number(yeniBakiye);
  }
  document.getElementById("kullanici-bakiye").textContent = paraBicimle(yeniBakiye);
  document.getElementById("bakiye-detay-tutar").textContent = paraBicimle(yeniBakiye);
}

async function istekGonder(yol, secenekler = {}) {
  const ayarlar = {
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    credentials: "same-origin",
    ...secenekler,
  };
  const yanit = await fetch(yol, ayarlar);
  const veri = await yanit.json().catch(() => ({}));
  if (!yanit.ok) {
    throw new Error(veri.hata || "İşlem gerçekleştirilemedi.");
  }
  return veri;
}

function sekmeAc(sekmeAdi) {
  mesajTemizle();
  document.querySelectorAll(".sekme-dugme").forEach((dugme) => {
    dugme.classList.toggle("aktif", dugme.dataset.sekme === sekmeAdi);
  });
  document.querySelectorAll(".sekme-icerik").forEach((alan) => {
    alan.classList.toggle("gizli", alan.id !== "sekme-" + sekmeAdi);
  });

  if (sekmeAdi === "gunluk") gununMenusunuYukle();
  if (sekmeAdi === "haftalik") haftalikMenuleriYukle();
  if (sekmeAdi === "rezervasyonlar") rezervasyonlariYukle();
  if (sekmeAdi === "bakiye") bakiyeBilgisiniYukle();
  if (sekmeAdi === "degerlendirme") degerlendirmeleriYukle();
  if (sekmeAdi === "yonetici") yoneticiPaneliYukle();
}

async function tanimlariYukle() {
  const [yVeri, oVeri] = await Promise.all([
    istekGonder("/api/yemekhaneler"),
    istekGonder("/api/ogunler"),
  ]);
  yemekhaneler = yVeri.yemekhaneler;
  ogunler = oVeri.ogunler;

  const yemekhaneSecenekleri = yemekhaneler
    .map((y) => `<option value="${y.id}">${y.ad}</option>`)
    .join("");
  const ogunSecenekleri = ogunler
    .map((o) => `<option value="${o.id}">${o.ad} (Son: ${o.son_saat})</option>`)
    .join("");

  document.getElementById("gunluk-yemekhane").innerHTML = yemekhaneSecenekleri;
  document.getElementById("haftalik-yemekhane").innerHTML = yemekhaneSecenekleri;
  document.getElementById("yonetici-yemekhane").innerHTML = yemekhaneSecenekleri;

  document.getElementById("gunluk-ogun").innerHTML = ogunSecenekleri;
  document.getElementById("gunluk-ogun").value = "2";
  document.getElementById("yonetici-ogun").innerHTML = ogunSecenekleri;

  const bugun = new Date().toISOString().slice(0, 10);
  document.getElementById("gunluk-tarih").value = bugun;
  document.getElementById("yonetici-tarih").value = bugun;
}

async function gununMenusunuYukle() {
  const yemekhaneId = document.getElementById("gunluk-yemekhane").value;
  const ogunId = document.getElementById("gunluk-ogun").value;
  const tarih = document.getElementById("gunluk-tarih").value;
  const kutu = document.getElementById("gunluk-menu-icerik");

  try {
    const veri = await istekGonder(
      `/api/menuler/gunluk?yemekhane_id=${yemekhaneId}&ogun_id=${ogunId}&tarih=${tarih}`
    );
    const menu = veri.menu;
    if (!menu) {
      kutu.innerHTML = `<p class="soluk">Seçilen tarih ve öğün için menü bulunamadı.</p>`;
      return;
    }

    const satirlar = menu.yemekler
      .map(
        (y) => `
      <tr>
        <td>${y.kategori}</td>
        <td>
          <strong>${y.ad}</strong>
          ${y.vejetaryen ? '<span class="rozet rozet-vej">Vejetaryen</span>' : ""}
          ${y.alerjenler ? `<span class="rozet rozet-alerjen">${y.alerjenler}</span>` : ""}
        </td>
        <td>${y.kalori} kcal</td>
      </tr>`
      )
      .join("");

    kutu.innerHTML = `
      <p>
        <strong>${menu.yemekhane}</strong> · ${menu.tarih} · ${menu.ogun}
        <span class="soluk">(Boş yer: ${menu.bos_yer}/${menu.kapasite}, Toplam: ${menu.toplam_kalori} kcal${
      menu.ortalama_puan ? `, Puan: ${menu.ortalama_puan}/5` : ""
    })</span>
      </p>
      <div class="tablo-kaydir">
        <table class="tablo">
          <thead><tr><th>Kategori</th><th>Yemek</th><th>Kalori</th></tr></thead>
          <tbody>${satirlar}</tbody>
        </table>
      </div>
    `;
  } catch (hata) {
    mesajGoster(hata.message, "hata");
  }
}

async function haftalikMenuleriYukle() {
  const yemekhaneId = document.getElementById("haftalik-yemekhane").value;
  const liste = document.getElementById("haftalik-menu-listesi");
  try {
    const veri = await istekGonder(`/api/menuler/haftalik?yemekhane_id=${yemekhaneId}`);
    if (!veri.menuler.length) {
      liste.innerHTML = `<p class="soluk">Önümüzdeki 7 gün için tanımlı menü bulunamadı.</p>`;
      return;
    }

    liste.innerHTML = veri.menuler
      .map((m) => {
        const zatenVar = m.rezervasyon_durumu === "aktif" || m.rezervasyon_durumu === "kullanildi";
        const pasif = m.suresi_gecti || m.bos_yer <= 0 || zatenVar;
        let dugmeYazi = "Rezervasyon Yap";
        if (m.rezervasyon_durumu === "aktif") dugmeYazi = "Rezerve Edildi";
        else if (m.rezervasyon_durumu === "kullanildi") dugmeYazi = "Kullanıldı";
        else if (m.bos_yer <= 0) dugmeYazi = "Kapasite Dolu";
        else if (m.suresi_gecti) dugmeYazi = "Süre Doldu";

        return `
        <article class="menu-kart">
          <div>
            <div class="menu-baslik">
              <strong>${m.tarih} · ${m.ogun}</strong>
              <span class="rozet rozet-aktif">${paraBicimle(m.fiyat)}</span>
            </div>
            <p class="soluk">${m.yemekhane}</p>
            <p class="soluk">Boş yer: ${m.bos_yer} / ${m.kapasite}</p>
            <p class="soluk">Son saat: ${m.rezervasyon_son}</p>
          </div>
          <button type="button" class="dugme" ${pasif ? "disabled" : ""} onclick="rezervasyonOlustur(${m.menu_id})">
            ${dugmeYazi}
          </button>
        </article>`;
      })
      .join("");
  } catch (hata) {
    mesajGoster(hata.message, "hata");
  }
}

async function rezervasyonOlustur(menuId) {
  mesajTemizle();
  try {
    const veri = await istekGonder("/api/rezervasyonlar", {
      method: "POST",
      body: JSON.stringify({ menu_id: menuId }),
    });
    bakiyeGuncelle(veri.bakiye);
    mesajGoster(veri.mesaj, "basari");
    haftalikMenuleriYukle();
  } catch (hata) {
    mesajGoster(hata.message, "hata");
  }
}

async function rezervasyonlariYukle() {
  const kutu = document.getElementById("rezervasyonlar-icerik");
  try {
    const veri = await istekGonder("/api/rezervasyonlar");
    if (!veri.rezervasyonlar.length) {
      kutu.innerHTML = `<p class="soluk">Henüz rezervasyonunuz bulunmuyor.</p>`;
      return;
    }

    const satirlar = veri.rezervasyonlar
      .map((r) => {
        const rozetSinif =
          r.durum === "aktif"
            ? "rozet-aktif"
            : r.durum === "kullanildi"
            ? "rozet-kullanildi"
            : "rozet-iptal";
        return `
        <tr>
          <td>${r.tarih}</td>
          <td>${r.yemekhane}</td>
          <td>${r.ogun}</td>
          <td>${paraBicimle(r.ucret)}</td>
          <td><span class="rozet ${rozetSinif}">${r.durum}</span></td>
          <td>
            ${
              r.iptal_edilebilir
                ? `<button type="button" class="dugme dugme-tehlike dugme-kucuk" onclick="rezervasyonIptalEt(${r.rezervasyon_id})">İptal Et</button>`
                : `<span class="soluk">-</span>`
            }
          </td>
        </tr>`;
      })
      .join("");

    kutu.innerHTML = `
      <table class="tablo">
        <thead>
          <tr><th>Tarih</th><th>Yemekhane</th><th>Öğün</th><th>Ücret</th><th>Durum</th><th>İşlem</th></tr>
        </thead>
        <tbody>${satirlar}</tbody>
      </table>`;
  } catch (hata) {
    mesajGoster(hata.message, "hata");
  }
}

async function rezervasyonIptalEt(rezervasyonId) {
  mesajTemizle();
  try {
    const veri = await istekGonder(`/api/rezervasyonlar/${rezervasyonId}/iptal`, {
      method: "POST",
    });
    bakiyeGuncelle(veri.bakiye);
    mesajGoster(veri.mesaj, "basari");
    rezervasyonlariYukle();
  } catch (hata) {
    mesajGoster(hata.message, "hata");
  }
}

async function bakiyeBilgisiniYukle(kaynaktan = false) {
  const kutu = document.getElementById("bakiye-hareketleri-icerik");
  try {
    const veri = await istekGonder(`/api/bakiye${kaynaktan ? "?kaynaktan=1" : ""}`);
    bakiyeGuncelle(veri.bakiye);

    if (!veri.hareketler.length) {
      kutu.innerHTML = `<p class="soluk">Henüz bakiye hareketiniz yok.</p>`;
      return;
    }

    const satirlar = veri.hareketler
      .map(
        (h) => `
      <tr>
        <td>${h.olusturma}</td>
        <td>${h.tur}</td>
        <td>${h.aciklama}</td>
        <td>${h.tutar >= 0 ? "+" : ""}${paraBicimle(h.tutar)}</td>
      </tr>`
      )
      .join("");

    kutu.innerHTML = `
      <table class="tablo">
        <thead><tr><th>Tarih</th><th>Tür</th><th>Açıklama</th><th>Tutar</th></tr></thead>
        <tbody>${satirlar}</tbody>
      </table>`;
  } catch (hata) {
    mesajGoster(hata.message, "hata");
  }
}

document.getElementById("bakiye-yukle-formu").addEventListener("submit", async (olay) => {
  olay.preventDefault();
  mesajTemizle();
  const tutar = document.getElementById("yukleme-tutari").value;
  try {
    const veri = await istekGonder("/api/bakiye/yukle", {
      method: "POST",
      body: JSON.stringify({ tutar }),
    });
    bakiyeGuncelle(veri.bakiye);
    document.getElementById("yukleme-tutari").value = "";
    mesajGoster(veri.mesaj, "basari");
    bakiyeBilgisiniYukle(true);
  } catch (hata) {
    mesajGoster(hata.message, "hata");
  }
});

async function degerlendirmeleriYukle() {
  const yapilacaklarKutu = document.getElementById("degerlendirme-yapilacaklar");
  const gecmisKutu = document.getElementById("gecmis-degerlendirmeler");
  try {
    const [rezVeri, degVeri] = await Promise.all([
      istekGonder("/api/rezervasyonlar"),
      istekGonder("/api/degerlendirmeler"),
    ]);

    const adaylar = rezVeri.rezervasyonlar.filter((r) => r.degerlendirilebilir);
    if (!adaylar.length) {
      yapilacaklarKutu.innerHTML = `<p class="soluk">Değerlendirilecek kullanılmış menü bulunmuyor.</p>`;
    } else {
      yapilacaklarKutu.innerHTML = adaylar
        .map(
          (r) => `
        <div class="kart">
          <strong>${r.tarih} · ${r.yemekhane} · ${r.ogun}</strong>
          <div class="filtre-satiri" style="margin-top:0.75rem;">
            <div>
              <label for="puan-${r.menu_id}">Puan (1-5)</label>
              <select id="puan-${r.menu_id}">
                <option value="5">5 - Çok İyi</option>
                <option value="4">4 - İyi</option>
                <option value="3">3 - Orta</option>
                <option value="2">2 - Kötü</option>
                <option value="1">1 - Çok Kötü</option>
              </select>
            </div>
            <div>
              <label for="yorum-${r.menu_id}">Yorum</label>
              <input id="yorum-${r.menu_id}" type="text" maxlength="500" placeholder="İsteğe bağlı yorum">
            </div>
          </div>
          <button type="button" class="dugme dugme-kucuk" onclick="degerlendirmeGonder(${r.menu_id})">Gönder</button>
        </div>`
        )
        .join("");
    }

    if (!degVeri.degerlendirmeler.length) {
      gecmisKutu.innerHTML = `<p class="soluk">Henüz değerlendirme yapmadınız.</p>`;
    } else {
      gecmisKutu.innerHTML = `
        <table class="tablo">
          <thead><tr><th>Tarih</th><th>Yemekhane</th><th>Öğün</th><th>Puan</th><th>Yorum</th></tr></thead>
          <tbody>
            ${degVeri.degerlendirmeler
              .map(
                (d) => `
              <tr>
                <td>${d.tarih}</td>
                <td>${d.yemekhane}</td>
                <td>${d.ogun}</td>
                <td>${d.puan} / 5</td>
                <td>${d.yorum || "-"}</td>
              </tr>`
              )
              .join("")}
          </tbody>
        </table>`;
    }
  } catch (hata) {
    mesajGoster(hata.message, "hata");
  }
}

async function degerlendirmeGonder(menuId) {
  mesajTemizle();
  const puan = document.getElementById(`puan-${menuId}`).value;
  const yorum = document.getElementById(`yorum-${menuId}`).value;
  try {
    const veri = await istekGonder("/api/degerlendirmeler", {
      method: "POST",
      body: JSON.stringify({ menu_id: menuId, puan, yorum }),
    });
    mesajGoster(veri.mesaj, "basari");
    degerlendirmeleriYukle();
  } catch (hata) {
    mesajGoster(hata.message, "hata");
  }
}

async function yoneticiPaneliYukle() {
  const yemekListesiKutu = document.getElementById("yonetici-yemek-listesi");
  const raporKutu = document.getElementById("yonetici-rapor-icerik");
  try {
    const [yVeri, rVeri] = await Promise.all([
      istekGonder("/api/yemekler"),
      istekGonder("/api/yonetici/rapor"),
    ]);

    yemekListesiKutu.innerHTML = yVeri.yemekler
      .map(
        (y) => `
      <label class="yemek-secim-oge">
        <input type="checkbox" name="yonetici-yemek" value="${y.id}">
        <span>${y.kategori}: ${y.ad} (${y.kalori} kcal)</span>
      </label>`
      )
      .join("");

    raporKutu.innerHTML = `
      <table class="tablo">
        <thead>
          <tr><th>Tarih</th><th>Yemekhane</th><th>Öğün</th><th>Doluluk</th><th>Ort. Puan</th><th>İşlem</th></tr>
        </thead>
        <tbody>
          ${rVeri.menuler
            .map(
              (m) => `
            <tr>
              <td>${m.tarih}</td>
              <td>${m.yemekhane}</td>
              <td>${m.ogun}</td>
              <td>${m.rezerve}/${m.kapasite} (%${m.doluluk_yuzde})</td>
              <td>${m.ortalama_puan !== null ? `${m.ortalama_puan} (${m.oy_sayisi} oy)` : "-"}</td>
              <td>
                <button type="button" class="dugme dugme-kucuk" onclick="menuDuzenleHazirla(${m.menu_id}, ${m.yemekhane_id}, '${m.tarih}', ${m.ogun_id}, ${m.ogrenci_fiyati}, ${m.personel_fiyati})">Düzenle</button>
              </td>
            </tr>`
            )
            .join("")}
        </tbody>
      </table>`;
  } catch (hata) {
    mesajGoster(hata.message, "hata");
  }
}

async function menuDuzenleHazirla(menuId, yemekhaneId, tarih, ogunId, ogrFiyat, perFiyat) {
  mesajTemizle();
  document.getElementById("yonetici-duzenlenen-id").value = menuId;
  document.getElementById("yonetici-form-baslik").textContent = "Menüyü Düzenle";
  document.getElementById("yonetici-yemekhane").value = yemekhaneId;
  document.getElementById("yonetici-yemekhane").disabled = true;
  document.getElementById("yonetici-tarih").value = tarih;
  document.getElementById("yonetici-tarih").disabled = true;
  document.getElementById("yonetici-ogun").value = ogunId;
  document.getElementById("yonetici-ogun").disabled = true;
  document.getElementById("yonetici-ogr-fiyat").value = ogrFiyat;
  document.getElementById("yonetici-per-fiyat").value = perFiyat;
  document.getElementById("yonetici-iptal-dugme").classList.remove("gizli");

  try {
    const veri = await istekGonder(`/api/yonetici/menuler/${menuId}/yemekler`);
    const seciliSet = new Set(veri.yemek_idler);
    document.querySelectorAll('input[name="yonetici-yemek"]').forEach((kutu) => {
      kutu.checked = seciliSet.has(Number(kutu.value));
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (hata) {
    mesajGoster(hata.message, "hata");
  }
}

function yoneticiFormunuSifirla() {
  document.getElementById("yonetici-duzenlenen-id").value = "";
  document.getElementById("yonetici-form-baslik").textContent = "Yeni Menü Oluştur";
  document.getElementById("yonetici-yemekhane").disabled = false;
  document.getElementById("yonetici-tarih").disabled = false;
  document.getElementById("yonetici-ogun").disabled = false;
  document.getElementById("yonetici-iptal-dugme").classList.add("gizli");
  document.querySelectorAll('input[name="yonetici-yemek"]').forEach((kutu) => {
    kutu.checked = false;
  });
}

document.getElementById("yonetici-iptal-dugme").addEventListener("click", yoneticiFormunuSifirla);

document.getElementById("yonetici-menu-formu").addEventListener("submit", async (olay) => {
  olay.preventDefault();
  mesajTemizle();
  const duzenlenenId = document.getElementById("yonetici-duzenlenen-id").value;
  const yemekIdler = Array.from(
    document.querySelectorAll('input[name="yonetici-yemek"]:checked')
  ).map((k) => Number(k.value));

  const govde = {
    yemekhane_id: Number(document.getElementById("yonetici-yemekhane").value),
    tarih: document.getElementById("yonetici-tarih").value,
    ogun_id: Number(document.getElementById("yonetici-ogun").value),
    ogrenci_fiyati: Number(document.getElementById("yonetici-ogr-fiyat").value),
    personel_fiyati: Number(document.getElementById("yonetici-per-fiyat").value),
    yemek_idler: yemekIdler,
  };

  try {
    const veri = duzenlenenId
      ? await istekGonder(`/api/yonetici/menuler/${duzenlenenId}`, {
          method: "PUT",
          body: JSON.stringify(govde),
        })
      : await istekGonder("/api/yonetici/menuler", {
          method: "POST",
          body: JSON.stringify(govde),
        });
    mesajGoster(veri.mesaj, "basari");
    yoneticiFormunuSifirla();
    yoneticiPaneliYukle();
  } catch (hata) {
    mesajGoster(hata.message, "hata");
  }
});

function oturumuBaslat(kullanici) {
  aktifKullanici = kullanici;
  document.getElementById("kullanici-ad-soyad").textContent = `${kullanici.ad} ${kullanici.soyad}`;
  bakiyeGuncelle(kullanici.bakiye);
  document
    .getElementById("yonetici-sekme-dugme")
    .classList.toggle("gizli", kullanici.rol !== "yonetici");
  girisBolumu.classList.add("gizli");
  ustCubuk.classList.remove("gizli");
  anaBolum.classList.remove("gizli");
}

document.getElementById("giris-formu").addEventListener("submit", async (olay) => {
  olay.preventDefault();
  mesajTemizle();
  const eposta = document.getElementById("giris-eposta").value;
  const sifre = document.getElementById("giris-sifre").value;
  try {
    const veri = await istekGonder("/api/giris", {
      method: "POST",
      body: JSON.stringify({ eposta, sifre }),
    });
    oturumuBaslat(veri.kullanici);
    await tanimlariYukle();
    sekmeAc("gunluk");
  } catch (hata) {
    mesajGoster(hata.message, "hata");
  }
});

document.getElementById("cikis-dugme").addEventListener("click", async () => {
  await istekGonder("/api/cikis", { method: "POST" });
  aktifKullanici = null;
  ustCubuk.classList.add("gizli");
  anaBolum.classList.add("gizli");
  girisBolumu.classList.remove("gizli");
  mesajTemizle();
});

document.querySelectorAll(".sekme-dugme").forEach((dugme) => {
  dugme.addEventListener("click", () => sekmeAc(dugme.dataset.sekme));
});

["gunluk-yemekhane", "gunluk-ogun", "gunluk-tarih"].forEach((id) => {
  document.getElementById(id).addEventListener("change", gununMenusunuYukle);
});
document.getElementById("haftalik-yemekhane").addEventListener("change", haftalikMenuleriYukle);

(async () => {
  try {
    const veri = await istekGonder("/api/ben");
    oturumuBaslat(veri.kullanici);
    await tanimlariYukle();
    sekmeAc("gunluk");
  } catch {
  }
})();
