import streamlit as st

st.set_page_config(
    page_title="PowderGuide AI",
    layout="wide",
    page_icon="❄️"
)

# ------------------ 제목 영역 ------------------
st.markdown(
    """
    <h1 style='text-align:center; font-size:50px; margin-bottom:10px;'>
        ❄️ PowderGuide AI
    </h1>
    <p style='text-align:center; font-size:18px; color:gray; margin-top:-10px;'>
        스키장 실시간 정보 · 렌탈 · 숙소 · AI 챗봇
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ------------------ 빠른 이동 버튼 ------------------
st.markdown("### 🔍 빠른 이동")

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

st.markdown("---")

# ------------------ 설명 카드 ------------------
st.markdown("### 🧊 PowderGuide 기능 안내")

c1, c2 = st.columns(2)

with c1:
    st.markdown(
        """
        #### ❄️ 실시간 스키장 검색  
        - 스키장 영업 여부  
        - 슬로프 개방 정보  
        - 날씨 & 적설량  
        """
    )

    st.markdown(
        """
        #### 🤖 AI 챗봇  
        - 스키장 추천  
        - 장비 추천  
        - 초보자 강습 설명  
        """
    )

with c2:
    st.markdown(
        """
        #### 🎿 렌탈 정보  
        - 스키/보드 렌탈 가격  
        - 장비별 비교  
        """
    )

    st.markdown(
        """
        #### 🏨 숙소 정보  
        - 스키장 주변 숙소 검색  
        - 가격/거리 필터링  
        """
    )

st.markdown("---")

st.markdown(
    "<p style='text-align:center; color:gray;'>© 2025 PowderGuide — Powered by Streamlit & OpenAI</p>",
    unsafe_allow_html=True
)
