# Avrupa Fabrika Taşıma Haber Tarama Ajanı  
Teknik İş Paketi (SOW) + Prompt Setleri + JSON Şemaları  
BIOS-Fit Skor Modeli + CRM Entegrasyon Senaryosu

BIOS Endüstriyel Relokasyon Perspektifi | Doküman Sürümü: v1.0

## 1\. Teknik İş Paketi (SOW) – Kapsam ve Teslimatlar

### 1.1 Amaç

Avrupa genelinde fabrika taşıma/kapasite kaydırma/yatırım/tesis kapanışı gibi endüstriyel relokasyon sinyallerini çok dilli kaynaklardan otomatik olarak toplayan; sınıflandıran, yapılandırılmış veri çıkaran, BIOS-fit skorlayan ve yüksek skorları CRM’e aksiyon olarak ileten bir yapay zekâ ajanının geliştirilmesi.

### 1.2 Kapsam (In-Scope)

*   Kaynak yönetimi: RSS, News API benzeri indeksler, şirket IR/basın bülteni sayfaları, teşvik ajansları, ihale portalları (uyumlu olanlar).
*   Collector: zamanlayıcı (hourly/daily), rate-limit, hata yönetimi, dedup (kopya haber birleştirme).
*   Normalizer: HTML temizleme, dil tespiti, metadata çıkarımı, standartlaştırılmış metin formatı.
*   AI Processor: olay tipi sınıflandırma, entity extraction, from→to lokasyon çıkarımı, özetleme, BIOS-fit skor.
*   Veri katmanı: PostgreSQL + (opsiyonel) arama indeksi (OpenSearch).
*   Dashboard (MVP): filtreleme (ülke, sektör, şirket, olay tipi), Top fırsatlar listesi, detay sayfası.
*   Bildirim: skor eşiklerine göre e-posta/Teams/Slack uyarıları.
*   CRM entegrasyonu: yüksek skorlar için Lead/Opportunity/Task oluşturma, linkleme ve geri bildirim döngüsü.
*   Audit/log: her kayıt için kaynak, zaman, sürüm, karar izi ve güven puanı.

### 1.3 Kapsam Dışı (Out-of-Scope) – v1

*   Kapalı/ücretli veri tabanlarının lisanslanması (ayrı satın alma gerektirir).
*   Robots.txt veya kullanım şartları izin vermeyen sitelerin scraping’i.
*   Sosyal medya (LinkedIn/Twitter) otomatik kazıma (platform kuralları nedeniyle v1’de yok).
*   Tam otomatik teklif oluşturma ve müşteri ile doğrudan iletişim (onay mekanizması olmadan).

### 1.4 Fazlar ve Zaman Planı (MVP)

*   Faz 0 (1 hafta): Kapsam netleştirme, kaynak listesi v1, veri şeması, skor kriterleri ve kabul kriterleri.
*   Faz 1 (2 hafta): Collector + Normalizer + DB; dedup; temel dashboard iskeleti.
*   Faz 2 (1–2 hafta): AI Processor (prompt setleri, JSON çıktı), skor motoru, bildirimler.
*   Faz 3 (1 hafta): CRM entegrasyonu, kullanıcı kabul testleri (UAT), canlıya geçiş ve dokümantasyon.

### 1.5 Kabul Kriterleri (Acceptance Criteria)

*   Günlük taramada aynı haberin en fazla 1 kayıt olarak tutulması (dedup).
*   Her kayıt için: olay tipi, şirket, en az 1 lokasyon ve 0–100 BIOS-fit skor alanlarının dolu olması.
*   Top fırsatlar: skor ≥ 80 eşiklerinde bildirim üretimi ve dashboard’da listelenmesi.
*   Çok dilli içerikte (EN/DE/FR/PL/IT/ES): dil tespiti ve minimum tutarlı sınıflandırma.
*   CRM’e aktarılan kayıtların: kaynak linki, özet, skor, olay tipi ve önerilen aksiyon ile oluşturulması.
*   İzlenebilirlik: her kayıtta kaynak URL, çekim zamanı, işlem sürümü ve hata logları.

### 1.6 NFR – Performans, Güvenlik, Operasyon

*   Performans: 150 kaynağa kadar günde 2–4 çekim döngüsünde stabil çalışma.
*   Güvenlik: API anahtarları secret manager’da; rol bazlı erişim; loglarda hassas veri maskeleme.
*   Uyumluluk: robots.txt ve site şartlarına uyum; telif için tam metin yerine özet + link yaklaşımı.
*   Operasyon: izleme (healthcheck), retry/backoff, hata oranı raporu; yedekleme (DB günlük).

## 2\. Prompt Setleri ve JSON Çıktı Şemaları

### 2.1 Prompt Tasarım İlkeleri

Tüm LLM çağrıları JSON üretmek zorundadır. Şema dışı alan üretimi yasaktır. Belirsiz alanlarda 'null' kullanılmalı; güven puanı ve gerekçe yazılmalıdır. Çıktı dili Türkçe; özel isimler orijinal dilde korunur.

### 2.2 Prompt Seti – Olay Tipi Sınıflandırma

  
SEN: Endüstriyel relokasyon istihbaratı çıkaran bir analistsin.  
GÖREV: Aşağıdaki metinden olay tipini (event\_type) belirle ve gerekçe yaz.  
KURALLAR:  
\- Sadece JSON döndür.  
\- event\_type şu değerlerden biri olmalı:  
\["relocation","closure","downsizing","expansion","new\_plant","tender","capex\_fdi","supply\_chain\_shift","other"\]  
\- Emin değilsen other seç ve confidence düşük ver.  
  
METİN:  
{{article\_text}}  

### 2.3 Prompt Seti – Bilgi Çıkarımı (Entity & Event Extraction)

  
SEN: BIOS için fırsat çıkaran bir endüstriyel relokasyon analistsin.  
GÖREV: Metinden şirket, lokasyon(lar), from→to ilişkisi, sektör, hat/ekipman tipi, zaman çizelgesi,  
CAPEX/istihdam gibi sayısal bilgileri çıkar.  
KURALLAR:  
\- Sadece JSON döndür (aşağıdaki şemaya uygun).  
\- Bulamadığın alanları null bırak.  
\- Olası/ima edilen bilgiler için assumptions alanında not düş ve confidence düşür.  
  
METİN:  
{{article\_text}}  

### 2.4 Prompt Seti – BIOS-Fit Skor ve Aksiyon Önerisi

  
SEN: BIOS iş geliştirme danışmanısın.  
GÖREV: Çıkarılmış yapısal veriye göre BIOS-fit skor (0-100) ver ve en uygun aksiyonu öner.  
KURALLAR:  
\- Sadece JSON döndür.  
\- Skor gerekçesi kısa ve net olsun.  
\- Aksiyon türleri: \["monitor","reach\_out","request\_docs","propose\_site\_visit","partner\_search","tender\_watch"\]  
  
GİRDİ JSON:  
{{extracted\_json}}  

### 2.5 JSON Çıktı Şeması – ArticleRecord (v1)

  
{  
"source": {  
"publisher": "string",  
"url": "string",  
"retrieved\_at\_utc": "string (ISO8601)",  
"language": "string (ISO639-1)"  
},  
"article": {  
"title": "string",  
"published\_at\_utc": "string (ISO8601|null)",  
"text\_summary\_tr": "string",  
"event\_type": "string (enum)",  
"confidence": 0.0  
},  
"entities": {  
"company": {"name": "string", "ticker": "string|null"},  
"countries": \["string"\],  
"cities\_sites": \["string"\],  
"from\_location": "string|null",  
"to\_location": "string|null"  
},  
"industry": {  
"sector": "string|null",  
"subsector": "string|null",  
"line\_type": "string|null",  
"equipment\_keywords": \["string"\]  
},  
"signals": {  
"capex\_usd": "number|null",  
"jobs\_impact": "integer|null",  
"timeline": "string|null"  
},  
"bios\_fit": {  
"score": 0,  
"score\_confidence": 0.0,  
"rationale\_tr": "string",  
"recommended\_action": "string (enum)",  
"recommended\_next\_step\_tr": "string"  
},  
"assumptions": \["string"\],  
"raw\_hash": "string"  
}  

## 3\. BIOS-Fit Skor Matematiği (Formüllü)

### 3.1 Değişken Tanımları (0–1 Normalize)

*   T = Teknik Karmaşıklık (robot/PLC/safety/commissioning varlığı)
*   R = Relokasyon Doğrudanlığı (relocation/line transfer ise yüksek; sadece yatırım haberi ise orta)
*   G = Coğrafi Uygunluk (BIOS erişimi, vize/lojistik kolaylığı, geçmiş proje sinyali)
*   S = Sektör Önceliği (otomotiv, beyaz eşya, enerji/batarya, kimya vb.)
*   U = Zaman Penceresi (0–18 ay yüksek; 18–36 ay orta; belirsiz düşük)
*   C = Kaynak Güveni (IR/press release yüksek; saygın medya orta; blog düşük)
*   V = Proje Hacmi (capex, kapasite, ekipman büyüklüğü; yoksa proxy)

### 3.2 Skor Formülü

Ağırlıklı skor (0–100):  
Score = 100 \* (0.22\*T + 0.18\*R + 0.15\*G + 0.12\*S + 0.12\*U + 0.11\*C + 0.10\*V)  
  
Skor güveni (0–1):  
ScoreConfidence = min(1, 0.6\*C + 0.4\*DataCompleteness)  
DataCompleteness = (dolu kritik alan sayısı / kritik alan sayısı)  
Kritik alanlar: company, event\_type, country, (from/to veya site), sector/line\_type.

### 3.3 Eşikler ve Aksiyon Haritası

\- Score ≥ 80: 'reach\_out' veya 'request\_docs' + anlık bildirim  
\- 65 ≤ Score < 80: 'monitor' + haftalık rapor  
\- 50 ≤ Score < 65: 'tender\_watch' veya 'partner\_search'  
\- Score < 50: arşivle (yalnızca arama için)  
  
Ayrıca event\_type 'tender' ise Score ne olursa olsun 'tender\_watch' tetiklenebilir.

## 4\. CRM’e Bağlama Senaryosu (Lead/Opportunity/Task Akışı)

### 4.1 Genel Akış

*   Ajan yüksek skorlu fırsat kaydı üretir (ArticleRecord).
*   Workflow Engine, eşik ve kurallara göre CRM aksiyonu seçer.
*   CRM’de 'Company' (hesap) varsa ilişkilendir; yoksa yeni Account/Company oluştur.
*   Skor ≥ 80 ise: Lead/Opportunity aç + 'Next Step' görevi (Task) oluştur.
*   Haber linki, özet, skor, event\_type ve önerilen aksiyon CRM kaydına yazılır.
*   Satış ekibi geri bildirim alanını işaretler (Qualified/Disqualified/Follow-up).
*   Geri bildirim, model iyileştirme için etiket olarak sisteme geri akar.

### 4.2 CRM Nesneleri ve Alan Eşlemesi (Öneri)

*   Account/Company: company.name, country/city (varsa)
*   Lead/Opportunity: event\_type, sector, line\_type, from\_location, to\_location, timeline
*   Custom Fields: bios\_fit.score, bios\_fit.score\_confidence, source.publisher, source.url
*   Task (BD Aksiyonu): recommended\_action + recommended\_next\_step\_tr + due date (7–14 gün)
*   Attachment/Note: özet metni ve çıkarılan ana sinyaller

### 4.3 Entegrasyon Seçenekleri

Seçenek A (Önerilen): CRM REST API + Webhook  
\- Workflow Engine, CRM API’ye kayıt açar/günceller.  
\- CRM tarafında webhook ile durum değişiklikleri (Qualified vb.) geri alınır.  
  
Seçenek B: iPaaS (Make/Zapier/Power Automate)  
\- Hızlı kurulum; ancak yüksek hacimde maliyet ve kontrol sınırlı.  
  
Seçenek C: Mesaj Kuyruğu (Kafka/RabbitMQ) + Integration Service  
\- Kurumsal ölçek; çok sistemli mimariler için.

### 4.4 Veri Kalitesi ve Satış Süreci Notları

CRM’e otomatik kayıt atarken kalite kontrol kritik olur:  
\- Aynı şirket için çoklu haber birleşimi (threading)  
\- Bölgesel BD sorumlusu ataması (ülke/sektöre göre)  
\- SLA: yüksek skor fırsatlar 48 saat içinde değerlendirilir  
\- Satış geri bildirimi modele dönerek yanlış pozitifleri azaltır
