import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# --- GİZLİLİK VE GÖRÜNÜM AYARLARI ---
st.set_page_config(page_title="Saat Sipariş Sistemi", layout="centered", page_icon="⌚")

# Teknik menüleri gizleyen CSS
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            [data-testid="stToolbar"] {visibility: hidden !important;}
            [data-testid="stDecoration"] {display:none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("⌚ Saat Sipariş Formu")

# --- 1. AYARLAR ---
URL = "https://script.google.com/macros/s/AKfycbz8NoVUJOLHtDpAwSHHQxOO8caOcto1-9zeiCwaCGB73EeNzKuljvrHueif8aJ5LQL-/exec"

# --- 2. GOOGLE'DAN STOKLARI ÇEKME ---
@st.cache_data(ttl=60, show_spinner=False)
def stoklari_getir():
    try:
        res = requests.get(URL, timeout=10)
        res.raise_for_status() 
        veri = res.json()
        return pd.DataFrame(veri)
    except Exception:
        return pd.DataFrame(columns=["Model", "Stok"])

# --- 3. ANA UYGULAMA ---
try:
    df = stoklari_getir()

    if df is None or df.empty:
        st.warning("🔄 Stoklar güncelleniyor, lütfen sayfayı yenileyin.")
    else:
        # Kullanıcı Bilgileri
        col_bilgi1, col_bilgi2 = st.columns(2)
        with col_bilgi1:
            musteri = st.text_input("👤 Adınız Soyadınız")
        with col_bilgi2:
            firma = st.text_input("🏢 Firma Adı")
        
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
                c1, c2 = st.columns([3, 1])
                c1.write(f"**{model}**")
                adet = c2.number_input(f"Adet (Stok: {stok})", min_value=0, max_value=stok, key=f"in_{i}", step=1)
                if adet > 0:
                    siparisler[model] = adet
                    
        st.divider()
        
        # Sipariş Onay Butonu
        if st.button("🚀 Siparişi Onayla", use_container_width=True):
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
                with st.spinner('Siparişiniz işleniyor...'):
                    try:
                        res = requests.post(URL, json=veri_paketi, timeout=15)
                        if res.status_code == 200:
                            basarili_mi = True
                    except:
                        basarili_mi = False

                if basarili_mi:
                    st.success(f"✅ Sayın {musteri}, siparişiniz başarıyla iletildi.")
                    st.cache_data.clear()
                    time.sleep(5)
                    st.rerun()
                else:
                    st.error("❌ Bir bağlantı sorunu oluştu. Lütfen tekrar deneyiniz.")
            else:
                st.warning("⚠️ Lütfen formu eksiksiz doldurunuz.")

except Exception as e:
    st.error("💥 Bir hata oluştu, lütfen sayfayı yenileyiniz.")
