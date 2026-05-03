"""HTML temizleme yardımcısı."""
import re
from typing import Optional

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


def clean_html(text: Optional[str]) -> str:
    """HTML etiketlerini kaldır, temiz metin döndür."""
    if not text:
        return ""
    if BS4_AVAILABLE:
        # Sadece HTML gibi görünüyorsa BeautifulSoup kullan
        if bool(re.search(r'<[^>]+>', text)):
            soup = BeautifulSoup(text, "html.parser")
            clean = soup.get_text(separator=" ")
        else:
            clean = text
    else:
        clean = re.sub(r'<[^>]+>', ' ', text)
    # Çoklu boşlukları temizle
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean
