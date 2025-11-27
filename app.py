import streamlit as st

st.set_page_config(
    page_title="PowderGuide AI",
    layout="wide",
    page_icon="❄️"
)

# ----------------- 제목 -----------------
st.markdown("""
<h1 style='text-align:center; font-size:50px;'>
    ❄️ PowderGuide AI
</h1>
<p style='text-align:center; font-size:18px; color:gray; margin-top:-10px;'>
    스키장 실시간 검색 · 렌탈 · 숙소 · AI 챗봇
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ----------------- 빠른 이동 -----------------
st.markdown("## 🔎 빠른 이동")
st.write("")  # 간격

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 스키장 검색", use_container_width=True):
        st.switch_page("pages/1_search.py")

with col2:
    if st.button("🎿 렌탈 정보", use_container_width=True):
        st.switch_page("pages/2_rental.py")

with col3:
    if st.button("🏨 숙소 정보", use_container_width=True):
        st.switch_page("pages/3_lodging.py")

with col4:
    if st.button("🤖 AI 챗봇", use_container_width=True):
        st.switch_page("pages/4_chatbot.py")


