import streamlit as st

st.set_page_config(
    page_title="PowderGuide AI",
    layout="wide",
    page_icon="❄️"
)

# ---------------- CSS (Shadow + Card) ----------------
st.markdown("""
<style>

body {
    background: linear-gradient(135deg, #eef7ff, #ffffff);
    font-family: 'Arial', sans-serif;
}

/* 카드 기본 스타일 */
.card {
    border-radius: 18px;
    color: white;
    padding: 45px 15px;
    text-align: center;
    box-shadow: 0px 12px 28px rgba(0,0,0,0.30);  /* 더 강한 그림자 */
    transition: transform .25s ease, box-shadow .25s ease;
}
.card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0px 18px 40px rgba(0,0,0,0.45); /* hover 더 깊고 진함 */
}

/* 카드별 색상 */
.card-blue {
    background: linear-gradient(135deg, #4dabf7, #228be6);
}
.card-purple {
    background: linear-gradient(135deg, #b197fc, #845ef7);
}
.card-orange {
    background: linear-gradient(135deg, #ffc078, #fa8e28);
}

/* 제목 및 서브 */
.card-title {
    font-size: 26px;
    font-weight: bold;
    margin-bottom: 5px;
}
.card-sub {
    font-size: 16px;
    margin-top: 5px;
    opacity: 0.9;
}

</style>
""", unsafe_allow_html=True)


# ---------------- Header ----------------
st.markdown("""
<div style="text-align:center; padding-top:5px;">
    <h1 style='font-size:55px;'>❄ PowderGuide AI</h1>
    <p style='font-size:20px; color:gray;'>
        지금, 눈 내리는 겨울 속 스키 여행 ✨
    </p>
</div>
""", unsafe_allow_html=True)

st.write("<hr>", unsafe_allow_html=True)
st.write("")

# ---------------- 3 메뉴 카드 ----------------
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.button("🔍 스키장 검색", use_container_width=True):
        st.switch_page("pages/1_search.py")
    st.markdown("""
        <div class="card card-blue">
            <div class="card-title">🔎 스키장 검색</div>
            <div class="card-sub">실시간 정보 · 리프트 가격 · 코스 안내</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("🤖 파우디 챗봇", use_container_width=True):
        st.switch_page("pages/3_chatbot.py")
    st.markdown("""
        <div class="card card-purple">
            <div class="card-title">😀 파우디 챗봇</div>
            <div class="card-sub">스키/보드 성향 분석 AI 카드</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    if st.button("🧥 파우디 코디네이터", use_container_width=True):
        st.switch_page("pages/4_style.py")
    st.markdown("""
        <div class="card card-orange">
            <div class="card-title">🧣 파우디 스타일러</div>
            <div class="card-sub">AI 스키/보드 코디 추천</div>
        </div>
    """, unsafe_allow_html=True)
