import streamlit as st

st.set_page_config(
    page_title="PowderGuide AI",
    layout="wide",
    page_icon="❄️"
)

# ---------------- CSS 스타일 ----------------
st.markdown("""
<style>

body {
    background: linear-gradient(135deg, #e3f2fd, #ffffff);
    font-family: 'Arial', sans-serif;
}

/* 론칭 타이틀 */
.title-container {
    text-align: center;
    padding-top: 10px;
}

/* 카드 버튼 공통 스타일 */
.card {
    background-color: white;
    border-radius: 18px;
    padding: 40px 20px;
    text-align: center;
    box-shadow: 0px 5px 15px rgba(0,0,0,0.1);
    transition: 0.3s;
    border: 1px solid #f1f1f1;
}

.card:hover {
    transform: translateY(-8px);
    box-shadow: 0px 12px 20px rgba(0,0,0,0.18);
    cursor: pointer;
}

/* 버튼 텍스트 */
.card h3 {
    font-size: 24px;
    margin-top: 10px;
}

.sub {
    color: gray;
    margin-top: -12px;
    font-size: 15px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# ----------------- 제목 -----------------
st.markdown("""
<div class="title-container">
    <h1 style='font-size:55px;'>❄ PowderGuide AI</h1>
    <p style='font-size:20px; color:gray;'>
        당신의 스키 / 보드 경험을 AI가 더 즐겁게 만들어드립니다!
    </p>
</div>
""", unsafe_allow_html=True)

st.write("")
st.markdown("<hr>", unsafe_allow_html=True)
st.write("")

# ----------------- 카드 3개 배치 -----------------
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔍 스키장 검색", key="search"):
        st.switch_page("pages/1_search.py")
    st.markdown("""
        <div class='card'>
            <h3>🔍 스키장 검색</h3>
            <p class='sub'>실시간 정보 · 리프트 가격 · 코스 안내</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("🤖 파우디 챗봇", key="chatbot"):
        st.switch_page("pages/3_chatbot.py")
    st.markdown("""
        <div class='card'>
            <h3>🤖 파우디 챗봇</h3>
            <p class='sub'>스키/보드 성향 분석 AI 카드</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    if st.button("🧥 파우디 스타일러", key="style"):
        st.switch_page("pages/4_style.py")
    st.markdown("""
        <div class='card'>
            <h3>🧥 파우디 스타일러</h3>
            <p class='sub'>AI 스키/보드 코디 추천</p>
        </div>
    """, unsafe_allow_html=True)
