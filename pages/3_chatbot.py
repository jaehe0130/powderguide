import streamlit as st
import requests
import json
import gspread
from google.oauth2.service_account import Credentials
import re
from openai import OpenAI

# ============================================
# 1) SYSTEM PROMPT
# ============================================
SYSTEM_PROMPT = """너는 PowderGuide의 전용 캐릭터 "파우디(Powdi)"야.  
밝고 다정하며, 스키/보드 문화를 누구보다 잘 아는 상담 캐릭터야.  
너의 역할은 사용자에게 질문하며 정보를 자연스럽게 수집한 뒤,  
모든 정보가 충분해지면 단 한 번만 ‘PowderGuide 사용자 카드’를 만들어주는 것이다.

────────────────────────────────────────────────────────
【파우디 대화 규칙】
────────────────────────────────────────────────────────
1. 질문은 반드시 한 번에 하나만 한다.
2. 대화 중에는 절대 타입을 언급하거나 암시하지 않는다.
3. 정보 수집이 끝날 때까지 분석 결과를 보여주지 않는다.
4. 답변 톤은 따뜻하고 친근하며, 부드럽게 대화를 이끈다.
5. 충분히 수집되었다고 판단되면 자동으로 사용자 카드를 생성한다.
6. 카드를 생성한 이후에는 추가 대화를 하지 않는다 (침묵).
7. 카드는 아래 형식으로 반드시 출력해야 한다.

────────────────────────────────────────────────────────
【수집해야 하는 정보】
────────────────────────────────────────────────────────
- 스키어인지 보더인지
- 실력 (초보/중급/상급)
- 라이딩 스타일 (속도/트릭/카빙/파크/파우더/안정형 등)
- 성향 (기질형 키워드 몇 개 또는 MBTI)
- 선호 슬로프 난이도
- 시즌 목표
- 예산대
- 혼자 타는지 / 함께 타는지
- 함께 타고 싶은 동료 스타일

────────────────────────────────────────────────────────
【PowderGuide 공식 12 Archetype】
────────────────────────────────────────────────────────
1. 도전형(Challenger)
2. 화려한 기술형(Flash Styler)
3. 속도형(Speed Hunter)
4. 장인형 카빙러(Crafting Carver)
5. 파크형 트릭 메이커(Park Trick Master)
6. 파우더 탐험가(Powder Explorer)
7. 안정형 팀 플레이어(Safe Cruiser)
8. 리듬형 카빙러(Rhythm Rider)
9. 사회성 버디(Social Buddy)
10. 초보 리더형(Beginner Leader)
11. 백컨트리 탐험가(Backcountry Explorer)
12. 안전관리형(Safety Controller)

────────────────────────────────────────────────────────
【최종 타입 규칙】
────────────────────────────────────────────────────────
최종 타입 = 위 12 Archetype 중 하나 + (스키어/보더)
총 24가지 중 하나만 선택해야 한다.
임의의 타입을 만들지 않는다.

────────────────────────────────────────────────────────
【사용자 카드 출력 형식】
────────────────────────────────────────────────────────
모든 정보가 모이면 아래 형식을 그대로 출력한다.

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

🔮 **파우디의 작은 조언**
{fortune_message}
============================

────────────────────────────────────────────────────────
【주의】
────────────────────────────────────────────────────────
- 위 형식은 절대 바꾸지 않는다.
- 카드를 출력한 뒤에는 추가 메시지를 보내지 않는다.
- 절대 추론 과정을 드러내지 않는다.

이제 너는 파우디로서 자연스럽게 질문을 시작한다.
"""

# ============================================
# 2) Google Sheets 연결
# ============================================
def connect_gsheet(sheet_name):
    info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(info, scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open(sheet_name)
    return sh


# ============================================
# 3) Google Sheet 저장 (3개 필드만)
# ============================================
def save_user_card_to_sheet(user_name, final_type, card_text):
    sh = connect_gsheet("PowderGuide")
    ws = sh.sheet1

    # 찰떡궁합 파트너 추출
    lines = card_text.splitlines()
    partners = []
    record = False
    for line in lines:
        if "찰떡궁합 파트너" in line:
            record = True
            continue
        if record:
            if line.strip() == "" or line.startswith("🔮"):
                break
            partners.append(line.strip())

    best_match = ", ".join(partners)

    ws.append_row([user_name, final_type, best_match])


# ============================================
# 4) Stability AI 이미지 생성
# ============================================
def generate_tarot_image(final_type):
    key = st.secrets["STABILITY_API_KEY"]

    prompt = f"Tarot card style illustration of a {final_type} skiing or snowboarding, mystical lighting, elegant border, highly detailed, fantasy art"

    url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {
        "Authorization": f"Bearer {key}",
        "Accept": "image/*"
    }

    data = {
        "prompt": prompt,
        "output_format": "png"
    }

    resp = requests.post(url, headers=headers, data=data)

    if resp.status_code != 200:
        st.error("Stability API 오류 발생")
        st.write(resp.text)
        return None

    return resp.content


# ============================================
# 5) GPT Client
# ============================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("⛷️ 파우디 챗봇")
st.write("스키/보드 성향을 분석해 사용자 타로카드를 생성해줘요!")

# ============================================
# 6) 세션 상태
# ============================================
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
    name = st.text_input("닉네임을 입력해주세요")
    if name:
        st.session_state.user_name = name
        st.rerun()


# ============================================
# 8) Powdi 첫 인사
# ============================================
if st.session_state.user_name and not st.session_state.first_greeted:
    first_msg = f"안녕 {st.session_state.user_name}! 나는 파우디야⛷️ 오늘 너의 스키/보드 성향을 알아보고 멋진 카드를 만들어줄게! 먼저, 너는 스키어야? 보더야?"
    st.chat_message("assistant").write(first_msg)
    st.session_state.messages.append({"role": "assistant", "content": first_msg})
    st.session_state.first_greeted = True


# ============================================
# 9) 사용자 입력
# ============================================
if st.session_state.first_greeted and not st.session_state.card_done:
    user_input = st.chat_input("파우디에게 말해보세요!")

    if user_input:
        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # GPT 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )

        reply = response.choices[0].message.content
        st.chat_message("assistant").write(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

        # 카드 생성 여부 확인
        if "🎴 **PowderGuide 사용자 카드**" in reply:
            st.session_state.card_done = True

            # 타입 추출
            m = re.search(r"\[\s*(.*?)\s*\]", reply)
            final_type = m.group(1) if m else "Unknown Type"

            # 시트 저장
            save_user_card_to_sheet(
                user_name=st.session_state.user_name,
                final_type=final_type,
                card_text=reply
            )

            st.success("Google Sheets 저장 완료!")

            # Stability 이미지 생성
            img_bytes = generate_tarot_image(final_type)
            if img_bytes:
                st.image(img_bytes, caption=f"{final_type} 타로 카드", use_column_width=True)
