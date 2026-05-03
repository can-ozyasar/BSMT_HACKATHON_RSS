
# Avrupa Fabrika Taşıma Haberleri için  
Yapay Zekâ Destekli Tarama Ajanı

Teknik Mimari Diyagramı ve Yapılacaklar Listesi (MVP + Ölçekleme)

## 1\. Teknik Mimari Diyagramı

# Sistem Akışı


[Kaynaklar]
RSS / News API / IR (Basın Bülteni) / Teşvik Ajansları / İhale Portalları
        |
        v
[Collector + Scheduler]
(Saatlik/Günlük çekim, rate-limit, robots.txt kontrolü)
        |
        v
[Normalizer]
(HTML temizleme, dil tespiti, metadata, dedup)
        |
        v
[AI Processor (LLM/NLP)]
(Sınıflandırma, bilgi çıkarımı, özet, BIOS-fit skor)
        |
        +------------------------+
        |                        |
        v                        v
[DB: PostgreSQL]          [Search: OpenSearch]
(kayıtlar,                (tam metin arama,
 ilişkiler)                filtreler)
        |                        |
        +-----------+------------+
                    v
[Rules/Workflow Engine]
(Eşikler, takip listesi, CRM aksiyonları)
        |
        v
[Dashboard + Alerts]
(Web panel, e-posta/Teams/Slack, haftalık rapor PDF)

Not: Mimari, önce MVP (Minimum Viable Product) olarak kurulup; kaynak sayısı, dil kapsamı ve workflow otomasyonları arttıkça ölçeklenecek şekilde tasarlanmıştır.

## 2\. Net Yapılacaklar Listesi

### 2.1. Hedef ve Kapsam Tanımı (Hafta 1)

*   Relokasyon sinyali tanımı: relocation/closure/expansion/tender gibi olay tiplerini netleştir.
*   Hedef ülkeler ve diller: EN, DE, FR, IT, ES, PL vb. öncelik sırası belirle.
*   BIOS-fit skor kriterleri: teknik karmaşıklık, zaman penceresi, sektör, coğrafya, kaynak güveni.
*   Çıktı formatı: Kim? Nereden? Nereye? Ne? Ne zaman? Hat tipi? Tahmini hacim? Aksiyon önerisi?

### 2.2. Kaynak Havuzu ve Toplayıcı (Hafta 1–2)

*   Kaynak listesi oluştur: RSS/News API/IR sayfaları/teşvik ajansları/ihale portalları (ilk etap 50–150 kaynak).
*   Collector servis: zamanlayıcı (cron), rate-limit, hata yönetimi, robots.txt ve site şartları kontrol yaklaşımı.
*   Dedup mekanizması: aynı haberin farklı yayıncı kopyalarını tespit (başlık+hash+benzerlik).
*   Ham içerik depolama: kaynak URL, çekim zamanı, içerik snapshot.

### 2.3. Normalizasyon ve Dil İşleme (Hafta 2)

*   HTML temizleme ve metin çıkarımı (boilerplate removal).
*   Dil tespiti ve gerekiyorsa çeviri stratejisi (önce sınıflandır, sonra gerekirse çevir).
*   Metadata standardı: tarih, yayıncı, ülke, kategori, güven skoru alanları.
*   Kayıt şeması (JSON) tasarla: LLM çıktılarıyla uyumlu tek şema.

### 2.4. AI İşleme Katmanı (Hafta 3)

*   Sınıflandırma prompt’u: relocation/closure/expansion/tender etiketleri.
*   Bilgi çıkarımı: company, from→to lokasyon, sektör, hat tipi, zaman çizelgesi, capex/headcount (varsa).
*   Özetleme: yönetici özeti (5–7 satır) + teknik özet (hat/ekipman odaklı).
*   BIOS-fit skor: 0–100 ve açıklama (neden yüksek/düşük).
*   Güven puanı: kaynak türü ve metin kesinliğine göre (ör. basın bülteni > blog).

### 2.5. Veri Tabanı, Arama ve Panel (Hafta 3–4)

*   PostgreSQL şeması: articles, entities, events, locations, scores, sources tabloları.
*   OpenSearch/Elasticsearch indeks: hızlı arama ve filtreleme (ülke, sektör, şirket, olay tipi).
*   Basit web panel: filtreler + 'Top fırsatlar' listesi + tekil haber detay sayfası.
*   Export: haftalık rapor (Word/PDF) ve CSV/Excel dışa aktarım.

### 2.6. Bildirim ve Workflow (Hafta 4)

*   Eşik tanımı: ör. skor ≥ 80 ise anlık bildirim; 60–79 haftalık rapora girer.
*   Bildirim kanalları: e-posta, Teams/Slack; konu başlığı standardı ve kısa özet.
*   Takip listesi: şirket/ülke/sektör bazlı izleme; yeniden haber gelince zincirleme bağlama.
*   CRM aksiyon taslağı: 'BD aksiyonu', 'teklif sinyali', 'site visit önerisi' gibi durumlar.

### 2.7. Uyumluluk ve Operasyon (Sürekli)

*   Robots.txt ve site şartlarına uyum; scraping yerine mümkün olduğunda RSS/API önceliği.
*   Copyright: tam metin saklama yerine özet + kaynak linki yaklaşımı.
*   Loglama ve izlenebilirlik: her çekim ve LLM kararı için audit alanları.
*   Kalite kontrol: yanlış pozitif/negatif takibi ve prompt iyileştirme döngüsü.

## 3\. MVP Başarı Kriterleri

*   Günlük taramada en az %70 doğrulukla 'relokasyon sinyali' yakalama.
*   Haftalık raporda 10–20 adet yüksek alaka düzeyli fırsat üretimi.
*   Her fırsatta: şirket, lokasyon, olay tipi ve BIOS-fit skorunun tutarlı üretimi.
*   Dedup sayesinde aynı haberin en fazla 1 kayıt olarak gösterilmesi.
