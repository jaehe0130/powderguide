import streamlit as st
import json
import pandas as pd
from PIL import Image

# 페이지 기본 설정
st.set_page_config(
    page_title="스키장 검색 - PowderGuide",
    layout="wide",
    page_icon="🏔"
)

# -----------------------
# 데이터 로드 함수
# -----------------------
@st.cache_data
def load_resort_data():
    try:
        with open("data/resorts.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

resorts = load_resort_data()

# -----------------------
# 헤더
# -----------------------
st.markdown("""
    <h1 style='text-align:center; font-weight:700; margin-bottom:10px;'>
        🏔 스키장 검색
    </h1>
    <p style='text-align:center; color:gray; margin-top:-10px;'>
        스키장 운영정보 · 이용요금 · 위치를 한 번에 확인해보세요.
    </p>
""", unsafe_allow_html=True)
st.write("")

# -----------------------
# 검색 필터 바
# -----------------------
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    search_keyword = st.text_input("🔍 스키장 검색", placeholder="예: 용평, 비발디, 웰리힐리")

with col2:
    regions = sorted(list(set([r["region"] for r in resorts])))
    selected_region = st.selectbox("📍 지역 선택", ["전체"] + regions)

with col3:
    sort_option = st.selectbox("정렬", ["이름순", "가까운순(준비중)", "요금 낮은순(준비중)"])

st.write("---")

# -----------------------
# 검색 필터 적용
# -----------------------
def filter_resorts():
    result = resorts
    if search_keyword:
        result = [r for r in result if search_keyword in r["name"] or search_keyword in r["name_eng"].lower()]
    if selected_region != "전체":
        result = [r for r in result if r["region"] == selected_region]
    return result

filtered = filter_resorts()

# -----------------------
# 결과 출력
# -----------------------
if not filtered:
    st.warning("검색된 스키장이 없습니다. 다시 검색해주세요.")
else:
    for r in filtered:
        with st.container():
            st.markdown(
                f"""
                <div style="
                    padding: 20px;
                    border-radius: 15px;
                    background: #ffffff;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                    margin-bottom: 25px;">
                    
                    <h3 style="margin-bottom:5px;">🎿 {r['name']}</h3>
                    <p style="color: gray; margin-top:-5px;">📍 {r['region']}</p>

                    <hr style="margin:10px 0;">
                    
                    <b>⏳ 운영현황:</b> {r.get('status', '정보없음')} <br>
                    <b>💰 이용요금:</b><br>
# 홈버튼
def go_home():
    st.switch_page("app.py")
st.button("🏠 초기 화면으로 돌아가기", on_click=go_home)

st.markdown("## 🔍 실시간 스키장 검색")
