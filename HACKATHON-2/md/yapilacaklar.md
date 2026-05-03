# Proje İçin Dikkat Edilecekler — Yapılacak / Yapılmayacaklar

## 0. Ana Karar

Bu proje **basit bir RSS haber okuyucu** gibi değil, **Avrupa endüstriyel fırsat radarı** gibi sunulmalı.

Ama temel hedef unutulmamalı:

> Kullanıcı RSS ekler → haberler çekilir → AI analiz eder → skorlanır → modern arayüzde anlamlı şekilde gösterilir.

Yarışma özellikle çalışan MVP, arayüz kalitesi, AI isabeti ve kullanıcı deneyimini öne çıkarıyor. 

---

# 1. Mutlaka Yapılacaklar

## 1.1 RSS Kaynak Yönetimi

* Kullanıcı RSS kaynağı ekleyebilmeli.
* RSS kaynağı listelenebilmeli.
* RSS kaynağı silinebilmeli.
* Eklenen kaynaklar uygulama kapanıp açıldığında kaybolmamalı.
* RSS URL geçersizse kullanıcıya anlaşılır hata verilmeli.
* Her kaynak için mümkünse şu bilgiler gösterilmeli:

  * Kaynak adı
  * RSS URL
  * Son çekim zamanı
  * Durum: aktif / hata / bekliyor

Yarışma dokümanı RSS ekleme, listeleme, silme, geçerlilik kontrolü ve kalıcılığı zorunlu görüyor. 

---

## 1.2 Haber Çekme Akışı

* “Yenile” butonu mutlaka olmalı.
* Tüm RSS kaynaklarından haber çekilmeli.
* Haberlerde en az şu alanlar alınmalı:

  * Başlık
  * Link
  * Yayın tarihi
  * Kaynak adı
  * Kısa açıklama / içerik
* Aynı haber tekrar gösterilmemeli.
* Dedup için sadece URL değil, başlık/hash kontrolü de yapılmalı.
* Hatalı RSS kaynağı tüm sistemi bozmamalı.

Önerilen akış: RSS kaynakları → collector → normalizer → AI processor → veri katmanı → dashboard. 

---

## 1.3 AI Analizi

Her haber için AI şu alanları üretmeli:

```json
{
  "event_type": "relocation | closure | expansion | new_plant | tender | other",
  "summary_tr": "Türkçe kısa özet",
  "company": "Şirket adı veya null",
  "from_location": "Çıkış lokasyonu veya null",
  "to_location": "Hedef lokasyon veya null",
  "sector": "Sektör veya null",
  "confidence": 0.0
}
```

Dikkat:

* AI çıktısı **sadece JSON** olmalı.
* Eksik bilgi varsa uydurulmamalı, `null` yazılmalı.
* Türkçe özet üretmeli.
* Özel isimler orijinal haliyle korunmalı.
* AI cevabı mutlaka validate edilmeli.
* JSON bozuk gelirse sistem çökmemeli.
* Confidence düşükse kartta uyarı gösterilmeli.

AI çıktısında JSON zorunluluğu, `null` kullanımı, Türkçe çıktı ve güven puanı dosyalarda açıkça belirtilmiş. 

---

## 1.4 BIOS-Fit Skoru

Skor sistemin en önemli farklarından biri olmalı.

Yapılacak doğru yaklaşım:

```txt
AI veri çıkarır.
Backend skoru hesaplar.
```

AI’ya doğrudan “skor ver” demek yerine, AI’dan olay tipi, şirket, lokasyon, sektör ve zaman bilgisi alınmalı. Skor daha sonra deterministik hesaplanmalı.

Skor bileşenleri:

* Olay tipi
* Aktör netliği
* Coğrafya
* Zaman penceresi
* Kaynak güveni

Yarışma raporu BIOS-fit skorunun 0–100 arasında hesaplanmasını ve olay tipi, aktör netliği, coğrafya, zaman ve kaynak güveni gibi bileşenlere dayanmasını istiyor. 

---

## 1.5 Skor Renkleri ve Aksiyon

Kartlarda skor sadece sayı olarak kalmamalı.

|   Skor | Durum         | Renk  | Aksiyon                                  |
| -----: | ------------- | ----- | ---------------------------------------- |
| 80–100 | Yüksek fırsat | Yeşil | Hemen iletişime geç / dosya talep et     |
|  65–79 | İzlenecek     | Mavi  | Takip listesine al                       |
|  50–64 | Şartlı ilgi   | Sarı  | Tender ise takip et, değilse partner ara |
|   0–49 | Düşük alaka   | Gri   | Arşivle                                  |

Detay ekranında “Bu skor neden çıktı?” bölümü olmalı.

Örnek:

```txt
Olay Tipi: expansion
Şirket: Hitachi Energy
Lokasyon: Türkiye
Sektör: Enerji ekipmanları
Kaynak Güveni: Orta-yüksek
Sonuç: 82 / 100
```

---

# 2. Arayüzde Mutlaka Olması Gerekenler

## 2.1 Ana Dashboard

Ana ekran karmaşık olmamalı.

Olması gerekenler:

* Üstte arama kutusu
* Filtreler:

  * Olay tipi
  * Kaynak
  * Tarih
  * Minimum skor
  * Şirket
  * Sektör
* RSS kaynak paneli
* Haber kartları
* Yenile butonu
* Son güncelleme zamanı
* Top fırsatlar alanı

Yarışma dokümanı ana ekranda arama, filtreler, RSS kaynak yönetimi, haber kartları ve yenile butonu bekliyor. 

---

## 2.2 Haber Kartı

Her kartta şunlar görünmeli:

```txt
[Skor] [Olay Tipi] [Kaynak]

Haber Başlığı

Kısa Türkçe özet

Şirket:
Lokasyon:
Sektör:
Tarih:
Önerilen aksiyon:
```

Kartlarda renk kodu olmalı:

* relocation: mavi
* closure: kırmızı
* expansion: yeşil
* new_plant: mor/yeşil
* tender: turuncu
* other: gri

---

## 2.3 Haber Detay Ekranı

Detay ekranı projeyi profesyonel gösterir.

Mutlaka olsun:

* Haber başlığı
* Kaynak adı
* Yayın tarihi
* Kaynağa git linki
* AI Türkçe özet
* Event type
* Şirket
* From → To lokasyon
* Sektör
* Skor
* Confidence
* Skor gerekçesi
* AI varsayımları
* Önerilen aksiyon

---

## 2.4 Boş / Hata / Loading Durumları

Bunlar küçük görünür ama jüri gözünde kaliteyi artırır.

Yapılacaklar:

* RSS yoksa: “Henüz RSS kaynağı eklemediniz.”
* Haber yoksa: “Bu filtreye uygun haber bulunamadı.”
* AI analiz sürüyorsa: skeleton/loading göster.
* RSS hatalıysa: “Bu kaynak okunamadı, URL’yi kontrol edin.”
* API hatasında teknik stack trace gösterme.

Yarışma dokümanı sade, okunabilir tipografi, anlamlı boş durumlar, loading göstergesi ve teknik olmayan hata mesajlarını özellikle vurguluyor. 

---

# 3. Markdown + Obsidian Graph Katmanı

## 3.1 Yapılmalı mı?

Evet, yapılmalı.

Ama ana sistemin yerine değil, **fark yaratan ikinci katman** olarak yapılmalı.

Doğru konumlandırma:

```txt
Ana ürün:
RSS + AI + Skor + Dashboard

Fark yaratan katman:
Markdown notları + Opportunity Graph
```

Bu fikir projeyi “haber okuyucu” olmaktan çıkarıp “kurumsal hafıza ve fırsat ağı” haline getirir. Dosyalarda da sistemin uzun vadede kurumsal hafızaya dönüşmesi ve şirket/lokasyon/sektör ilişkileriyle pazar zekâsı üretmesi stratejik değer olarak anlatılıyor. 

---

## 3.2 Markdown Nasıl Kullanılmalı?

Her analiz edilen haberden otomatik Markdown notu üretilebilir.

Örnek yapı:

```txt
/notes
  /news
    2026-05-02-hitachi-energy-kapasite-artisi.md
  /companies
    Hitachi Energy.md
  /locations
    Türkiye.md
    Dilovası.md
  /sectors
    Enerji Ekipmanları.md
  /events
    Expansion.md
```

---

## 3.3 Haber Markdown Örneği

```md
---
title: "Hitachi Energy Türkiye’deki üretim kapasitesini artıracak"
source: "Yeşil Ekonomi"
event_type: "expansion"
company: "Hitachi Energy"
location: "Türkiye"
sector: "Enerji Ekipmanları"
score: 82
confidence: 0.8
recommended_action: "reach_out"
---

# Hitachi Energy Türkiye’deki üretim kapasitesini artıracak

## Özet

Hitachi Energy, Türkiye’deki üretim kapasitesini artıracağını duyurdu. Bu haber BIOS açısından kapasite genişlemesi ve potansiyel endüstriyel relokasyon fırsatı olarak değerlendirilebilir.

## Çıkarılan Bilgiler

- Şirket: [[Hitachi Energy]]
- Lokasyon: [[Türkiye]]
- Sektör: [[Enerji Ekipmanları]]
- Olay Tipi: [[Expansion]]
- Skor: 82 / 100

## Önerilen Aksiyon

Teknik yatırım detayları takip edilmeli ve şirketin ilgili operasyon/tedarik karar vericileri araştırılmalı.
```

---

## 3.4 Graph View Nasıl Olmalı?

Graph node türleri:

* Haber
* Şirket
* Lokasyon
* Sektör
* Olay tipi
* Kaynak
* Aksiyon

Bağlantılar:

```txt
Haber → Şirket
Haber → Lokasyon
Haber → Sektör
Haber → Olay Tipi
Haber → Kaynak
Şirket → Diğer Haberler
Lokasyon → Diğer Şirketler
Sektör → Benzer Fırsatlar
```

Graph View ana ekran değil, ayrı sekme olmalı:

```txt
1. Haber Akışı
2. Top Fırsatlar
3. Opportunity Graph
4. RSS Kaynakları
```

---

# 4. Teknik Mimari

## 4.1 Önerilen MVP Mimari

24 saatlik yarışma için ağır mimariye girmeyin.

Önerilen yapı:

```txt
Frontend:
Next.js / React + Tailwind + shadcn/ui

Backend:
Next.js API routes veya Node.js Express

RSS:
rss-parser

Veri:
SQLite veya JSON dosyası

AI:
OpenAI / Gemini / Claude API

Validation:
Zod

Graph:
React Flow / Cytoscape.js / vis-network

Deploy:
Vercel / Render / Railway
```

Dosyalarda PostgreSQL, OpenSearch, workflow engine gibi ölçeklenebilir bileşenler öneriliyor; ancak bunlar MVP sonrası büyüme için düşünülmeli. 

---

## 4.2 Veri Modeli

Minimum veri modeli:

```ts
Source {
  id
  name
  url
  status
  lastFetchedAt
}

Article {
  id
  sourceId
  title
  url
  publishedAt
  rawSummary
  contentHash
  analysisStatus
}

Analysis {
  id
  articleId
  eventType
  summaryTr
  company
  fromLocation
  toLocation
  sector
  timeline
  score
  confidence
  rationale
  recommendedAction
  assumptions
}

GraphNode {
  id
  type
  label
}

GraphEdge {
  source
  target
  relation
}
```

---

# 5. Yapılmaması Gerekenler

## 5.1 Ana Akışı Riski Atmayın

Şunlara ana özellik bitmeden zaman harcamayın:

* Tam CRM entegrasyonu
* OpenSearch kurulumu
* PostgreSQL + karmaşık migration sistemi
* Kafka / RabbitMQ
* Kubernetes
* Gelişmiş harita animasyonları
* Tam Obsidian editörü
* Kullanıcıların elle not yazdığı karmaşık bilgi yönetim sistemi

Yarışma kapsam dışı olarak tam kurumsal CRM, üretim seviyesinde ölçeklenebilirlik, native mobil uygulama ve kuralları ihlal edecek scraping işlemlerini açıkça dışarıda bırakıyor. 

---

## 5.2 AI’ya Fazla Güvenmeyin

Yapılmamalı:

```txt
AI ne döndürürse doğrudan ekrana basmak
AI’dan açıklamasız skor almak
Eksik lokasyonu tahmin ettirmek
JSON validasyonu yapmamak
Bozuk JSON gelince sistemi çökertmek
```

Yapılmalı:

```txt
JSON schema validation
Eksik alanlara null
Confidence gösterimi
Assumptions alanı
Skor gerekçesi
Fallback hata mesajı
```

---

## 5.3 Graph’ı Ana Ürün Yapmayın

Yanlış yaklaşım:

```txt
Projeyi tamamen Obsidian klonu gibi yapmak
```

Doğru yaklaşım:

```txt
Graph = fark yaratan analiz katmanı
Dashboard = ana kullanım ekranı
```

Çünkü yarışmanın ana beklentisi kart/liste görünümü, filtreleme, arama ve detay ekranıdır. 

---

## 5.4 Canlı RSS’ye Tam Bağımlı Kalmayın

Demo sırasında RSS, internet veya AI API hata verebilir.

Bu yüzden mutlaka:

* Seed demo data oluşturun.
* En az 3 örnek haber hazırlayın.
* AI analiz sonuçlarını cache’leyin.
* Demo mod ekleyin.
* “API çalışmazsa sistem demo verisiyle açılır” mantığı kurun.

Örnek dosyada kullanılabilecek haber bağlantıları verilmiş; bunlar demo datası için iyi başlangıç noktasıdır. 

---

# 6. Güvenlik ve Uyumluluk

Mutlaka dikkat edin:

* API key frontend’e yazılmamalı.
* `.env` kullanılmalı.
* API key GitHub’a commit edilmemeli.
* RSS/API öncelikli gidilmeli.
* Robots.txt ihlal edecek scraping yapılmamalı.
* Tam haber metni yerine özet + kaynak linki saklanmalı.
* Loglarda API key veya hassas veri görünmemeli.

Uyumluluk tarafında robots.txt, telif için özet + link yaklaşımı, loglama ve izlenebilirlik özellikle vurgulanıyor. 

---

# 7. README’de Mutlaka Olmalı

README eksik olursa proje zayıf görünür.

README içeriği:

```txt
1. Proje adı
2. Problem tanımı
3. Çözüm özeti
4. Kullanılan teknolojiler
5. Kurulum adımları
6. .env örneği
7. Örnek RSS kaynakları
8. AI prompt örneği
9. JSON çıktı şeması
10. BIOS-fit skor formülü
11. Graph View açıklaması
12. Demo verisi açıklaması
13. Bilinen limitler
14. V2 yol haritası
```

---

# 8. Sunumda Vurgulanacak Ana Cümleler

Kullanılabilecek güçlü cümleler:

```txt
Bu proje sadece haberleri listelemez; haberlerden iş geliştirme fırsatı çıkarır.
```

```txt
AI sadece özet üretmez; şirket, lokasyon, sektör ve olay tipi gibi aksiyona dönüşebilecek alanları çıkarır.
```

```txt
BIOS-fit skoru sayesinde kullanıcı yüzlerce haber arasından gerçekten önemli fırsatlara odaklanır.
```

```txt
Opportunity Graph ile sistem zamanla şirket, sektör ve lokasyon bazlı bir endüstriyel istihbarat hafızasına dönüşür.
```

---

# 9. Öncelik Sırası

## 1. Önce Bitirilecekler

* RSS ekleme/silme/listeleme
* Haber çekme
* Dedup
* AI JSON analizi
* BIOS-fit skor
* Haber kartları
* Arama/filtre
* Detay ekranı
* Kalıcılık
* Demo data

## 2. Sonra Eklenecekler

* Graph View
* Markdown export
* Top fırsatlar alanı
* CSV export
* Dark mode
* Kaynak sağlık durumu
* Confidence uyarısı

## 3. Vakit Kalırsa

* Otomatik periyodik yenileme
* Şirket timeline
* Basit bildirim
* Harita görünümü
* CRM konsept ekranı

---

# 10. Son Kontrol Listesi

## Ürün

* [ ] Kullanıcı RSS ekleyebiliyor.
* [ ] RSS listesi kalıcı.
* [ ] Haberler çekiliyor.
* [ ] Aynı haber tekrar gösterilmiyor.
* [ ] AI analiz çalışıyor.
* [ ] JSON validate ediliyor.
* [ ] Skor hesaplanıyor.
* [ ] Kartlarda skor rengi var.
* [ ] Filtreleme çalışıyor.
* [ ] Arama çalışıyor.
* [ ] Detay ekranı var.
* [ ] Kaynağa git linki var.
* [ ] Demo data var.

## AI

* [ ] Event type doğru enum’dan geliyor.
* [ ] Eksik alanlar `null`.
* [ ] Türkçe özet var.
* [ ] Confidence var.
* [ ] Assumptions var.
* [ ] Skor gerekçesi var.
* [ ] Hatalı JSON sistemi bozmuyor.

## UI/UX

* [ ] Dashboard sade.
* [ ] Haber kartları okunabilir.
* [ ] Loading state var.
* [ ] Empty state var.
* [ ] Hata mesajları anlaşılır.
* [ ] Mobil uyumlu.
* [ ] Dark mode varsa düzgün çalışıyor.

## Graph / Markdown

* [ ] Her haberden Markdown üretilebiliyor.
* [ ] Şirket, lokasyon, sektör, olay tipi node’ları var.
* [ ] Graph ayrı sekmede.
* [ ] Graph ana akışı bozmayacak kadar sade.
* [ ] Obsidian mantığı sunumda “kurumsal hafıza” olarak anlatılıyor.

## Teslim

* [ ] README hazır.
* [ ] Kurulum adımları yazılmış.
* [ ] API key açıklaması var.
* [ ] Demo linki veya video var.
* [ ] Örnek RSS listesi var.
* [ ] 3 örnek haber üzerinde skor gösterilmiş.
* [ ] Sunum 5–7 slayt.

---

# 11. Net Sonuç

Bu projede ana hedef:

```txt
Çalışan RSS + AI + Skor + Dashboard MVP
```

Fark yaratan katman:

```txt
Markdown not üretimi + Obsidian benzeri Opportunity Graph
```

Yapılmaması gereken ana hata:

```txt
Graph, CRM, OpenSearch, harita gibi bonuslara dalıp ana akışı eksik bırakmak.
```

En güçlü sunum mesajı:

```txt
BIOS Signal Radar, Avrupa sanayi haberlerini AI ile analiz ederek şirket, lokasyon, sektör ve olay tipi ilişkilerinden oluşan yaşayan bir fırsat grafına dönüştürür.
```

