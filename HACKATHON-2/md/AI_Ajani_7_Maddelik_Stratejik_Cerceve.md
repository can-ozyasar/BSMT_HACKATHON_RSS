# Yapay Zekâ Destekli Avrupa Fabrika Taşıma  
Haber Tarama Ajanı – Kavramsal Çerçeve

7 Maddelik Stratejik ve Teknik Yaklaşım  
BIOS Endüstriyel Relokasyon Perspektifi

## 1\. Hedef Tanımı – Relokasyon Sinyali Nedir?

Ajanın yakalaması hedeflenen olaylar net şekilde tanımlanmalıdır:

*   Plant relocation / site transfer
*   Factory closure / downsizing
*   New plant / expansion (greenfield / brownfield)
*   Equipment / line transfer
*   Supply chain reconfiguration
*   CAPEX / FDI duyuruları

Her olay için şu sorular cevaplanmalıdır:

Kim? Nereden? Nereye? Ne zaman? Hangi sektör? Hangi hat? Tahmini hacim?

BIOS açısından fırsat değeri nedir?

## 2\. Veri Toplama Katmanı – Kaynak Odaklı Yaklaşım

Sürdürülebilir bir sistem için klasik web scraping yerine kaynak-odaklı toplama tercih edilmelidir.

Ana kaynak grupları:

*   Haber akışları (RSS, News API)
*   Şirket basın bültenleri ve Investor Relations sayfaları
*   Teşvik ajansları ve kalkınma ofisleri
*   İhale ve tedarik duyuruları

Bu yaklaşım daha temiz veri, daha az hukuki risk ve daha yüksek sinyal kalitesi sağlar.

## 3\. Yapay Zekâ Katmanı – Sınıflandırma ve Bilgi Çıkarımı

Ajan üç temel yapay zekâ fonksiyonunu yerine getirir:

1) Sınıflandırma:

*   relocation, closure, expansion, tender gibi etiketler

2) Bilgi çıkarımı:

*   Şirket adı, lokasyonlar, sektör
*   From → To ilişkisi
*   Hat tipi, zaman çizelgesi, yatırım büyüklüğü

3) Fırsat skorlaması (BIOS-fit):

*   Teknik karmaşıklık
*   Coğrafi uygunluk
*   Zaman penceresi
*   Sektörel öncelik

## 4\. Mimari Yaklaşım – Modüler ve Ölçeklenebilir Yapı

Önerilen mimari şu ana bileşenlerden oluşur:

*   Collector (veri çekme)
*   Normalizer (temizleme, dil tespiti)
*   AI Processor (LLM/NLP)
*   Veritabanı ve arama motoru
*   Skorlama ve workflow motoru
*   Dashboard ve bildirim katmanı

Bu yapı önce MVP olarak kurulup daha sonra yatayda ölçeklenebilir.

## 5\. MVP Yaklaşımı – 4–6 Haftalık Gerçekçi Hedef

MVP'nin amacı hızlıca gerçek fırsat sinyali üretmektir.

Kapsam:

*   50–150 kaynak
*   Günlük tarama
*   Otomatik özetleme ve etiketleme
*   Fırsat skorlaması
*   Haftalık özet rapor

Bu aşamada mükemmellik değil doğruluk ve hız hedeflenir.

## 6\. Hukuk ve Uyumluluk

Sistemin sürdürülebilirliği için uyumluluk kritik önemdedir:

*   Robots.txt ve site kullanım şartlarına uyum
*   Copyright ihlali yaratmayan özetleme yaklaşımı
*   GDPR kapsamında kişi verisi işlenmemesi
*   Loglama ve izlenebilirlik

Bu başlıklar en baştan tasarıma dahil edilmelidir.

## 7\. Stratejik Değer – BIOS İçin Neden Kritik?

Bu ajan BIOS için bir teknoloji projesinden öte bir iş geliştirme silahıdır.

Sağladığı değerler:

*   Erken fırsat yakalama
*   Proaktif satış ve teklif hazırlığı
*   Ülke / sektör bazlı pazar zekâsı
*   Rakiplerden önce pozisyon alma

Uzun vadede bu sistem BIOS’un kurumsal hafızasına dönüşür.
