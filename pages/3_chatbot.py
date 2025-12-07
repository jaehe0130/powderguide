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
# 2) Type Theme & Stats
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

def save_user_card_to_sheet(name, final_type, partner):
    sh = connect_gsheet()
    ws = sh.sheet1
    ws.append_row([name, final_type, partner])


# ============================================
# 4) 추천 동반자 자동 생성 (TYPE 제한)
# ============================================
def get_partner_type(final_type: str) -> str:
    possible_types = list(TYPE_COLOR_THEME.keys())
    possible_types_str = ", ".join(possible_types)

    prompt = f"""
너는 PowderGuide 스키/보드 성향 매칭 전문가야.

아래 목록 중에서 "{final_type}" 와 가장 궁합이 좋은 타입 하나를 선택해.
선택 가능한 타입 목록:
[{possible_types_str}]

규칙:
- 목록 안에서만 선택
- 새로운 이름 생성 금지
- 설명 금지
- 출력은 타입 이름만
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return resp.choices[0].message.content.strip()

# ============================================
# 5) Stability Pixel Card
# ============================================
def generate_pixel_card_image(final_type: str, partner: str) -> bytes:
    key = st.secrets["STABILITY_API_KEY"]

    is_skier = "스키어" in final_type
    type_name = final_type.replace("스키어", "").replace("보더", "").strip()

    gear = (
        "2D pixel ski character, holding carving skis, goggles, winter jacket"
        if is_skier else
        "2D pixel snowboard character, doing small trick, goggles, winter jacket"
    )

    color = TYPE_COLOR_THEME.get(type_name, "retro pastel blue and arcade pink palette")
    stats = TYPE_STATS.get(type_name, {"speed": 70, "skill": 70, "balance": 70})
    spd, skl, bal = stats["speed"], stats["skill"], stats["balance"]

    prompt = f"""
retro 2003-style pixel art RPG character status card,
inspired by old MapleStory UI,
wooden style rounded UI panel frame,
thin black pixel outline,
small pixel font labels,
pastel UI buttons, HP/MP bar decoration,
full body {gear},
{color},
snow resort background,
pixel text '{final_type}' at top center,
pixel text 'PARTNER: {partner}' below,
pixel stats SPEED:{spd}, SKILL:{skl}, BALANCE:{bal},
clean center composition,
4:5 card ratio,
16-bit sprite shading,
low resolution pixel density,
game UI, nostalgic and cozy,
professional pixel art quality
"""

    url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {"Authorization": f"Bearer {key}", "Accept": "image/*"}

    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png"),
        "aspect_ratio": (None, "4:5"),  # 🔥 변경된 라인
    }

    response = requests.post(url, headers=headers, files=files)

    if response.status_code != 200:
        st.error("⚠ Stability API 오류 발생")
        st.code(response.text)
        return None

    return response.content


# ============================================
# 6) OpenAI GPT
# ============================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ============================================
# 7) 상태 변수
# ============================================
st.title("⛷️ 파우디 챗봇 ❄️")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "name" not in st.session_state:
    st.session_state.name = None

if "greeted" not in st.session_state:
    st.session_state.greeted = False

if "final_type" not in st.session_state:
    st.session_state.final_type = None

if "partner" not in st.session_state:
    st.session_state.partner = None


# ============================================
# 8) 이름 입력
# ============================================
if st.session_state.name is None:
    name = st.text_input("닉네임을 알려줘!")
    if name:
        st.session_state.name = name
        st.rerun()

# ============================================
# 9) 첫 인사
# ============================================
if st.session_state.name and not st.session_state.greeted:
    msg = f"안녕 {st.session_state.name}!⛷️❄️ 어떤 스타일인지 알아보고 픽셀카드로 만들어줄게! 스키어야? 보더야?"
    st.chat_message("assistant").write(msg)
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.session_state.greeted = True

# ============================================
# 10) 사용자 입력
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

            # ⚡ 추천 동반자 생성
            partner = get_partner_type(st.session_state.final_type)
            st.session_state.partner = partner

            # ⚡ GoogleSheet 저장
            save_user_card_to_sheet(st.session_state.name, st.session_state.final_type, partner)

            st.rerun()

# ============================================
# 11) 최종 카드 출력
# ============================================
if st.session_state.final_type:
    st.subheader(f"🎴 {st.session_state.final_type} — 너의 도트 RPG 카드!")

    img_bytes = generate_pixel_card_image(
        st.session_state.final_type,
        st.session_state.partner
    )

    if img_bytes:
        st.image(img_bytes, width=380)

    st.markdown(f"🤝 **찰떡궁합 동반자 타입:** `{st.session_state.partner}`")
    st.markdown("🌨 ❄ 세상에 단 하나뿐인 너의 스키/보드 픽셀 카드 완성! ⛷️🏂")
