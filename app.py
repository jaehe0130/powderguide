import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="PowderGuide",
    layout="wide",
    page_icon="🎿",
)

# ==============================
# PAGE SWITCH FUNCTIONS
# ==============================
def go_search():
    st.switch_page("views/search.py")

def go_rental():
    st.switch_page("views/rental.py")

def go_lodging():
    st.switch_page("views/lodging.py")

def go_chatbot():
    st.switch_page("views/chatbot.py")

# ==============================
# HEADER
# ==============================
st.markdown("<h1 style='text-align:center; font-weight:700;'>🎿 PowderGuide</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666;'>스키·보드 정보를 한 곳에서</p>", unsafe_allow_html=True)

# 이미지
try:
    bg = Image.open("assets/ski_bg.jpg")
    st.image(bg, use_container_width=True)
except:
    pass

# ==============================
# 서비스 소개
# ==============================
st.markdown("""
### ❄ PowderGuide란?
국내 스키·보드 유저들을 위한 실시간 정보 통합 플랫폼입니다.
스키장 운영정보, 렌탈샵, 숙소 추천, 챗봇 상담까지 한 번에 제공합니다.
""")

st.write("---")

# ==============================
# 메인 메뉴 버튼 4개
# ==============================
st.markdown("### ⛷️ 메뉴 선택")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    if st.button("🔍 실시간 스키장 검색", use_container_width=True):
        go_search()

with col2:
    if st.button("🎿 렌탈 추천", use_container_width=True):
        go_rental()

with col3:
    if st.button("🏨 숙소 추천", use_container_width=True):
        go_lodging()

with col4:
    if st.button("🤖 챗봇 서비스", use_container_width=True):
        go_chatbot()
