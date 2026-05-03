
# BSMT HACKATHON

## Yarışma Konusu ve Beklentiler Raporu

## Avrupa Endüstriyel Haber Tarama Ajanı

#### RSS Tabanlı, Yapay Zekâ Destekli, Kullanıcı Dostu Arayüz





## 1. Yarışma Özeti

BSMT Hackathon kapsamında yarışmacılardan; Avrupa genelinde fabrika taşıma, tesis kapanışı, yeni
yatırım ve kapasite genişletme gibi endüstriyel haberleri otomatik olarak takip edebilen, yapay zekâ
ile sınıflandıran ve kullanıcıya sade bir arayüz üzerinden sunan bir uygulama geliştirmesi
beklenmektedir.

Sistemin temel mantığı şudur: Kullanıcı arayüze istediği haber sitelerinin RSS bağlantılarını ekler.
Uygulama bu RSS kaynaklarından haberleri çeker, bir yapay zekâ modeli (LLM) ile haberleri analiz eder,
endüstriyel relokasyon (taşıma) sinyali içerip içermediğini tespit eder, içeriği özetler ve sonuçları
kart/liste şeklinde kullanıcıya gösterir.

Yarışma 24 saat ile sınırlıdır (15:00 başlangıç → ertesi gün 15:00 proje teslim/sunum). Bu nedenle
yarışmacılardan kurumsal seviyede karmaşık bir mimari değil; çalışan, demoya hazır bir MVP
(Minimum Viable Product) beklenmektedir. Değerlendirmede çalışırlık, arayüz kalitesi, yapay zekâ
entegrasyonunun isabeti ve kullanıcı deneyimi öne çıkacaktır.

Bu doküman; problem tanımını, fonksiyonel beklentileri, teknik serbestliği, önerilen mimariyi, arayüz
beklentilerini, değerlendirme kriterlerini, BSMT Hackathon resmi program akışına göre saat bazlı
çalışma planını ve teslim formatını net şekilde tanımlar.

## 2. Problem Tanımı

Sanayi şirketleri ve iş geliştirme ekipleri, Avrupa'da hangi fabrikanın taşındığını, hangi tesisin
kapandığını veya nerede yeni yatırım açıklandığını manuel olarak takip etmek zorundadır. Bu süreç
yavaş, dağınık ve emek yoğundur. Onlarca farklı haber sitesini her gün gezmek pratik değildir.

Bu hackathonda yarışmacılardan, bu sorunu çözen sade bir araç geliştirmeleri istenmektedir. Aracın
görevi şudur:

```
 Kullanıcının seçtiği haber kaynaklarını (RSS) otomatik olarak takip etmek.
 Gelen haberleri yapay zekâ ile okumak ve sınıflandırmak (taşıma, kapanış, genişleme, yeni
yatırım, ihale gibi).
 Şirket adı, lokasyon (nereden → nereye), sektör gibi temel bilgileri çıkartmak.
 Haberi kısa Türkçe özet ile birlikte arayüzde göstermek.
 Kullanıcının önemsizleri filtreleyip önemli olanlara odaklanmasını sağlamak.
```
Yarışmacılar bu çekirdek senaryoyu çalışır hâlde teslim ettikleri sürece görev tamamlanmış sayılır.
Ekstra özellikler bonus puan getirir.


```
Smart Inspection with AI
Pro Sicht Yapay Zekâ Yazılım Ar-Ge ve Proje Danışmanlık Sanayi ve Ticaret A.Ş.
```
## 3. Yarışma Kapsamı

### 3.1. Kapsam İçi (Yapılması Beklenen)

```
 RSS yönetimi: Kullanıcı arayüzden RSS bağlantısı ekleyebilmeli, listeleyebilmeli ve istediğini
silebilmelidir. Listenin uygulama yeniden açıldığında kaybolmaması beklenir (yerel dosya,
SQLite, JSON, IndexedDB gibi basit bir kalıcılık yeterlidir).
 Haber çekme: Eklenen RSS kaynaklarından haberleri çeken bir mekanizma kurulmalıdır.
Manuel "Yenile" butonu yeterlidir; periyodik (cron) çalışma bonus puandır.
 AI ile analiz: Her haber için yapay zekâ modeli kullanılarak en az şu çıktılar üretilmelidir: olay
tipi etiketi, kısa Türkçe özet, şirket adı (varsa), lokasyon (varsa) ve 0–100 arasında bir alaka
skoru.
 Kullanıcı arayüzü: Haberlerin liste/kart şeklinde görüntülendiği, filtre ve aramanın çalıştığı,
modern ve sade bir arayüz sunulmalıdır.
 Detay görünümü: Bir habere tıklandığında özet, etiket, skor, kaynak linki ve çıkarılan
bilgilerin gösterildiği bir detay alanı bulunmalıdır.
```
### 3.2. Kapsam Dışı (Yapılması Beklenmeyen)

```
 Tam kurumsal CRM entegrasyonu (Salesforce, HubSpot vb.) — sadece konsept anlatımı
yeterlidir.
 Çok dilli gelişmiş NLP modelinin sıfırdan eğitilmesi — hazır LLM API kullanımı serbesttir.
 Üretim seviyesinde ölçeklenebilirlik, Kubernetes, mikroservis ayrıştırması.
 Robots.txt'i ihlal edecek scraping işlemleri (sadece RSS / herkese açık API).
 Mobil native uygulama (Web yeterlidir; mobil uyumlu web bonus puandır).
```
## 4. Fonksiyonel Gereksinimler

Aşağıdaki tabloda zorunlu (Must) ve isteğe bağlı (Nice to Have) gereksinimler listelenmiştir.
Yarışmacıların önce zorunluları bitirip ardından opsiyonellere geçmesi tavsiye edilir.

```
Kod Gereksinim Öncelik
F1 Kullanıcı yeni RSS kaynağı ekleyebilir (URL girer, isim/etiket atayabilir) Must
F2 Eklenen RSS kaynakları listelenir ve silinebilir Must
F3 RSS bağlantılarının geçerliliği eklenmeden önce kontrol edilir (hata
mesajı gösterilir)
```
```
Must
```
```
F4 Tüm kaynaklardan haberler çekilir (manuel yenileme butonu) Must
F5 Aynı haber tekrar gösterilmez (URL veya başlık bazlı dedup) Must
```

```
Smart Inspection with AI
Pro Sicht Yapay Zekâ Yazılım Ar-Ge ve Proje Danışmanlık Sanayi ve Ticaret A.Ş.
```
```
Kod Gereksinim Öncelik
F6 Her haber için AI özet ve sınıflandırma üretilir Must
F7 Olay tipi etiketleri belirlenir (relocation / closure / expansion /
new_plant / tender / other)
```
```
Must
```
```
F7b BIOS-fit skoru bölüm 7.4'teki formüle göre 0–100 aralığında üretilir;
eşik renk kodu (yeşil/mavi/sarı/gri) kart üzerinde gösterilir
```
```
Must
```
```
F8 Haberler skor, tarih, etiket veya kaynağa göre filtrelenebilir Must
F9 Anahtar kelime ile arama çalışır Must
F10 Detay sayfasında çıkarılan bilgiler (şirket, lokasyon vb.) görüntülenir Must
F11 RSS listesi uygulama kapatılıp açıldığında korunur (kalıcılık) Must
F12 Otomatik periyodik yenileme (örn. her X dakikada bir) Nice to Have
F13 Yüksek skorlu haberler için bildirim/öne çıkarma Nice to Have
F14 Haberin orijinal dilinden Türkçe özet üretimi Nice to Have
F15 Karanlık mod (dark mode) Nice to Have
F16 CSV / Excel olarak dışa aktarım Nice to Have
F17 Şirket bazlı zaman çizelgesi (timeline) Nice to Have
F18 Harita üzerinde "nereden → nereye" gösterimi Nice to Have
```
## 5. Kullanıcı Arayüzü Beklentileri

Arayüz, bu yarışmanın merkezindedir. Yarışmacılar yalnızca "çalışan bir backend" değil; teknik bilgisi
olmayan bir kullanıcının dahi 30 saniyede anlayıp kullanabileceği bir ekran sunmalıdır. Aşağıda
beklenen ekranlar açıklanmıştır.

### 5.1. Ana Ekran (Haber Akışı)

```
 Üst kısımda arama kutusu ve filtre alanları (etiket, kaynak, tarih, minimum skor).
 Sol veya sağ tarafta RSS kaynak yönetimi paneli.
 Orta alanda haberlerin kart/liste görünümü: başlık, kaynak, tarih, etiket, kısa özet, skor.
 Sağ üstte "Yenile" butonu ve son güncelleme zamanı.
```

```
Smart Inspection with AI
Pro Sicht Yapay Zekâ Yazılım Ar-Ge ve Proje Danışmanlık Sanayi ve Ticaret A.Ş.
```
### 5.2. RSS Yönetim Paneli

```
 "Yeni RSS Ekle" butonu ve URL giriş alanı.
 Eklenmiş kaynakların listesi: kaynak ismi, URL, son çekim zamanı, çalışıyor mu durumu.
 Her kaynağın yanında sil butonu.
 Geçersiz RSS girişinde kullanıcıya anlaşılır hata mesajı.
```
### 5.3. Haber Detay Görünümü

```
 Haberin başlığı, kaynak adı, yayın tarihi, orijinal link.
 Yapay zekâ tarafından üretilmiş Türkçe özet.
 Etiket (olay tipi), şirket, lokasyon (from → to), sektör, alaka skoru.
 "Kaynağa Git" linki orijinal habere yönlendirir.
```
### 5.4. Tasarım İlkeleri

```
 Sade, temiz ve okunabilir tipografi.
 Etiketlere renk kodlaması: ör. relocation = mavi, closure = kırmızı, expansion = yeşil.
 Boş durumlarda anlamlı placeholder metni ("Henüz RSS kaynağı eklemediniz" gibi).
 Yükleme sırasında loading göstergesi (spinner / skeleton).
 Hata durumlarında kullanıcıya teknik olmayan dilde geri bildirim.
```
## 6. Önerilen Teknik Mimari

Bu mimari önerisidir; yarışmacılar farklı bir yapı kurabilir. Önemli olan akışın çalışmasıdır.

### 6.1. Yüksek Seviyeli Akış

1. Kullanıcı arayüzden bir RSS URL'si ekler ve bu URL kalıcı olarak saklanır.
2. Kullanıcı "Yenile" butonuna bastığında veya zamanlayıcı tetiklendiğinde, sistem tüm RSS
    kaynaklarını paralel olarak çeker.
3. Çekilen ham haberler dedup (kopya eleme) işleminden geçirilir.
4. Yeni haberlerin başlık + özeti LLM'e gönderilir; LLM yapılandırılmış JSON döndürür (etiket,
    özet, şirket, lokasyon, skor).
5. Sonuçlar veritabanına / dosyaya yazılır.
6. Arayüz veriyi çeker ve filtre/arama ile birlikte kullanıcıya sunar.


```
Smart Inspection with AI
Pro Sicht Yapay Zekâ Yazılım Ar-Ge ve Proje Danışmanlık Sanayi ve Ticaret A.Ş.
```
### 6.2. Önerilen Teknolojiler (Serbest)

```
Katman Önerilen Seçenekler
Frontend React, Next.js, Vue, Svelte, ya da basit HTML+JS
Backend Node.js (Express/Fastify), Python (FastAPI/Flask), .NET, Go
RSS Parser feedparser (Python), rss-parser (Node), Cheerio
Kalıcılık SQLite, JSON dosyası, IndexedDB, MongoDB Atlas (free tier)
AI / LLM OpenAI API, Claude API, Gemini API, Ollama (lokal model)
UI Bileşenleri TailwindCSS, shadcn/ui, Material UI, Bootstrap
Hosting (opsiyonel) Vercel, Netlify, Render, Railway, lokal demo
```
### 6.3. Bileşen Sorumlulukları

```
 Collector: RSS URL listesinden haberleri çeker, başlık + link + yayın tarihi + içerik özetini
toplar.
 Normalizer: HTML etiketlerini temizler, dil tespiti yapar, dedup için hash üretir.
 AI Processor: LLM çağrısı yapar, prompt'a göre JSON çıktı üretir, hata yönetimi sağlar.
 Storage: RSS kaynaklarını ve işlenmiş haberleri saklar.
 API / Servis: Frontend'e haber listesi, RSS yönetimi ve detay endpointleri sunar.
 UI: Listeleme, filtreleme, arama, kaynak yönetimi ve detay ekranını sunar.
```
## 7. Yapay Zekâ Entegrasyonu Detayı

Yarışmacılar tercih ettikleri herhangi bir LLM'i kullanabilir. Önemli olan modelin tutarlı ve
yapılandırılmış JSON çıktı üretmesidir.

### 7.1. Beklenen JSON Çıktı Şeması

Her haber için AI'dan aşağıdaki yapıda bir JSON döndürmesi beklenir. Eksik bulunan alanlar null olarak
bırakılmalıdır.

{ "event_type": "relocation | closure | expansion | new_plant | tender | other",
"summary_tr": "Türkçe 2–4 cümlelik özet", "company": "Şirket adı veya null",
"from_location": "Çıkış lokasyonu veya null", "to_location": "Hedef lokasyon
veya null", "sector": "Sektör veya null", "score": 0, "confidence": 0.0 }

### 7.2. Örnek Prompt (Türkçe)

Sen bir endüstriyel haber analistsin. Aşağıdaki haber metninden olay tipini,
şirket adını, lokasyonları ve sektörü çıkar. Haberin Avrupa'daki bir fabrika


```
Smart Inspection with AI
Pro Sicht Yapay Zekâ Yazılım Ar-Ge ve Proje Danışmanlık Sanayi ve Ticaret A.Ş.
```
taşıması, kapanışı, genişlemesi veya yeni yatırımı ile ilgili olup olmadığına göre
0 – 100 arası alaka skoru ver. SADECE JSON döndür, başka hiçbir şey yazma.
Bilmediğin alanları null bırak. Özeti Türkçe yaz. METIN: {{article_text}}

### 7.3. Olay Tipi Etiketleri

```
Etiket Anlamı
relocation Bir fabrikanın / üretim hattının başka bir lokasyona taşınması
closure Tesis kapanışı, küçülme, üretimi durdurma
expansion Mevcut tesisin büyütülmesi, kapasite artışı
new_plant Yeni fabrika / greenfield yatırım duyurusu
tender İhale, tedarik veya satın alma duyurusu
other Yukarıdakilerin hiçbiri / belirsiz
```
### 7.4. BIOS-Fit Skor Modeli (Matematiksel Tanım)

BIOS-fit skoru, bir haberin Pro Sicht / BIOS perspektifinden "iş geliştirme fırsatı" olarak ne kadar değerli
olduğunu 0–100 ölçeğinde ifade eden ağırlıklı bir ölçüttür. Yarışmacılar bu skoru aşağıda tanımlanan
formüle göre hesaplamak zorundadır. Skor, AI tarafından üretilen 'score' alanına yazılır.

Skor; haberin neyle ilgili olduğuna (olay tipi), aktörlerin ne kadar netleştiğine (şirket, lokasyon, sektör),
olayın nerede gerçekleştiğine (coğrafya) ve haber kaynağının ne kadar güvenilir olduğuna göre üretilir.
Aşağıdaki beş bileşen kullanılır.

#### 7.4.1. Bileşenler ve Puanlama Kuralları

Her bileşen 0–1 arasında bir alt puan üretir. Bu alt puanlar deterministik kurallarla hesaplanır; AI'a
yorum yaptırılmaz, sadece çıkarım sonucundaki alanlar tabloya bakılarak puanlanır.

```
Bileşen Semb
ol
```
```
Puanlama Kuralı (0–1)
```
```
Olay Tipi (Event Type) E relocation = 1.00 | new_plant = 0.90 | expansion = 0.75 |
tender = 0.55 | closure = 0.45 | other = 0.
Aktör Netliği (Actor Clarity) A company net (+0.40) + from_location net (+0.25) +
to_location net (+0.25) + sector net (+0.10). Toplam 0– 1
arası.
Coğrafya (Geography) G Avrupa içi (AB + Birleşik Krallık + Türkiye + Balkanlar) = 1.
| Avrupa komşuluğu (Rusya, Kuzey Afrika) = 0.50 | Diğer =
0.10 | Bilinmiyor = 0.
```

```
Smart Inspection with AI
Pro Sicht Yapay Zekâ Yazılım Ar-Ge ve Proje Danışmanlık Sanayi ve Ticaret A.Ş.
```
```
Bileşen Semb
ol
```
```
Puanlama Kuralı (0–1)
```
```
Zaman Penceresi (Timeline) T 0 – 6 ay içinde / "announced", "will move", "in Q" gibi yakın
zaman = 1.00 | 6–18 ay = 0.70 | 18–36 ay = 0.40 |
Belirtilmemiş = 0.
Kaynak Güveni (Source
Trust)
```
```
C Şirketin resmi sitesi / IR sayfası = 1.00 | Saygın haber ajansı
(Reuters, Bloomberg, FT, Handelsblatt) = 0.85 | Sektörel
yayın = 0.70 | Genel haber sitesi = 0.55 | Blog / forum =
0.
```
#### 7.4.2. Ağırlıklı Skor Formülü

Beş bileşen aşağıdaki ağırlıklarla birleştirilir. Ağırlıklar toplamı 1.00'dır; nihai çarpan 100 olduğu için
skor doğal olarak 0–100 aralığında çıkar.

```
Score = 100 × ( 0.30·E + 0.25·A + 0.20·G + 0.15·T + 0.10·C )
```
Ağırlıkların gerekçesi: Olay tipinin (E) ne olduğu en belirleyicidir çünkü ihale haberi ile fabrika taşıma
haberi BIOS için aynı değerde değildir. Aktör netliği (A) ikinci önceliktedir; çünkü hangi şirketin nereden
nereye gittiği bilinmiyorsa fırsat eyleme geçirilemez. Coğrafya (G), Pro Sicht'in operasyon alanı Avrupa
olduğu için kritik bir filtredir. Zaman penceresi (T) ve kaynak güveni (C) ise sıralama amaçlı ince ayar
bileşenleridir.

#### 7.4.3. Güven Puanı (Confidence)

Skorun yanında bir de güven puanı (confidence, 0–1 arası) üretilir. Güven, skorun ne kadar dolu veriyle
hesaplandığını gösterir. Beş kritik alanın doluluk oranıdır:

```
confidence = ( dolu_alan_sayısı / 5 )
```
Sayılan kritik alanlar şunlardır: company, from_location, to_location, sector, event_type. Beşi de
doluysa confidence = 1.00; ikisi doluysa 0.40 olur. Confidence değeri 0.40'ın altındaysa skor 0.5 ile
çarpılarak yumuşatılır (cezalandırılır), çünkü eksik veriyle yüksek skor üretmek yanıltıcıdır:

```
if confidence < 0.40 then Score = Score × 0.
```
#### 7.4.4. Karar Eşikleri (Aksiyon Haritası)

Skor üretildikten sonra arayüzde renk ve aksiyon önerisi göstermek için aşağıdaki eşikler
kullanılmalıdır. Yarışmacıların arayüzünde haber kartları bu renklere göre işaretlenmelidir.

```
Skor Aralığı Etiket Renk Önerilen Aksiyon
80 – 100 Yüksek Fırsat Yeşil Hemen iletişime geç (reach_out) / dosya
talep et
65 – 79 İzlenecek Mavi Takip listesine al, haftalık raporda göster
```

```
Smart Inspection with AI
Pro Sicht Yapay Zekâ Yazılım Ar-Ge ve Proje Danışmanlık Sanayi ve Ticaret A.Ş.
```
```
Skor Aralığı Etiket Renk Önerilen Aksiyon
50 – 64 Şartlı İlgi Sarı Tender ise ihale takibi, değilse partner
araması
0 – 49 Düşük Alaka Gri Arşivle, sadece arama için tut
```
#### 7.4.5. Hesaplama Örneği

Aşağıda örnek bir haberin skor hesaplaması adım adım gösterilmiştir. Bu örnek yarışmacılar için
referans niteliğindedir.

_Haber: "BMW, Münih'teki bir üretim hattını Macaristan'ın Debrecen tesisine taşıyor; süreç 2026'nın ilk
çeyreğinde tamamlanacak. (Kaynak: Reuters)"_

Çıkarılan veri:

```
 event_type = relocation
 company = "BMW"
 from_location = "Münih, Almanya"
 to_location = "Debrecen, Macaristan"
 sector = "otomotiv"
 timeline = "2026 Q1" (yaklaşık 6 ay)
 kaynak = Reuters
```
Bileşen puanları:

```
 E (olay tipi = relocation) = 1.
 A (4 alan da net: 0.40 + 0.25 + 0.25 + 0.10) = 1.
 G (Almanya → Macaristan, ikisi de Avrupa) = 1.
 T (6 ay içinde) = 1.
 C (Reuters, saygın haber ajansı) = 0.
```
Score = 100 × ( 0.30·1.00 + 0.25·1.00 + 0.20·1.00 + 0.15·1.00 + 0.10·0.85 )
= 100 × ( 0.30 + 0.25 + 0.20 + 0.15 + 0.085 ) = 100 × 0.985 = 98.5 →
yuvarlanmış: 99 confidence = 5/5 = 1.00 (yumuşatma uygulanmaz) Etiket: Yüksek
Fırsat (Yeşil) Önerilen Aksiyon: reach_out

#### 7.4.6. Önemli Notlar

```
 Skor 0–100 aralığında bir tam sayı olarak yuvarlanır (Math.round).
 Yumuşatma uygulanırsa, sonuç yine 0–100 aralığında bir tam sayı olarak yuvarlanır.
 Yarışmacılar formüle yeni bir bileşen ekleyebilir veya ağırlıkları değiştirebilir; ancak
değişikliğin gerekçesi README'de belirtilmelidir.
```

```
Smart Inspection with AI
Pro Sicht Yapay Zekâ Yazılım Ar-Ge ve Proje Danışmanlık Sanayi ve Ticaret A.Ş.
```
```
 Skor mantığının tutarlı çalıştığını göstermek için yarışmacıların en az 3 adet test haberi
üzerinde çalışan örnek hesaplama sunması beklenir.
```


## 9. Değerlendirme Kriterleri

Jüri, projeleri aşağıdaki ağırlıklara göre puanlayacaktır. Toplam 100 puan üzerinden değerlendirilir.

```
Kriter Ağırlık Açıklama
Çalışırlık ve İşlevsellik 30 RSS ekleme/silme, haber çekme, AI analizi ve
listelemenin uçtan uca çalışması
Kullanıcı Arayüzü ve UX 25 Sade, modern, kullanıcı dostu tasarım;
filtre/arama akışı
Yapay Zekâ Entegrasyonunun
Kalitesi
```
```
20 Etiketlemenin doğruluğu, özet kalitesi, JSON
tutarlılığı
Kod Kalitesi ve Mimari 10 Modülerlik, okunabilirlik, hata yönetimi
Sunum ve Demo 10 Net anlatım, problem-çözüm bağı, görsel demo
(14:00–15:00 arası sunum)
Yaratıcılık ve Ekstra Özellikler 5 Bonus özellikler (harita, timeline, bildirim vb.)
```
### 9.1. Yarışma Sırasında Ek Puan Getiren Davranışlar

```
 Boş durumların ve hata mesajlarının özenle tasarlanması.
 Mobil uyumlu (responsive) arayüz.
 Karanlık / aydınlık tema desteği.
 AI promptunun belgelendirilmesi (README'de prompt örnekleri).
 Demo videosunun düzgün ve sade olması.
```
## 10. Teslim Formatı ve Kuralları

### 10.1. Teslim Edilecekler

```
 Kaynak kod: GitHub / GitLab repo linki, public veya yarışma jürisine erişim verilmiş şekilde.
 README.md: Kurulum adımları, gereken API anahtarları (varsa), kullanılan teknolojiler ve
kısa mimari açıklaması.
 Demo: Canlı bir link (Vercel/Netlify/Render) veya 2–3 dakikalık ekran kaydı videosu.
 Sunum: 5 – 7 slaytlık kısa bir sunum (PDF veya PPTX). 14:00–15:00 arası jüri önünde
sunulacaktır.
 Örnek RSS Listesi: Test için kullanılabilecek 3–5 adet endüstriyel RSS kaynağı (README
içinde).
```

```
Smart Inspection with AI
Pro Sicht Yapay Zekâ Yazılım Ar-Ge ve Proje Danışmanlık Sanayi ve Ticaret A.Ş.
```
### 10.2. Teslim Süresi

Yarışmanın resmi son teslim zamanı 14:00'tür. 14:00–15:00 arası proje teslim ve sunum oturumudur.
14:00'tan sonra yapılan commit'ler değerlendirmeye alınmaz; jüri yalnızca bu saatten önceki son
commit'i inceler.

### 10.3. Etik Kurallar

```
 Hazır şablonlar / boilerplate kullanımı serbesttir; ancak çekirdek özelliklerin yarışma
süresince yazılmış olması gerekir.
 Açık kaynak kütüphaneler kullanılabilir; lisans uyumluluğuna dikkat edilmelidir.
 Bir başkasının kodu kendi kodu gibi sunulamaz.
 RSS dışında scraping yapılması durumunda hedef sitenin robots.txt kurallarına uyulmalıdır.
```
## 11. Sıkça Sorulan Sorular

#### Hangi LLM'i kullanmalıyım?

Tercih sizin. OpenAI, Anthropic, Google, açık kaynak (Ollama, Mistral) — hepsi geçerlidir. Önemli olan
modelin JSON çıktısı tutarlı olarak üretebilmesidir.


#### Türkçe haber kaynağı kullanabilir miyim?

Evet. Konu Avrupa endüstrisi olduğu için tercihen İngilizce/Almanca kaynaklar önerilir, ancak Türkçe
RSS de kabul edilir. Çıktı dili Türkçe olmalıdır.

#### Veritabanı zorunlu mu?

Hayır. SQLite, JSON dosyası veya tarayıcı IndexedDB de yeterlidir. Önemli olan RSS listesinin uygulama
yeniden başlatıldığında kaybolmamasıdır.

#### Mobil uygulama yapabilir miyim?

Web uygulaması beklenmektedir. Mobil uyumlu (responsive) web bonus puandır. Native mobil
uygulama yapmak süre baskısı nedeniyle önerilmez.


#### Demo verisi olarak ne kullanmalıyım?

Reuters, Bloomberg, Manufacturing.net, Just-auto, IndustryWeek gibi sitelerin RSS bağlantılarını test
için kullanabilirsiniz. README'de bu listeyi paylaşmanız bekleniyor.

## 12. Sonuç ve Beklenti Özeti

BSMT Hackathon kapsamında yarışmacılardan; 24 saatlik süre içinde, kullanıcının kendi RSS
kaynaklarını yönetebildiği, yapay zekâ ile haberlerin sınıflandırıldığı, modern ve kullanıcı dostu bir web
arayüzü sunan, çalışan bir MVP teslim etmesi beklenmektedir.

Başarının üç temel ayağı şunlardır:

```
 1. Çalışan akış: Kullanıcı RSS ekler → haberler çekilir → AI işler → arayüzde anlamlı sonuç
görünür.
 2. Anlaşılır arayüz: Teknik bilgisi olmayan bir kullanıcının dahi anında kullanabileceği sade ve
modern bir UI.
 3. AI'ın isabeti: Etiketleme ve özetlemenin haberlerle tutarlı olması; gereksiz halüsinasyonun
önlenmesi.
```
Bu üç ayağı sağlayan her proje yarışmayı başarıyla tamamlamış sayılır. Geri kalan tüm özellikler ekstra
ve değerli; ancak temelin sağlam olması her zaman önceliktir.

BSMT Hackathon'da hepinize başarılar dileriz.

```
— Pro Sicht & BSMT Hackathon Komitesi
```


