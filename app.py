import streamlit as st

st.set_page_config(
    page_title="PowderGuide AI",
    layout="wide",
    page_icon="❄️"
)

# ------------------ 스타일 ------------------
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #e5e5e5;
    background-color: #fafafa;
    transition: 0.2s;
    cursor: pointer;
}
.card:hover {
    background-color: #f1f8ff;
    border-color: #4da3ff;
    transform: scale(1.02);
}
.card-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 8px;
}
.card-desc {
    font-size: 15px;
    color: #555;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

# ------------------ 제목 ------------------
st.markdown(
    """
    <h1 style='text-align:center; font-size:50px;'>❄️ PowderGuide AI</h1>
    <p style='text-align:center; font-size:18px; color:gray; margin-top:-10px;'>
        스키장 실시간 검색 · 렌탈 · 숙소 · AI 챗봇
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ------------------ 카드 버튼 4개 ------------------
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# ----- 카드 함수 -----
def card(label, title, desc, page):
    with st.container():
        clicked = st.button(
            f"{label}",
            key=page,
            use_container_width=True
        )
        st.markdown(
            f"""
            <div class='card'>
                <div class='card-title'>{title}</div>
                <div class='card-desc'>{desc}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if clicked:
            st.switch_page(page)

# ----- 각 카드 구성 -----
with col1:
    card("🔍 스키장 검색", 
         "실시간 스키장 검색",
         "• 스키장 영업 여부\n• 슬로프 개방 정보\n• 날씨 & 적설량",
         "pages/1_search.py")

with col2:
    card("🎿 렌탈 정보", 
         "스키/보드 렌탈 정보",
         "• 스키/보드 렌탈 가격\n• 장비별 비교",
         "pages/2_rental.py")

with col3:
    card("🏨 숙소 정보", 
         "스키장 주변 숙소 검색",
         "• 주변 숙소 탐색\n• 가격/거리 필터링",
         "pages/3_lodging.py")

with col4:
    card("🤖 AI 챗봇", 
         "PowderGuide AI 챗봇",
         "• 스키장 추천\n• 장비 추천\n• 초보자 강습 설명",
         "pages/4_chatbot.py")

st.markdown("---")

st.markdown(
    "<p style='text-align:center; color:gray;'>© 2025 PowderGuide — Powered by Streamlit & OpenAI</p>",
    unsafe_allow_html=True
)
