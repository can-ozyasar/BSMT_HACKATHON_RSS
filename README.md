# BSMT Hackathon RSS

RSS verileri ve haber/akış takibi üzerine kurgulanmış Python hackathon çalışması.

## Bu Repo Ne İçin Var?
RSS akışlarından anlamlı veri çıkarma ve hackathon sürecinde hızlı prototip geliştirme pratiği yapmak için oluşturuldu.

Bu README'nin amacı; repoya ilk kez gelen birinin projenin neden açıldığını, içinde ne bulunduğunu ve nereden başlaması gerektiğini hızlıca anlamasını sağlamaktır.

## İçerik ve Kapsam
Bu repoda öne çıkan içerikler şunlardır:
- RSS kaynaklarından veri toplama yaklaşımı
- Python ile hızlı prototipleme
- Hackathon teslim yapısına uygun dosya düzeni
- Node.js tabanlı kurulum ve geliştirme komutları
- Python bağımlılıklarını tanımlayan requirements dosyası
- Tarayıcıda incelenebilen HTML arayüz dosyaları
- Hazır npm scriptleriyle geliştirme, build veya test akışı

## Kimler İçin Faydalı?
Hackathon demosunu incelemek, fikrin teknik kapsamını anlamak veya prototipi geliştirmek isteyenler için uygundur.

## Kullanılan Teknolojiler
- Python
- Node.js
- npm
- React
- Vite
- HTML
- CSS

## Kurulum
```bash
cd HACKATHON-2/bios-signal-radar/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd HACKATHON-2/bios-signal-radar/frontend
npm install
```

## Çalıştırma
```bash
cd HACKATHON-2/bios-signal-radar/frontend && npm run dev
```

## Önemli Dosyalar
- `HACKATHON-2/bios-signal-radar/backend/main.py`
- `HACKATHON-2/bios-signal-radar/backend/requirements.txt`
- `HACKATHON-2/bios-signal-radar/frontend/index.html`
- `HACKATHON-2/bios-signal-radar/frontend/package.json`

## Proje Yapısı
- `HACKATHON-2` - 199 dosya

## Geliştirme Notları
- README içeriği, repodaki mevcut dosya yapısı ve proje açıklamasına göre düzenlenmiştir.
- Yeni modül, veri seti veya servis eklendiğinde kurulum/çalıştırma bölümlerini güncelleyin.
- Frontend projelerinde sürüm uyumu için `package-lock.json`/`pnpm-lock.yaml` gibi lock dosyalarını koruyun.

## Lisans
Bu repoda açık bir lisans dosyası yoksa tüm haklar varsayılan olarak proje sahibine aittir. Paylaşım veya kullanım koşulları için repo sahibine danışın.
