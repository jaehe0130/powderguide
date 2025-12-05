import streamlit as st
import requests
import json
import gspread
import re
from google.oauth2.service_account import Credentials
from openai import OpenAI

# ============================================
# 1) SYSTEM PROMPT
# ============================================
SYSTEM_PROMPT = """
너는 PowderGuide의 전용 캐릭터 파우디(Powdi)야.
사용자에게 질문하여 정보를 수집하고,
모든 정보가 모이면 아래 형식으로 최종 타입만 출력해야 한다.

[최종 타입]

예: [파크형 트릭 메이커 보더]

규칙:
- 질문은 항상 하나씩.
- 타입을 암시하지 않는다.
- 설명, 키워드, 조언 등은 절대 출력하지 않는다.
- 최종 타입 출력 후 아무 말도 하지 않는다.
"""

# ============================================
# 2) 타입 테마 & 능력치 (전역 변수)
# ============================================
TYPE_COLOR_THEME = {
    "도전형": "fiery red and orange palette",
    "화려한 기술형": "neon cyan and pink trickster palette",
    "속도형": "blue and silver speed palette",
    "장인형 카빙러": "deep navy precision palette",
    "파크형 트릭 메이커": "neon pink and lime freestyle palette",
    "파우더 탐험가": "soft pastel blue powder palette",
    "안정형 팀 플레이어": "warm beige friendly palette",
    "리듬형 카빙러": "turquoise rhythm palette",
    "사회성 버디": "bright orange social palette",
    "초보 리더형": "soft green beginner palette",
    "백컨트리 탐험가": "earth brown mountain palette",
    "안전관리형": "steel gray safety palette",
}

TYPE_STATS = {
    "도전형": {"speed": 90, "skill": 80, "balance": 70},
    "화려한 기술형": {"speed": 75, "skill": 95, "balance": 65},
    "속도형": {"speed": 95, "skill": 75, "balance": 70},
    "장인형 카빙러": {"speed": 85, "skill": 90, "balance": 80},
    "파크형 트릭 메이커": {"speed": 80, "skill": 95, "balance": 60},
    "파우더 탐험가": {"speed": 70, "skill": 85, "balance": 90},
    "안정형 팀 플레이어": {"speed": 60, "skill": 70, "balance": 95},
    "리듬형 카빙러": {"speed": 80, "skill": 85, "balance": 85},
    "사회성 버디": {"speed": 65, "skill": 70, "balance": 80},
    "초보 리더형": {"speed": 55, "skill": 60, "balance": 70},
    "백컨트리 탐험가": {"speed": 75, "skill": 80, "balance": 85},
    "안전관리형": {"speed": 50, "skill": 70, "balance": 95},
}

# ============================================
# 3) Google Sheet 저장
# ============================================
SHEET_ID = "1MZQaCE8ez2dSYEMo35N2JLreQWjV5bjfof1KvsTZafE"

def connect_gsheet():
    info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    gc = gspread.authorize(creds)
    return gc.open_by_key(SHEET_ID)

def save_user_card_to_sheet(name, final_type):
    sh = connect_gsheet()
    ws = sh.sheet1
    ws.append_row([name, final_type])

# ============================================
# 4) Stability 이미지 생성
# ============================================
def generate_tarot_image(final_type):
    key = st.secrets["STABILITY_API_KEY"]

    is_skier = "스키어" in final_type
    type_name = final_type.replace("스키어", "").replace("보더", "").strip()

    gear = (
        "pixel ski character, carving skis, goggles"
        if is_skier else
        "pixel snowboard character, freestyle trick, goggles"
    )

    color = TYPE_COLOR_THEME.get(type_name, "arcade palette")
    stats = TYPE_STATS.get(type_name, {"speed": 70, "skill": 70, "balance": 70})
    spd, skl, bal = stats["speed"], stats["skill"], stats["balance"]

    prompt = (
        f"retro 16-bit pixel art character card, {gear}, "
        f"{color}, neon winter slope background, chibi proportions, "
        f"pixel text '{final_type}', "
        f"pixel stats SPEED {spd}, SKILL {skl}, BALANCE {bal}, "
        f"arcade collectible UI, dynamic action lines, high-detail shading"
    )

    url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {"Authorization": f"Bearer {key}", "Accept": "image/*"}
    files = {"none": (None, "")}
    data = {"prompt": prompt, "aspect_ratio": "3:4", "output_format": "png"}

    resp = requests.post(url, headers=headers, files=files, data=data)
    if resp.status_code != 200:
        st.error("Stability 오류:")
        st.write(resp.text)
        return None

    return resp.content

# ============================================
# 5) OpenAI GPT
# ============================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ============================================
# 6) Streamlit 상태 변수
# ============================================
st.title("⛷️ 파우디 챗봇 — 픽셀 캐릭터 카드 생성기")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "name" not in st.session_state:
    st.session_state.name = None

if "greeted" not in st.session_state:
    st.session_state.greeted = False

if "final_type" not in st.session_state:
    st.session_state.final_type = None

# ============================================
# 7) 이름 입력
# ============================================
if st.session_state.name is None:
    name = st.text_input("닉네임을 알려줘!")
    if name:
        st.session_state.name = name
        st.rerun()

# ============================================
# 8) 첫 인사
# ============================================
if st.session_state.name and not st.session_state.greeted:
    msg = f"안녕 {st.session_state.name}!⛷️❄️ 어떤 스타일인지 알아보고 픽셀카드로 만들어줄게! 스키어야? 보더야?"
    st.chat_message("assistant").write(msg)
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.session_state.greeted = True

# ============================================
# 9) 사용자 입력 처리
# ============================================
if st.session_state.greeted and st.session_state.final_type is None:

    user_input = st.chat_input("파우디에게 말해줘!")
    if user_input:
        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        reply = resp.choices[0].message.content
        st.chat_message("assistant").write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        m = re.search(r"\[(.*?)\]", reply)
        if m:
            st.session_state.final_type = m.group(1)
            save_user_card_to_sheet(st.session_state.name, st.session_state.final_type)
            st.rerun()

# ============================================
# 10) 최종 이미지 출력
# ============================================
if st.session_state.final_type:
    st.subheader(f"🎴 {st.session_state.final_type} — 너의 픽셀 캐릭터 카드!")

    img = generate_tarot_image(st.session_state.final_type)
    if img:
        st.image(img, width=400)

    st.markdown("🔮 **파우디의 코멘트:** 오늘도 너만의 스타일로 신나게 달려보자! ❄️")
