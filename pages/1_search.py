# -*- coding: utf-8 -*-
import streamlit as st
import requests
import pandas as pd

# ----------------------------------------
# Config
# ----------------------------------------
st.set_page_config(page_title="스키장 검색", page_icon="🎿", layout="wide")

WEATHER_KEY = st.secrets["WEATHER_API_KEY"]  # <-- 수정됨!
GOOGLE_MAPS_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]


# ----------------------------------------
# Ski Resort Basic Data (Image / URL / Lat Lon)
# ----------------------------------------
ski_resorts = [
    {"name": "휘닉스 평창", "lat": 37.5795, "lon": 128.3257,
     "url": "https://phoenixhnr.co.kr", "image": "https://phoenixhnr.co.kr/images/sub/ski.jpg"},

    {"name": "비발디파크", "lat": 37.6512, "lon": 127.6841,
     "url": "https://www.sonohotelsresorts.com/vp", "image": "https://image.goodchoice.kr/resize_1000X500/affiliate/2020/11/03/5fa12c0b2b3fa.jpg"},

    {"name": "엘리시안 강촌", "lat": 37.8162, "lon": 127.6365,
     "url": "https://www.elysian.co.kr", "image": "https://www.elysian.co.kr/common/images/ski/main_ski01.jpg"},

    {"name": "하이원 리조트", "lat": 37.2189, "lon": 128.8404,
     "url": "https://www.high1.com", "image": "https://image.goodchoice.kr/resize_1000X500/affiliate/2020/01/30/5e322a27c63a6.jpg"},

    {"name": "용평 리조트", "lat": 37.6450, "lon": 128.6811,
     "url": "https://www.yongpyong.co.kr", "image": "https://www.yongpyong.co.kr/images/main/slide_01.jpg"},

    {"name": "곤지암 리조트", "lat": 37.3524, "lon": 127.3345,
     "url": "https://www.konjiamresort.co.kr", "image": "https://cdn.visitkorea.or.kr/img/call?cmd=VIEW&id=6c5b2b30-1f0e-4c58-81c7-050f27824f66"},

    {"name": "오크밸리", "lat": 37.4488, "lon": 127.8238,
     "url": "https://www.oakvalley.co.kr", "image": "https://www.oakvalley.co.kr/images/sub/ski/ski_01.jpg"},

    {"name": "웰리힐리파크", "lat": 37.4883, "lon": 128.2422,
     "url": "https://www.wellihillipark.com", "image": "https://cdn.visitkorea.or.kr/img/call?cmd=VIEW&id=d5b97ca2-f778-4dd9-ad07-291e886a193f"},
]


# ----------------------------------------
# Weather Info
# ----------------------------------------
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


# ----------------------------------------
# Google Static Map
# ----------------------------------------
def get_static_map(lat, lon):
    return f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lon}&zoom=13&size=400x300&maptype=roadmap&markers={lat},{lon}&key={GOOGLE_MAPS_KEY}"


# ----------------------------------------
# UI Layout
# ----------------------------------------
st.markdown("""
<h1 style='text-align:center;'>🎿 스키장 검색</h1>
<p style='text-align:center; color:gray;'>
스키장 위치 + 날씨 + 사진 확인하기
</p>
""", unsafe_allow_html=True)

st.markdown("---")
st.subheader("🔍 스키장 이름 또는 지역 검색")
keyword = st.text_input("스키장 이름 또는 지역 입력", "예: 평창 / 강원도 / 용평 / 경기")

filtered_df = df.copy()

if keyword:
    keyword_lower = keyword.lower()
    filtered_df = filtered_df[
        df["name"].str.lower().str.contains(keyword_lower) |
        df["region"].str.lower().str.contains(keyword_lower)
    ]


if keyword:
    df = df[df["name"].str.contains(keyword)]

for resort in df.to_dict(orient="records"):
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        st.image(resort["image"], caption=resort["name"], use_column_width=True)

    with col2:
        st.subheader("🌤 날씨")
        weather = get_weather(resort["lat"], resort["lon"])
        if weather:
            st.write(f"온도: **{weather['temp']}℃**")
            st.write(f"체감: **{weather['feels']}℃**")
            st.write(f"상태: **{weather['desc']}**")
        else:
            st.write("날씨 정보 없음")

        st.markdown(f"🔗 [공식 홈페이지 바로가기]({resort['url']})")

    with col3:
        st.subheader("🗺 지도")
        map_url = get_static_map(resort["lat"], resort["lon"])
        st.image(map_url, use_column_width=True)
