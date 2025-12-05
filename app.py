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
    스키장 실시간 검색 · AI 챗봇 · AI 스타일
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

with col3:
    if st.button("🤖 파우디 챗봇", use_container_width=True):
        st.switch_page("pages/3_chatbot.py")

with col4:
    if st.button("🤖 파우디 스타일러", use_container_width=True):
        st.switch_page("pages/4_style.py")


