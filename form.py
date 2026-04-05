import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="Canlı Sipariş Formu", layout="centered", page_icon="⌚")
st.title("⌚ Saat Sipariş Formu")

# --- 1. AYARLAR (BURASI ÇOK ÖNEMLİ) ---
# Google Apps Script'ten aldığın linki buraya yapıştır. 
# Not: Linkin içinde iki tane "https" olmamalı, tek bir temiz link olmalı.
URL = "https://script.google.com/macros/s/AKfycbz8NoVUJOLHtDpAwSHHQxOO8caOcto1-9zeiCwaCGB73EeNzKuljvrHueif8aJ5LQL-/exec"

# --- 2. GOOGLE'DAN STOKLARI ÇEKME FONKSİYONU ---
@st.cache_data(ttl=60)
def stoklari_getir():
    try:
        # Google'ın yönlendirmelerini aşmak için allow_redirects=True şart
        res = requests.get(URL, timeout=15, allow_redirects=True)
        res.raise_for_status() 
        veri = res.json()
        return pd.DataFrame(veri)
    except Exception as e:
        # Hata olursa boş tablo döner, uygulama çökmez
        return pd.DataFrame(columns=["Model", "Stok"])

# --- 3. ANA UYGULAMA MANTIĞI ---
try:
    df = stoklari_getir()
    
    if df.empty:
        st.error("⚠️ Stok listesi yüklenemedi. Lütfen Google Script linkini ve 'Stoklar' sayfa adını kontrol edin.")
        st.info("İpucu: Kopyaladığınız linkin sonu '/exec' ile bitmelidir.")
    else:
        # Kullanıcı Bilgileri
        col_bilgi1, col_bilgi2 = st.columns(2)
        with col_bilgi1:
            musteri = st.text_input("👤 Adınız Soyadınız")
        with col_bilgi2:
            firma = st.text_input("🏢 Firma Adı")
        
        st.subheader("📦 Mevcut Modeller ve Stoklar")
        siparisler = {}
        
        # Stok Listesini Göster
        for i, row in df.iterrows():
            model = row['Model']
            stok = int(row['Stok'])
            
            # Sadece stoğu 0'dan büyük olanları göster
            if stok > 0:
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{model}**")
                # Kullanıcının stoktan fazla seçmesini engeller
                adet = c2.number_input(f"Kalan: {stok}", min_value=0, max_value=stok, key=f"in_{i}", step=1)
                if adet > 0:
                    siparisler[model] = adet
                    
        st.divider()
        
        # Sipariş Onay Butonu
        if st.button("🚀 Siparişi Onayla", use_container_width=True):
            if musteri and firma and siparisler:
                # Veriyi paketle
                veri_paketi = []
                for m, a in siparisler.items():
                    veri_paketi.append({
                        "Tarih": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Müşteri": musteri,
                        "Firma": firma,
                        "Model": m,
                        "Adet": a
                    })
                
                with st.spinner('Sipariş iletiliyor...'):
                    # Google'a Gönder (POST)
                    res = requests.post(URL, json=veri_paketi)
                    
                    if res.status_code == 200:
                        st.success("✅ Harika! Sipariş alındı ve stoklar güncellendi.")
                        st.balloons()
                        # Önbelleği temizle ki yeni stoklar hemen gelsin
                        st.cache_data.clear()
                        # Sayfayı yenile
                        st.rerun()
                    else:
                        st.error(f"❌ Bir hata oluştu (Hata Kodu: {res.status_code})")
            else:
                st.warning("⚠️ Lütfen isminizi, firmanızı girin ve en az 1 ürün seçin.")

except Exception as e:
    st.error(f"💥 Beklenmedik bir hata oluştu: {e}")

