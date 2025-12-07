import streamlit as st
import requests
import json
import gspread
import re
from google.oauth2.service_account import Credentials
from openai import OpenAI
from PIL import Image
from io import BytesIO

# ============================================
# 1) SYSTEM PROMPT
# ============================================
SYSTEM_PROMPT = """
너는 PowderGuide의 전용 캐릭터 파우디(Powdi)야.
사용자의 정보를 하나씩 자연스럽게 질문하면서 수집해야 한다.

필수로 물어야 하는 항목:
- 성별 (남자 / 여자 / 기타)
- 스키어인지 보더인지
- 스타일/성격/라이딩 정보

모든 정보가 수집되면 아래 형식으로 최종 타입만 출력한다.
[최종 타입]

예: [파크형 트릭 메이커 보더]

⚠ 규칙:
- 질문은 항상 하나씩.
- 아직 수집되지 않은 정보를 기반으로 질문한다.
- 타입을 암시하지 않는다.
- 설명, 조언, 키워드 나열 금지.
- 최종 타입 출력 후 아무 말도 하지 않는다.
"""

# ============================================
# 2) TYPE Theme & Stats
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
# 3) Google Sheets 저장
# ============================================
SHEET_ID = "1MZQaCE8ez2dSYEMo35N2JLreQWjV5bjfof1KvsTZafE"

def connect_gsheet():
    info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    gc = gspread.authorize(creds)
    return gc.open_by_key(SHEET_ID)

def save_user_card_to_sheet(name, final_type, partner, gender, ski_type):
    sh = connect_gsheet()
    ws = sh.sheet1
    ws.append_row([name, final_type, partner, gender, ski_type])


# ============================================
# 4) HuggingFace Image Generation
# ============================================
def generate_pixel_card_image(final_type: str, partner: str, gender: str, ski_type: str):
    HF_TOKEN = st.secrets["HUGGINGFACE_TOKEN"]

    gender_prompt = "female" if "여" in gender.lower() else "male"
    equipment = "pixel ski character holding skis" if "스키" in ski_type else "pixel snowboard character holding snowboard"

    type_name = final_type.replace("스키어", "").replace("보더", "").strip()
    color = TYPE_COLOR_THEME.get(type_name, "retro arcade palette")
    stats = TYPE_STATS.get(type_name, {"speed": 70, "skill": 70, "balance": 70})
    spd, skl, bal = stats["speed"], stats["skill"], stats["balance"]

    prompt = f"""
retro japanese pixel RPG card UI,
{gender_prompt}, {equipment},
{color},
snow mountain town background,
pixel text header '{final_type}',
pixel footer showing 'Speed {spd} | Skill {skl} | Balance {bal}',
pixel note 'Partner: {partner}',
16-bit pixel shading,
nostalgic maple story style,
game UI window frame,
high quality pixel sprite
"""

    response = requests.post(
        "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-dev",
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        json={"inputs": prompt, "parameters": {"num_inference_steps": 25}}
    )

    if response.status_code != 200:
        st.error("⚠ HuggingFace API 오류")
        st.code(response.text)
        return None

    return Image.open(BytesIO(response.content))


# ============================================
# 5) GPT
# ============================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("⛷️❄ 파우디의 챗봇")

# ============================================
# Session
# ============================================
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

for key in ["name", "gender", "ski_type", "final_type", "partner"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ============================================
# 이름 입력
# ============================================
if st.session_state.name is None:
    name = st.text_input("닉네임을 알려줘! ⛷️")
    if name:
        st.session_state.name = name
        st.rerun()

# ============================================
# 대화 진행
# ============================================
if st.session_state.final_type is None:

    user_input = st.chat_input("파우디에게 말해줘!")
    if user_input:

        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # gender 감지
        if st.session_state.gender is None:
            if re.search(r"여|걸|female", user_input, re.IGNORECASE):
                st.session_state.gender = "여자"
            elif re.search(r"남|보이|male", user_input, re.IGNORECASE):
                st.session_state.gender = "남자"

        # 스키/보드 감지
        if st.session_state.ski_type is None:
            if "보드" in user_input:
                st.session_state.ski_type = "보더"
            elif "스키" in user_input:
                st.session_state.ski_type = "스키어"

        # GPT reply
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        reply = resp.choices[0].message.content
        st.chat_message("assistant").write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # detect final type
        m = re.search(r"\[(.*?)\]", reply)
        if m:
            st.session_state.final_type = m.group(1)
            st.session_state.partner = "매칭중"

            save_user_card_to_sheet(
                st.session_state.name,
                st.session_state.final_type,
                st.session_state.partner,
                st.session_state.gender,
                st.session_state.ski_type
            )

            st.rerun()

# ============================================
# 카드 출력
# ============================================
if st.session_state.final_type:

    st.subheader(f"🎴 {st.session_state.final_type} — Pixel RPG Card")

    img = generate_pixel_card_image(
        st.session_state.final_type,
        st.session_state.partner,
        st.session_state.gender,
        st.session_state.ski_type
    )

    if img:
        st.image(img, width=380)

    st.markdown("🌨 ❄ **PowderGuide Pixel Character Complete!**")
