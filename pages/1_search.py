# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# ----------------------------------------
# 페이지 기본 설정
# ----------------------------------------
st.set_page_config(page_title="스키장 검색", page_icon="🎿", layout="wide")

st.markdown("""
<h1 style='text-align:center;'>🎿 스키장 검색</h1>
<p style='text-align:center; color:gray;'>
원하는 조건으로 스키장을 찾아보세요!
</p>
""", unsafe_allow_html=True)


# ----------------------------------------
# 스키장 샘플 데이터
# 나중에 JSON / Google Sheet로 분리 가능
# ----------------------------------------

ski_resorts = [
    {
        "name": "휘닉스 평창",
        "region": "강원도",
        "beginner": 40,
        "intermediate": 40,
        "advanced": 20,
        "night": True,
        "price": 89000,
        "open_rate": 75,
        "image": "https://phoenixhnr.co.kr/images/sub/ski.jpg"
    },
    {
        "name": "비발디파크",
        "region": "강원도",
        "beginner": 50,
        "intermediate": 35,
        "advanced": 15,
        "night": True,
        "price": 95000,
        "open_rate": 80,
        "image": "https://image.goodchoice.kr/resize_1000X500/affiliate/2020/11/03/5fa12c0b2b3fa.jpg"
    },
    {
        "name": "엘리시안 강촌",
        "region": "강원도",
        "beginner": 60,
        "intermediate": 30,
        "advanced": 10,
        "night": True,
        "price": 79000,
        "open_rate": 70,
        "image": "https://www.elysian.co.kr/common/images/ski/main_ski01.jpg"
    },
    {
        "name": "하이원 리조트",
        "region": "강원도",
        "beginner": 30,
        "intermediate": 40,
        "advanced": 30,
        "night": False,
        "price": 110000,
        "open_rate": 85,
        "image": "https://image.goodchoice.kr/resize_1000X500/affiliate/2020/01/30/5e322a27c63a6.jpg"
    },
    {
        "name": "용평 리조트",
        "region": "강원도",
        "beginner": 25,
        "intermediate": 45,
        "advanced": 30,
        "night": True,
        "price": 105000,
        "open_rate": 85,
        "image": "https://www.yongpyong.co.kr/images/main/slide_01.jpg"
    },
    {
        "name": "곤지암 리조트",
        "region": "경기도",
        "beginner": 50,
        "intermediate": 35,
        "advanced": 15,
        "night": True,
        "price": 98000,
        "open_rate": 65,
        "image": "https://cdn.visitkorea.or.kr/img/call?cmd=VIEW&id=6c5b2b30-1f0e-4c58-81c7-050f27824f66"
    },
    {
        "name": "오크밸리",
        "region": "강원도",
        "beginner": 55,
        "intermediate": 30,
        "advanced": 15,
        "night": False,
        "price": 68000,
        "open_rate": 60,
        "image": "https://www.oakvalley.co.kr/images/sub/ski/ski_01.jpg"
    },
    {
        "name": "웰리힐리파크",
        "region": "강원도",
        "beginner": 40,
        "intermediate": 45,
        "advanced": 15,
        "night": True,
        "price": 88000,
        "open_rate": 78,
        "image": "https://cdn.visitkorea.or.kr/img/call?cmd=VIEW&id=d5b97ca2-f778-4dd9-ad07-291e886a193f"
    }
]


df = pd.DataFrame(ski_resorts)

# ----------------------------------------
# 검색 & 필터
# ----------------------------------------

st.subheader("🔍 검색 및 필터")

col1, col2, col3, col4 = st.columns([2,1,1,1])

with col1:
    keyword = st.text_input("스키장 이름 검색", "")

with col2:
    region_filter = st.selectbox("지역 선택", ["전체", "강원도", "경기도"])

with col3:
    night_filter = st.selectbox("야간 가능 여부", ["전체", "야간 가능", "야간 불가"])

with col4:
    price_filter = st.slider("가격대(최대)", 50000, 120000, 120000)


# ----------------------------------------
# 필터링 적용 로직
# ----------------------------------------
filtered = df.copy()

# 이름 검색
if keyword:
    filtered = filtered[filtered["name"].str.contains(keyword)]

# 지역 필터
if region_filter != "전체":
    filtered = filtered[filtered["region"] == region_filter]

# 야간 스키
if night_filter == "야간 가능":
    filtered = filtered[filtered["night"] == True]
elif night_filter == "야간 불가":
    filtered = filtered[filtered["night"] == False]

# 가격
filtered = filtered[filtered["price"] <= price_filter]


# ----------------------------------------
# 결과 출력
# ----------------------------------------
st.markdown("---")
st.subheader(f"🎿 검색 결과: {len(filtered)}곳")

if len(filtered) == 0:
    st.info("조건에 맞는 스키장이 없습니다!")
else:
    for i, row in filtered.iterrows():
        with st.container():
            cols = st.columns([1, 2])

            # 이미지
            with cols[0]:
                st.image(row["image"], use_column_width=True)

            # 정보
            with cols[1]:
                st.markdown(f"### **{row['name']}**  ({row['region']})")
                st.markdown(f"""
                - 🟢 초급: **{row['beginner']}%**
                - 🟡 중급: **{row['intermediate']}%**
                - 🔴 상급: **{row['advanced']}%**
                - 🌙 야간 스키: {"가능" if row['night'] else "불가"}
                - 💰 가격: **{row['price']:,}원**
                - 🗻 슬로프 오픈률: **{row['open_rate']}%**
                """)

                # 버튼
                detail_btn = st.button(f"자세히 보기", key=f"detail_{i}")
                if detail_btn:
                    st.session_state["selected_resort"] = row["name"]
                    st.switch_page("pages/2_resort_detail.py")

        st.markdown("---")

