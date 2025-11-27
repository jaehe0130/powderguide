import streamlit as st

st.set_page_config(
    page_title="PowderGuide AI",
    layout="wide",
    page_icon="❄️"
)

st.markdown(
    """
    <h1 style='text-align:center; font-size:50px;'>❄️ PowderGuide AI</h1>
    <p style='text-align:center; font-size:18px; color:gray;'>
        스키장 실시간 정보 · 사진 분석 · 슬로프 추천 챗봇
    </p>
    """,
    unsafe_allow_html=True
)

st.image("assets/banner.png", use_container_width=True)

st.markdown("### 🔍 빠른 이동")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("❄️ 스키장 정보"):
        st.switch_page("pages/1_search.py")

with col2:
    if st.button("🏔️ 장비 랜탈"):
        st.switch_page("pages/2_rental.py")

with col3:
    if st.button("📸 숙소 정보"):
        st.switch_page("pages/3_lodging.py")

with col4:
    if st.button("📚 챗봇 서비스"):
        st.switch_page("pages/4_chatbot.py")

