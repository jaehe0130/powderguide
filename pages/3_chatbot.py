import streamlit as st
import requests
import json
import gspread
import re
from google.oauth2.service_account import Credentials
from openai import OpenAI

TYPE_COLOR_THEME = {
    "도전형": "fiery red and orange, bold energetic palette",
    "화려한 기술형": "neon cyan and pink, flashy trickster palette",
    "속도형": "high-contrast blue and silver, fast aura palette",
    "장인형 카빙러": "deep navy and ice blue precision palette",
    "파크형 트릭 메이커": "neon pink, teal, lime freestyle palette",
    "파우더 탐험가": "soft pastel blue and white powder palette",
    "안정형 팀 플레이어": "warm beige and yellow friendly palette",
    "리듬형 카빙러": "smooth turquoise and wave-like gradient palette",
    "사회성 버디": "bright orange and cheerful green palette",
    "초보 리더형": "soft green beginner palette",
    "백컨트리 탐험가": "earth brown and forest green palette",
    "안전관리형": "clean steel gray and orange safety palette",
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
    "사회성 베디": {"speed": 65, "skill": 70, "balance": 80},
    "초보 리더형": {"speed": 55, "skill": 60, "balance": 70},
    "백컨트리 탐험가": {"speed": 75, "skill": 80, "balance": 85},
    "안전관리형": {"speed": 50, "skill": 70, "balance": 95},
}


# ============================================
# 1) SYSTEM PROMPT
# ============================================
SYSTEM_PROMPT = """
너는 PowderGuide의 전용 캐릭터 "파우디(Powdi)"야.  
따뜻하고 다정하며, 스키/보드 문화를 누구보다 잘 이해하는 상담 캐릭터야.

너의 역할은 사용자에게 질문을 자연스럽게 던지며 정보를 모으고,  
모든 정보가 충분히 모였다고 판단되면 단 한 번 ‘PowderGuide 사용자 카드’를 생성하는 것이다.

────────────────────────────────────────────────────────
【파우디 대화 규칙】
────────────────────────────────────────────────────────
1. 질문은 반드시 한 번에 하나만 한다.
2. 대화 중에는 절대 타입을 직접 말하지 않는다.
3. 충분한 정보가 모일 때까지 카드를 생성하지 않는다.
4. 최종 카드 생성 시 아래 형식을 반드시 사용해야 한다.

============================
🔮 **파우디의 작은 조언**
{fortune_message}
============================

────────────────────────────────────────────────────────
【주의】
────────────────────────────────────────────────────────
- 카드를 출력하기 전에는 절대 결과를 암시하지 않는다.
- 카드 출력은 단 한 번만 한다.
- 추론 과정은 절대로 노출하지 않는다.
"""


# ============================================
# 2) Google Sheets 연결 (Drive API 사용 X)
# ============================================
SHEET_ID = "1MZQaCE8ez2dSYEMo35N2JLreQWjV5bjfof1KvsTZafE"

def connect_gsheet():
    info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    creds = Credentials.from_service_account_info(info, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)
    return sh


# ============================================
# 3) Google Sheets 저장 (3항목)
# ============================================
def save_user_card_to_sheet(user_name, final_type, card_text):
    sh = connect_gsheet()
    ws = sh.sheet1

    partners = []
    record = False
    for line in card_text.splitlines():
        if "찰떡궁합 파트너" in line:
            record = True
            continue
        if record:
            if line.strip() == "" or line.startswith("🔮"):
                break
            partners.append(line.strip())

    best_match = partners[0] if partners else ""
    ws.append_row([user_name, final_type, best_match])


# ============================================
# 4) StabilityAI — 픽셀 게임캐릭터 카드 이미지 생성
# ============================================
def generate_tarot_image(final_type):
    key = st.secrets["STABILITY_API_KEY"]

    # 장르 분리
    is_skier = "스키어" in final_type
    is_boarder = "보더" in final_type
    type_name = final_type.replace("스키어", "").replace("보더", "").strip()

    # 장비 묘사
    if is_skier:
        gear_prompt = (
            "pixel art character wearing ski outfit, holding ski poles, carving skis on slope, "
            "ski goggles, dynamic skiing posture"
        )
    else:
        gear_prompt = (
            "pixel art character riding a snowboard, baggy snowboard outfit, wide stance, "
            "reflective snowboard goggles, mid-air freestyle trick"
        )

    # 타입 연출
    base_style = TYPE_COLOR_THEME.get(type_name, "balanced arcade palette")

    # 능력치
    stats = TYPE_STATS.get(type_name, {"speed": 70, "skill": 70, "balance": 70})
    speed = stats["speed"]
    skill = stats["skill"]
    balance = stats["balance"]

    # 최종 프롬프트
    prompt = (
        f"retro 16-bit pixel art game character card, {gear_prompt}, "
        f"{base_style}, cute chibi proportions, neon snow slope background, "
        f"arcade collectible card layout, glowing effects, dramatic action lines, "
        f"pixel text '{final_type}' at top, "
        f"pixel UI stats at bottom: SPEED {speed}, SKILL {skill}, BALANCE {balance}, "
        f"high-detail pixel shading, colorful retro arcade lighting"
    )

    url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {
        "Authorization": f"Bearer {key}",
        "Accept": "image/*"
    }

    files = {"none": (None, "")}
    data = {"prompt": prompt, "aspect_ratio": "3:4", "output_format": "png"}

    response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code != 200:
        st.error("Stability API 오류 발생!")
        st.write(response.text)
        return None

    return response.content



# ============================================
# 5) GPT Client
# ============================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# ============================================
# 6) Streamlit UI
# ============================================
st.title("⛷️ 파우디 챗봇 — 픽셀 게임카드 버전")
st.write("너의 라이딩 성향을 분석해 게임 캐릭터 카드로 만들어줄게!")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "first_greeted" not in st.session_state:
    st.session_state.first_greeted = False

if "card_done" not in st.session_state:
    st.session_state.card_done = False


# ============================================
# 7) 사용자 이름 입력
# ============================================
if st.session_state.user_name is None:
    name = st.text_input("닉네임을 알려줘!")
    if name:
        st.session_state.user_name = name
        st.rerun()


# ============================================
# 8) 파우디 첫 인사
# ============================================
if st.session_state.user_name and not st.session_state.first_greeted:
    first_msg = (
        f"안녕 {st.session_state.user_name}! 나는 파우디야 ⛷️❄️\n"
        "너의 스키/보드 성향을 알아보고 멋진 픽셀카드를 만들어줄게!\n"
        "먼저, 너는 스키어야? 보더야?"
    )
    st.chat_message("assistant").write(first_msg)
    st.session_state.messages.append({"role": "assistant", "content": first_msg})
    st.session_state.first_greeted = True


# ============================================
# 9) 파우디 대화 진행
# ============================================
if st.session_state.first_greeted and not st.session_state.card_done:
    user_input = st.chat_input("파우디에게 말해보세요!")

    if user_input:
        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # GPT 응답 생성
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )

        reply = response.choices[0].message.content
        st.chat_message("assistant").write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # 타입 감지 규칙 변경
            if re.search(r"\[.*?\]", reply):

            st.session_state.card_done = True

            m = re.search(r"\[\s*(.*?)\s*\]", reply)
            final_type = m.group(1) if m else "Unknown"

            save_user_card_to_sheet(
                user_name=st.session_state.user_name,
                final_type=final_type,
                card_text=reply
            )

            st.success("Google Sheets 저장 완료!")

            # 픽셀 게임캐릭터 이미지 생성
            img_data = generate_tarot_image(final_type)
            if img_data:
                st.image(img_data, caption=f"{final_type} 픽셀 게임카드", width=450)
