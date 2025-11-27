import streamlit as st

st.set_page_config(
    page_title="PowderGuide AI",
    layout="wide",
    page_icon="❄️"
)

# ============ CSS 버튼 색상 스타일 ============
st.markdown("""
<style>

.custom-btn {
    width: 100%;
    padding: 12px 0;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 500;
    border: 1px solid #e0e0e0;
    cursor: pointer;
    text-align: center;
}

/* 버튼 hover 효과 동일 */
.custom-btn:hover {
    opacity: 0.85;
    transform: scale(1.02);
    transition: 0.15s;
}

/* 개별 버튼 색상 */
#ski_btn {
    background-color: #E8F3FF;   /* 연한 하늘색 */
}
#rental_btn {
    background-color: #FFF3E0;   /* 연한 주황 */
}
#lodging_btn {
    background-color: #E8FFE8;   /* 연한 초록 */
}
#chatbot_btn {
    background-color: #F3E8FF;   /* 연한 보라 */
}

</style>
""", unsafe_allow_html=True)

# ============ 제목 ============
st.markdown("## 🔎 빠른 이동")

col1, col2, col3, col4 = st.columns(4)

# ============ 버튼 4개 ============
with col1:
    if st.button("🔍 스키장 검색", key="ski", use_container_width=True):
        st.switch_page("pages/1_search.py")
    st.markdown("<div id='ski_btn' class='custom-btn'> </div>", unsafe_allow_html=True)

with col2:
    if st.button("🎿 렌탈 정보", key="rental", use_container_width=True):
        st.switch_page("pages/2_rental.py")
    st.markdown("<div id='rental_btn' class='custom-btn'> </div>", unsafe_allow_html=True)

with col3:
    if st.button("🏨 숙소 정보", key="lodging", use_container_width=True):
        st.switch_page("pages/3_lodging.py")
    st.markdown("<div id='lodging_btn' class='custom-btn'> </div>", unsafe_allow_html=True)

with col4:
    if st.button("🤖 AI 챗봇", key="chatbot", use_container_width=True):
        st.switch_page("pages/4_chatbot.py")
    st.markdown("<div id='chatbot_btn' class='custom-btn'> </div>", unsafe_allow_html=True)


