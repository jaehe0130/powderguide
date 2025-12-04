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
너는 PowderGuide의 전용 캐릭터 "파우디(Powdi)"야.  
밝고 다정하며, 스키/보드 문화를 누구보다 잘 아는 상담 캐릭터야.  
너의 역할은 사용자에게 질문하며 정보를 자연스럽게 수집한 뒤,  
모든 정보가 충분해지면 단 한 번만 ‘PowderGuide 사용자 카드’를 만들어주는 것이다.

────────────────────────────────────────────────────────
【파우디 대화 규칙】
────────────────────────────────────────────────────────
1. 질문은 반드시 한 번에 하나만 한다.
2. 대화 중에는 절대 타입을 언급하거나 암시하지 않는다.
3. 정보 수집이 끝날 때까지 분석 결과를 보여주지 않는다.
4. 답변 톤은 따뜻하고 친근하며 자연스럽다.
5. 충분히 정보를 수집했다고 판단하면 자동으로 사용자 카드를 생성한다.
6. 카드를 생성한 이후에는 추가 대화를 하지 않는다.

────────────────────────────────────────────────────────
【수집해야 하는 정보】
────────────────────────────────────────────────────────
- 스키어인지 보더인지
- 실력 (초보/중급/상급)
- 라이딩 스타일 (속도/트릭/카빙/파크/파우더/안정형 등)
- 성향 (기질형 키워드 또는 MBTI)
- 선호 슬로프 난이도
- 시즌 목표
- 예산대
- 혼자 타는지 / 함께 타는지
- 함께 타고 싶은 동료 스타일

────────────────────────────────────────────────────────
【공식 12 Archetype】
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
최종 타입 = 12 Archetype 중 하나 + (스키어/보더)
총 24개 조합 중 하나만 선택해야 한다.

────────────────────────────────────────────────────────
【사용자 카드 출력 형식】
────────────────────────────────────────────────────────

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
- 카드 형식은 절대 변경하지 않는다.
- 카드를 출력한 뒤에는 추가 메시지를 보내지 않는다.
- 추론 과정은 절대 노출하지 않는다.

이제 너는 파우디로서 첫 질문을 시작한다.
"""


# ============================================
# 2) Google Sheets 연결 (Drive API 사용 X)
# ============================================
SHEET_ID = "1MZQaCE8ez2dSYEMo35N2JLreQWjV5bjfof1KvsTZafE"

def connect_gsheet():
    info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    creds = Credentials.from_service_account_info(info, scopes=scopes)
    gc = gspread.authorize(creds)

    sh = gc.open_by_key(SHEET_ID)
    return sh


# ============================================
# 3) Google Sheet 저장 (3개 필드만)
# ============================================
def save_user_card_to_sheet(user_name, final_type, card_text):
    sh = connect_gsheet()
    ws = sh.sheet1

    # 찰떡궁합 파트너 추출
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
# 4) Stability AI 타로카드 이미지 생성 (multipart/form-data)
# ============================================
def generate_tarot_image(final_type):
    key = st.secrets["STABILITY_API_KEY"]

    prompt = (
        f"Tarot card style illustration of a {final_type} skiing or snowboarding, "
        "fantasy lighting, ornate gold border, magical tarot atmosphere, elegant, highly detailed"
    )

    url = "https://api.stability.ai/v2beta/stable-image/generate/core"

    headers = {
        "Authorization": f"Bearer {key}",
        "Accept": "image/*",        # ← Stability 문서 필수
    }

    # multipart/form-data 강제
    files = {"none": (None, "")}

    data = {
        "prompt": prompt,
        "aspect_ratio": "1:2",
        "output_format": "png",
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code != 200:
        st.error("Stability API 오류 발생")
        st.write(response.text)
        return None

    return response.content


# ============================================
# 5) GPT 클라이언트
# ============================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# ============================================
# 6) Streamlit UI 구성
# ============================================
st.title("⛷️ 파우디 챗봇")
st.write("스키/보드 성향을 분석하여 타로 카드 스타일로 만들어줘요!")


# 세션 상태 초기화
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
    first_msg = (
        f"안녕 {st.session_state.user_name}! 나는 파우디야⛷️❄️ "
        "너의 스키/보드 성향을 알아보고 멋진 카드를 만들어줄게! "
        "먼저, 너는 스키어야? 보더야?"
    )

    st.chat_message("assistant").write(first_msg)
    st.session_state.messages.append({"role": "assistant", "content": first_msg})
    st.session_state.first_greeted = True


# ============================================
# 9) 대화 처리
# ============================================
if st.session_state.first_greeted and not st.session_state.card_done:
    user_input = st.chat_input("파우디에게 말해보세요!")

    if user_input:
        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # GPT 응답
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )

        reply = response.choices[0].message.content
        st.chat_message("assistant").write(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # 카드 생성 감지
        if "🎴 **PowderGuide 사용자 카드**" in reply:
            st.session_state.card_done = True

            # 타입 추출
            m = re.search(r"\[\s*(.*?)\s*\]", reply)
            final_type = m.group(1) if m else "Unknown"

            # Google Sheets 저장
            save_user_card_to_sheet(
                user_name=st.session_state.user_name,
                final_type=final_type,
                card_text=reply
            )

            st.success("Google Sheets 저장 완료!")

            # Stability 이미지 생성
            img = generate_tarot_image(final_type)
            if img:
                st.image(img, caption=f"{final_type} 타로 카드", width=450)
