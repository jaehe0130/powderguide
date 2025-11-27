import streamlit as st

st.set_page_config(layout="wide",  page_title="PowderGuide", page_icon="❄️")

# 버튼 스타일
st.markdown("""
<style>
.custom-btn {
    border: none;
    width: 100%;
    padding: 14px 0;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 600;
    cursor: pointer;
    color: #333;
    margin-bottom: 10px;
}

/* 각 버튼 색상 */
#ski { background-color: #E7F1FF; }      /* 하늘색 */
#rental { background-color: #FFEFD6; }   /* 연한 주황 */
#lodging { background-color: #E9FFE9; }  /* 연한 초록 */
#chatbot { background-color: #F2E7FF; }  /* 연보라 */

.custom-btn:hover {
    opacity: 0.9;
    transform: scale(1.03);
    transition: 0.1s;
}
</style>
""", unsafe_allow_html=True)

# 제목
st.markdown("""
<h1 style='text-align:center; font-size:50px;'>❄️PowderGuide❄️</h1>
<p style='text-align:center; font-size:18px; color:gray; margin-top:-10px;'>
스키장 실시간 검색 · 렌탈 · 숙소 · AI 챗봇
</p>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("## 🔎 빠른 이동")

col1, col2, col3, col4 = st.columns(4)

# 버튼 + 클릭 이벤트
with col1:
    if st.markdown("<button class='custom-btn' id='ski'>🔍 스키장 검색</button>", unsafe_allow_html=True):
        pass
    if st.button(" ", key="ski_btn_invisible"):
        st.switch_page("pages/1_search.py")

with col2:
    if st.markdown("<button class='custom-btn' id='rental'>🎿 렌탈 정보</button>", unsafe_allow_html=True):
        pass
    if st.button(" ", key="rental_btn_invisible"):
        st.switch_page("pages/2_rental.py")

with col3:
    if st.markdown("<button class='custom-btn' id='lodging'>🏨 숙소 정보</button>", unsafe_allow_html=True):
        pass
    if st.button(" ", key="lodging_btn_invisible"):
        st.switch_page("pages/3_lodging.py")

with col4:
    if st.markdown("<button class='custom-btn' id='chatbot'>🤖 AI 챗봇</button>", unsafe_allow_html=True):
        pass
    if st.button(" ", key="chatbot_btn_invisible"):
        st.switch_page("pages/4_chatbot.py")


