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
    if st.button("❄️ 챗봇"):
        st.switch_page("pages/1_search.py")

with col2:
    if st.button("🏔️ 눈 상태"):
        st.switch_page("pages/2_🏔️_Snow_Status.py")

with col3:
    if st.button("📸 사진 분석"):
        st.switch_page("pages/3_📸_Photo_Analyze.py")

with col4:
    if st.button("📚 스키장 정보"):
        st.switch_page("pages/4_📚_Resort_Info.py")

