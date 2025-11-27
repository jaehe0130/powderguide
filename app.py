import streamlit as st

st.set_page_config(
    page_title="PowderGuide AI",
    layout="wide",
    page_icon="❄️"
)

# ----------------- CSS: 버튼 배경색 지정 -----------------
st.markdown("""
<style>

button[kind="secondary"] {
    border-radius: 12px !important;
    padding: 14px 0px !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    width: 100% !important;
    border: none !important;
    color: #333 !important;
}

/* 스키장 검색 버튼 */
#ski_btn button {
    background-color: #E7F1FF !important;   /* 하늘색 */
}

/* 렌탈 정보 버튼 */
#rental_btn button {
    background-color: #FFEFD6 !important;   /* 연한 주황 */
}

/* 숙소 정보 버튼 */
#lodging_btn button {
    background-color: #E9FFE9 !important;   /* 연한 초록 */
}

/* 챗봇 버튼 */
#chatbot_btn button {
    background-color: #F2E7FF !important;   /* 연한 보라 */
}

button:hover {
    opacity: 0.9 !important;
    transform: scale(1.02);
    transition: 0.1s ease-in-out;
}

</style>
""", unsafe_allow_html=True)


# ----------------- 제목 -----------------
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

# ----------------- 빠른 이동 -----------------
st.markdown("## 🔎 빠른 이동")

col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container():
        st.markdown('<div id="ski_btn">', unsafe_allow_html=True)
        if st.button("🔍 스키장 검색", key="ski", use_container_width=True):
            st.switch_page("pages/1_search.py")
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown('<div id="rental_btn">', unsafe_allow_html=True)
        if st.button("🎿 렌탈 정보", key="rental", use_container_width=True):
            st.switch_page("pages/2_rental.py")
        st.markdown('</div>', unsafe_allow_html=True)

with col3:
    with st.container():
        st.markdown('<div id="lodging_btn">', unsafe_allow_html=True)
        if st.button("🏨 숙소 정보", key="lodging", use_container_width=True):
            st.switch_page("pages/3_lodging.py")
        st.markdown('</div>', unsafe_allow_html=True)

with col4:
    with st.container():
        st.markdown('<div id="chatbot_btn">', unsafe_allow_html=True)
        if st.button("🤖 AI 챗봇", key="chatbot", use_container_width=True):
            st.switch_page("pages/4_chatbot.py")
        st.markdown('</div>', unsafe_allow_html=True)

