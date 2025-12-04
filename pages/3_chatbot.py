import streamlit as st
from openai import OpenAI
import json
import gspread
import requests
import re
from datetime import datetime
from io import BytesIO
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image

# ----------------------------------------------------
# 1) API KEY 불러오기
# ----------------------------------------------------
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# ----------------------------------------------------
# 2) Google Sheet 연결
# ----------------------------------------------------
def connect_gsheet(sheet_name: str):
    service_info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_info, scope)
    gc = gspread.authorize(creds)
    sh = gc.open(sheet_name)
    return sh


def save_user_card_to_sheet(user_name, final_type, card_text, conversation):
    sh = connect_gsheet("PowderGuide")
    ws = sh.worksheet("user_cards")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history = "\n".join(
        f"{m['role']}: {m['content']}"
        for m in conversation 
        if m["role"] in ("user", "assistant")
    )


    ws.append_row([timestamp, user_name, final_type, card_text, history])


# ----------------------------------------------------
# 3) 24타입 타로 이미지 프롬프트 빌더
# ----------------------------------------------------
ARCHETYPE_META = {
    "도전형": ("Challenger", "bold, fiery red-orange energy, aggressive riding"),
    "화려한 기술형": ("Flash Styler", "neon spotlight, stylish trick pose"),
    "속도형": ("Speed Hunter", "streamlined form, blue-silver fast motion"),
    "장인형 카빙러": ("Crafting Carver", "precise carving lines, green-brown tones"),
    "파크형 트릭 메이커": ("Park Trick Master", "dynamic jumps, neon blue & lime"),
    "파우더 탐험가": ("Powder Explorer", "floating powder snow, sky blue palette"),
    "안정형 팀 플레이어": ("Safe Cruiser", "calm warm beige tones, relaxed posture"),
    "리듬형 카빙러": ("Rhythm Rider", "smooth rhythm flow, dark blue & green"),
    "사회성 버디": ("Social Buddy", "friendly pose, coral & yellow accents"),
    "초보 리더형": ("Beginner Leader", "mint-green tone, growing confidence"),
    "백컨트리 탐험가": ("Backcountry Explorer", "mountain terrain, emerald-brown"),
    "안전관리형": ("Safety Controller", "navy-gray protection, confident stance"),
}


def build_tarot_prompt(final_type: str) -> str:
    # 장르
    genre = "skier" if "스키어" in final_type else "snowboarder"

    # 성향 한글 → 영어 매핑
    for key in ARCHETYPE_META:
        if key in final_type:
            eng, style = ARCHETYPE_META[key]
            break
    else:
        eng, style = "Snow Rider", "balanced neutral theme"

    return (
        f"tarot card illustration of a {genre}, {eng} archetype, "
        f"{style}, ornate golden tarot frame, glowing edges, snowy mountain, "
        f"full-body, fantasy art, cinematic lighting, high detail"
    )


# ----------------------------------------------------
# 4) Stability API로 타로 이미지 생성
# ----------------------------------------------------
def generate_tarot_image(final_type: str) -> Image.Image:
    prompt = build_tarot_prompt(final_type)

    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/*"
    }

    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png")
    }

    res = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/core",
        headers=headers,
        files=files,
    )

    if res.status_code != 200:
        st.error(res.text)
        raise RuntimeError("Stability API Error")

    return Image.open(BytesIO(res.content))


# ----------------------------------------------------
# 5) Powdi 시스템 프롬프트
# ----------------------------------------------------
SYSTEM_PROMPT = """
너는 PowderGuide의 전용 상담 캐릭터 파우디(Powdi)야.
밝고 다정하며 스키·보드를 잘 알고 자연스럽게 질문한다.

[규칙]
1. 질문은 한 번에 하나씩.
2. 중간에 절대로 타입을 언급하지 않는다.
3. 모든 정보가 모이면 단 한 번만 “PowderGuide 사용자 카드”를 아래 템플릿으로 출력한다.
4. 카드 출력 후 아무 말도 하지 않는다.

[카드 템플릿]
============================
🎴 **PowderGuide 사용자 카드**
**[{최종 타입}]**

🌈 **상징 아이콘**
{emoji}

🎨 **컬러 테마**
{color_theme}

✨ **키워드 3가지**
- {keyword1}
- {keyword2}
- {keyword3}

🧭 **타입 설명**
{type_description}

🤝 **찰떡궁합 파트너**
{best_match_1}  
{best_match_2}

🔮 **파우디의 작은 조언**
{fortune_message}
============================
"""

# ----------------------------------------------------
# 6) Streamlit UI
# ----------------------------------------------------
st.title("⛷️🏂 Powdi 사용자 카드 생성 챗봇")
user_name = st.text_input("사용자 이름 (선택)", placeholder="홍길동")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "card_done" not in st.session_state:
    st.session_state.card_done = False


# 대화 출력
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]):
            st.markdown(m["content"])


# ----------------------------------------------------
# 7) 사용자 입력 → Powdi 답변
# ----------------------------------------------------
if not st.session_state.card_done and st.session_state.first_greeted:

    user_input = st.chat_input("파우디에게 답해주세요!")

    if user_input:
        # 사용자 메시지 저장
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # GPT 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
        )
        reply = response.choices[0].message.content

        # Powdi 응답 저장
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

        # ----------------------------------------------------
        # 8) 사용자 카드 생성 감지
        # ----------------------------------------------------
        if "PowderGuide 사용자 카드" in reply:
            st.session_state.card_done = True

            # 최종 타입 추출
            m = re.search(r"\[\s*(.*?)\s*\]", reply)
            final_type = m.group(1) if m else "타입 미확인"

            st.success(f"최종 타입: {final_type}")

            # Google Sheet 저장
            save_user_card_to_sheet(
                user_name=st.session_state.user_name or "익명",
                final_type=final_type,
                card_text=reply,
                conversation=st.session_state.messages,
            )
            st.info("Google Sheet 저장 완료!")

            # Stability AI로 이미지 생성
            st.markdown("### 🎨 Powdi가 타로 카드를 그리고 있어요...")
            img = generate_tarot_image(final_type)
            st.image(img, caption=f"{final_type} 타로 카드", use_column_width=True)
