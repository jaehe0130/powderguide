import streamlit as st
import requests
import json
import gspread
import re
from google.oauth2.service_account import Credentials
from openai import OpenAI

# ============================================
# 1) SYSTEM PROMPT — 성별/스키/보드/스타일 수집 포함
# ============================================
SYSTEM_PROMPT = """
너는 PowderGuide의 전용 캐릭터 파우디(Powdi)야.

사용자에게 질문하여 정보를 하나씩 수집해야 한다.

반드시 아래 항목을 순서에 상관없이 물어봐야 한다:
- 성별 (남자 / 여자 / 기타)
- 스키어인지 보더인지
- 라이딩 스타일, 태도, 성격 기반 질문

모든 정보가 수집되면 아래 형식으로 최종 타입만 출력한다.

[최종 타입]

예: [파크형 트릭 메이커 보더]

⚠ 규칙:
- 질문은 항상 하나씩.
- 아직 묻지 않은 정보를 기반으로 질문한다.
- 타입을 암시하지 않는다.
- 설명, 키워드 나열, 조언 금지.
- 최종 타입 출력 후 아무 말도 하지 않는다.
"""


# ============================================
# 2) TYPE COLOR + STATS
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
# 3) TYPE COMPANION MATCHING
# ============================================
TYPE_COMPATIBILITY = {
    "파크형 트릭 메이커": "장인형 카빙러",
    "속도형": "안정형 팀 플레이어",
    "파우더 탐험가": "안전관리형",
    "도전형": "사회성 버디",
    "사회성 버디": "도전형",
    "초보 리더형": "장인형 카빙러",
    "리듬형 카빙러": "화려한 기술형",
    "안정형 팀 플레이어": "속도형",
    "화려한 기술형": "리듬형 카빙러",
    "백컨트리 탐험가": "안전관리형",
    "안전관리형": "파우더 탐험가",
}

# ============================================
# 4) Google Sheet 저장
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
# 5) Stability 이미지 생성
# ============================================
def generate_pixel_card_image(final_type: str, partner: str, gender: str, ski_type: str) -> bytes:
    key = st.secrets["STABILITY_API_KEY"]

    gender_prompt = "female" if "여" in gender.lower() else "male"

    if "스키" in ski_type:
        equipment = "full body pixel art ski character, holding skis"
    else:
        equipment = "full body pixel art snowboarder, holding snowboard doing small trick"

    type_name = final_type.replace("스키어", "").replace("보더", "").strip()
    color = TYPE_COLOR_THEME.get(type_name, "retro blue and pink palette")
    stats = TYPE_STATS.get(type_name, {"speed": 70, "skill": 70, "balance": 70})
    spd, skl, bal = stats["speed"], stats["skill"], stats["balance"]

    prompt = f"""
retro pixel art RPG character card,
MapleStory style UI,
{gender_prompt}, {equipment},
{color},
snow mountain background,
pixel text '{final_type}' top,
pixel text 'Partner: {partner}',
pixel stats SPEED:{spd} SKILL:{skl} BALANCE:{bal},
HP/MP bar UI, nostalgic cozy game interface,
16-bit shading, professional sprite art,
clean centered pose,
"""

    url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {"Authorization": f"Bearer {key}", "Accept": "image/*"}
    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png"),
        "aspect_ratio": (None, "4:5")
    }

    response = requests.post(url, headers=headers, files=files)

    if response.status_code != 200:
        st.error("⚠ Stability API 오류 발생")
        st.code(response.text)
        return None

    return response.content


# ============================================
# 6) GPT CLIENT
# ============================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# ============================================
# 7) STREAMLIT 상태 변수
# ============================================
st.title("⛷️ 파우디 챗봇 ❄")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

for key in ["name", "gender", "ski_type", "final_type", "partner_type"]:
    if key not in st.session_state:
        st.session_state[key] = None


# ============================================
# 8) 닉네임 입력
# ============================================
if st.session_state.name is None:
    name = st.text_input("닉네임을 알려줘!")
    if name:
        st.session_state.name = name
        st.rerun()


# ============================================
# 9) 대화 로직
# ============================================
if st.session_state.final_type is None:

    user_input = st.chat_input("파우디에게 말해줘!")
    if user_input:

        # 대화 저장
        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 성별 감지
        if st.session_state.gender is None:
            if re.search(r"여|girl|female", user_input, re.IGNORECASE):
                st.session_state.gender = "여자"
            elif re.search(r"남|boy|male", user_input, re.IGNORECASE):
                st.session_state.gender = "남자"

        # 스키/보드 감지
        if st.session_state.ski_type is None:
            if "보드" in user_input:
                st.session_state.ski_type = "보더"
            elif "스키" in user_input:
                st.session_state.ski_type = "스키어"

        # GPT 응답
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        reply = resp.choices[0].message.content
        st.chat_message("assistant").write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # 최종 타입 감지
        m = re.search(r"\[(.*?)\]", reply)
        if m:
            st.session_state.final_type = m.group(1)

            # 매칭 파트너 타입 저장
            base_type = st.session_state.final_type.split()[0]  
            st.session_state.partner_type = TYPE_COMPATIBILITY.get(base_type, "모두와 잘 맞음")

            # 구글시트 저장
            save_user_card_to_sheet(
                st.session_state.name,
                st.session_state.final_type,
                st.session_state.partner_type,
                st.session_state.gender,
                st.session_state.ski_type
            )

            st.rerun()


# ============================================
# 10) 최종 카드 생성 + 출력
# ============================================
if st.session_state.final_type:

    st.subheader(f"📍 {st.session_state.final_type} — 너의 도트 RPG 카드!")

    img = generate_pixel_card_image(
        st.session_state.final_type,
        st.session_state.partner_type,
        st.session_state.gender,
        st.session_state.ski_type
    )

    if img:
        st.image(img, width=400)

    st.markdown(f"🤝 **찰떡궁합 동반자 타입:** `{st.session_state.partner_type}`")
    st.markdown("☃ 세상에 단 하나뿐인 너의 스키/보드 픽셀 카드 완성! 🎿🏂")
