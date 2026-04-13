import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# --- 1. GİZLİLİK VE GÖRÜNÜM AYARLARI ---
st.set_page_config(
    page_title="Saat Sipariş Sistemi", 
    layout="centered", 
    page_icon="⌚",
    initial_sidebar_state="collapsed"
)

# Sadece dış bağlantıları ve teknik ikonları temizler, formuna dokunmaz
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden !important;}
            header {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            .stAppDeployButton {display:none !important;}
            [data-testid="stStatusWidget"] {display:none !important;}
            [data-testid="stToolbar"] {display:none !important;}
            [data-testid="stDecoration"] {display:none !important;}
            #viewerBadge {display:none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. AYARLAR ---
URL = "https://script.google.com/macros/s/AKfycbztzzGxNuQbBWZBeg_FeM-KdrjvNekw0VFZ0SQAMIobHaV2Bts9Eky3isyXpRO6un96/exec"

# --- 3. GOOGLE'DAN STOKLARI ÇEKME ---
@st.cache_data(ttl=60, show_spinner=False)
def stoklari_getir():
    try:
        res = requests.get(URL, timeout=10)
        res.raise_for_status() 
        veri = res.json()
        return pd.DataFrame(veri)
    except Exception:
        return pd.DataFrame(columns=["Model", "Stok"])

# --- 4. ANA UYGULAMA ARAYÜZÜ ---
st.title("⌚ Saat Sipariş Formu")
st.write("Lütfen sipariş vermek istediğiniz adetleri giriniz.")

try:
    df = stoklari_getir()

    if df is None or df.empty:
        st.warning("🔄 Stoklar güncelleniyor, lütfen sayfayı yenileyin.")
    else:
        # Kullanıcı Bilgileri
        col_bilgi1, col_bilgi2 = st.columns(2)
        with col_bilgi1:
            musteri = st.text_input("👤 Adınız Soyadınız", placeholder="Örn: Ahmet Yılmaz")
        with col_bilgi2:
            firma = st.text_input("🏢 Firma Adı", placeholder="Örn: X Saatçilik")
        
        st.subheader("📦 Mevcut Modeller")
        siparisler = {}
        
        # Stok Listesini Göster
        for i, row in df.iterrows():
            model = row['Model']
            stok_degeri = row['Stok']
            
            try:
                stok = int(stok_degeri)
            except:
                stok = 0
            
            if stok > 0:
                with st.container():
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"**{model}**")
                    adet = c2.number_input(f"Stok: {stok}", min_value=0, max_value=stok, key=f"in_{i}", step=1)
                    if adet > 0:
                        siparisler[model] = adet
                st.write("---") 
                    
        # Sipariş Onay Butonu
        if st.button("🚀 Siparişi Onayla ve Gönder", use_container_width=True):
            if musteri and firma and siparisler:
                veri_paketi = []
                for m, a in siparisler.items():
                    veri_paketi.append({
                        "Tarih": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Müşteri": musteri,
                        "Firma": firma,
                        "Model": m,
                        "Adet": a
                    })
                
                basarili_mi = False
                with st.spinner('Siparişiniz sisteme iletiliyor...'):
                    try:
                        res = requests.post(URL, json=veri_paketi, timeout=15)
                        if res.status_code == 200:
                            basarili_mi = True
                    except:
                        basarili_mi = False

                if basarili_mi:
                    st.success(f"✅ Sayın {musteri}, siparişiniz başarıyla iletildi.")
                    st.cache_data.clear()
                    time.sleep(3)
                    st.rerun()
                else:
                    st.error("❌ Bir bağlantı sorunu oluştu. Lütfen tekrar deneyiniz.")
            else:
                st.warning("⚠️ Lütfen adınızı, firmanızı ve en az bir ürün adedini giriniz.")

except Exception:
    # Hata durumunda teknik detay sızmaması için mesajı sadeleştirdim
    st.error("💥 Beklenmedik bir hata oluştu, lütfen sayfayı yenileyiniz.")