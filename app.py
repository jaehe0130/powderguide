import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="PowderGuide",
    page_icon="🎿",
    layout="wide"
)

# ---------------------------
# 헤더
# ---------------------------
st.markdown("<h1 style='text-align:center; font-weight:700;'>🎿 PowderGuide</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666;'>스키·보드 정보를 한 곳에서</p>", unsafe_allow_html=True)

# 대표 이미지
try:
    bg = Image.open("assets/ski_bg.jpg")
    st.image(bg, use_container_width=True)
except:
    pass

# 소개
st.write("### ❄ PowderGuide란?")
st.write("""
국내 스키·보드 유저들을 위한 실시간 정보 통합 플랫폼입니다.  
스키장 운영정보, 이용요금, 렌탈샵 추천, 숙소 추천, 챗봇까지 한 번에 제공합니다.
""")

st.write("---")

# ---------------------------
# 버튼 메뉴
# ---------------------------
st.write("### ⛷️ 메뉴 선택")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    if st.button("🔍 실시간 스키장 검색", use_container_width=True):
        st.switch_page("powderguide/pages/1_search.py")

with col2:
    if st.button("🎿 렌탈 추천", use_container_width=True):
        st.switch_page("pages/2_rental.py")

with col3:
    if st.button("🏨 숙소 추천", use_container_width=True):
        st.switch_page("pages/3_lodging.py")

with col4:
    if st.button("🤖 챗봇 서비스", use_container_width=True):
        st.switch_page("pages/4_chatbot.py")
