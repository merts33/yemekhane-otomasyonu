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
