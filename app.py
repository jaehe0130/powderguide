import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="PowderGuide",
    layout="wide",
    page_icon="🎿",
)

# -----------------------------
# CSS 스타일
# -----------------------------
st.markdown("""
    <style>
        .title {
            text-align: center;
            font-size: 3rem;
            font-weight: 700;
            margin-top: 20px;
        }
        .subtitle {
            text-align: center;
            font-size: 1.2rem;
            color: #555;
            margin-top: -10px;
            margin-bottom: 40px;
        }
        .intro-box {
            padding: 30px;
            border-radius: 18px;
            background: rgba(255,255,255,0.85);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }
        .feature-box {
            padding: 20px;
            border-radius: 20px;
            background: rgba(255,255,255,0.7);
            box-shadow: 0 4px 10px rgba(0,0,0,0.08);
            text-align: center;
            backdrop-filter: blur(10px);
        }
    </style>
""", unsafe_allow_html=True)

# =====================
# 헤더
# =====================
st.markdown("<h1 class='title'>🎿 PowderGuide</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>국내 최초, 스키·보드 유저를 위한 통합 데이터 플랫폼</p>",
            unsafe_allow_html=True)

# =====================
# 서비스 대표 이미지
# =====================
try:
    bg = Image.open("assets/ski_bg.jpg")
    st.image(bg, use_container_width=True)
except:
    pass

# =====================
# PowderGuide 소개
# =====================
st.markdown("### ❄ PowderGuide란?")
st.markdown("""
<div class='intro-box'>
    <h3>🏔 당신의 겨울 여정을 더 정확하게, 더 편하게.</h3>
    <p style="font-size:1.05rem; color:#333; line-height:1.6;">
        PowderGuide는 스키·보드를 사랑하는 모든 사람을 위한 <b>실시간 정보 기반 통합 플랫폼</b>입니다.<br><br>
        스키장 운영 시간, 슬로프 개장 현황, 이용 요금부터<br>
        장비 렌탈샵, 주변 숙소, 교통 정보까지<br>
        겨울 스포츠에 필요한 모든 정보를 한 곳에서 확인할 수 있어요.<br><br>
        단순한 정보 제공을 넘어서,<br>
        <b>데이터 기반 추천 시스템</b>으로 당신에게 꼭 맞는 옵션만 선별해드립니다.<br><br>

        초보자부터 상급자까지.<br>
        혼자 가든 친구와 함께 가든.<br>
        PowderGuide는 여러분의 겨울 여행을 더욱 안전하고 완벽하게 만들어주는<br>
        <b>겨울 액티비티 가이드의 새로운 기준</b>입니다.
    </p>
</div>
""", unsafe_allow_html=True)

# =====================
# 기능 소개
# =====================
st.markdown("### 🎿 PowderGuide 핵심 기능")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='feature-box'>
        <h3>🔍 실시간 스키장 검색</h3>
        <p>운영현황, 요금, 슬로프 개장 상황을 빠르게 확인할 수 있어요.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='feature-box'>
        <h3>🎿 장비 렌탈 추천</h3>
        <p>레벨·예산·거리 기반으로 가장 적합한 렌탈샵을 추천해드립니다.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='feature-box'>
        <h3>🏨 숙소 추천 엔진</h3>
        <p>가격, 후기, 접근성을 분석하여 최적의 숙소를 찾아드려요.</p>
    </div>
    """, unsafe_allow_html=True)


# =====================
# CTA 버튼
# =====================
st.markdown("""
<div style="text-align:center; margin-top:40px;">
    <a href="/search" target="_self">
        <button style="
            padding: 15px 40px;
            border-radius: 30px;
            background-color: #2D70F3;
            color: white;
            border: none;
            font-size: 1.1rem;
            cursor: pointer;">
        시작하기 🚀
        </button>
    </a>
</div>
""", unsafe_allow_html=True)

