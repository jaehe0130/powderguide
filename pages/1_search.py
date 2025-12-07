# -*- coding: utf-8 -*-
import streamlit as st
import requests
import pandas as pd

# CONFIG
st.set_page_config(page_title="스키장 검색", page_icon="🎿", layout="wide")

WEATHER_KEY = st.secrets["WEATHER_API_KEY"]
GOOGLE_MAPS_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]

# Local image mapping (파일명과 매칭)
IMAGE_MAP = {
    "휘닉스 평창": "photos/phoenix.webp",
    "비발디파크": "photos/vivaldi.jpg",
    "엘리시안 강촌": "photos/elysian.jpg",
    "하이원 리조트": "photos/high1.png",
    "용평 리조트": "photos/yongpyong.jpg",
    "곤지암 리조트": "photos/gonjiam.jpg",
    "오크밸리": "photos/oakvalley.jpg",
    "웰리힐리파크": "photos/welihily.jpg"
}


# --- Ski Resort Basic Data ---
ski_resorts = [
    {"name": "휘닉스 평창", "region": "강원도", "lat": 37.5795, "lon": 128.3257, "url": "https://phoenixhnr.co.kr"},
    {"name": "비발디파크", "region": "강원도", "lat": 37.6512, "lon": 127.6841, "url": "https://www.sonohotelsresorts.com/vp"},
    {"name": "엘리시안 강촌", "region": "강원도", "lat": 37.8162, "lon": 127.6365, "url": "https://www.elysian.co.kr"},
    {"name": "하이원 리조트", "region": "강원도", "lat": 37.2189, "lon": 128.8404, "url": "https://www.high1.com"},
    {"name": "용평 리조트", "region": "강원도", "lat": 37.6450, "lon": 128.6811, "url": "https://www.yongpyong.co.kr"},
    {"name": "곤지암 리조트", "region": "경기도", "lat": 37.3524, "lon": 127.3345, "url": "https://www.konjiamresort.co.kr"},
    {"name": "오크밸리", "region": "강원도", "lat": 37.4488, "lon": 127.8238, "url": "https://www.oakvalley.co.kr"},
    {"name": "웰리힐리파크", "region": "강원도", "lat": 37.4883, "lon": 128.2422, "url": "https://www.wellihillipark.com"}
]

df = pd.DataFrame(ski_resorts)

# --- Get Weather ---
def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_KEY}&units=metric&lang=kr"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    data = res.json()
    return {
        "temp": data["main"]["temp"],
        "feels": data["main"]["feels_like"],
        "desc": data["weather"][0]["description"]
    }

# --- Google Static Map ---
def get_static_map(lat, lon):
    return f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=13&size=400x300&maptype=roadmap&markers={lat},{lon}&key={GOOGLE_MAPS_KEY}"

# --- UI ---
st.markdown("""
<h1 style='text-align:center;'>🎿 스키장 검색</h1>
<p style='text-align:center; color:gray;'>
스키장 위치 + 날씨 + 사진 확인하기
</p>
""", unsafe_allow_html=True)

st.markdown("---")
keyword = st.text_input("🔍 스키장 이름 또는 지역 검색", "")

filtered = df.copy()

if keyword:
    k = keyword.lower()
    filtered = filtered[
        df["name"].str.lower().str.contains(k) |
        df["region"].str.lower().str.contains(k)
    ]

st.subheader(f"📍 검색 결과: {len(filtered)}곳")

# --- Result Loop ---
for _, resort in filtered.iterrows():
    st.markdown("---")
    col1, col2, col3 = st.columns([2,2,2])

    # IMAGE
    with col1:
        img_path = IMAGE_MAP.get(resort["name"], None)  # fallback
        if img_path:
            st.image(img_path, caption=resort["name"], use_column_width=True)
        else:
            st.write("❌ 이미지 없음")

    # WEATHER
    with col2:
        st.subheader("🌤 날씨")
        weather = get_weather(resort["lat"], resort["lon"])
        if weather:
            st.write(f"온도: **{weather['temp']}℃**")
            st.write(f"체감온도: **{weather['feels']}℃**")
            st.write(f"상태: **{weather['desc']}**")
        else:
            st.write("날씨 정보 없음")

        st.markdown(f"🔗 [공식 홈페이지]({resort['url']})")

    # MAP
    with col3:
        st.subheader("🗺 지도")
        map_url = get_static_map(resort["lat"], resort["lon"])
        st.image(map_url, use_column_width=True)
