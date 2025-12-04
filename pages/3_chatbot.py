import streamlit as st
import re
import json
import requests
from openai import OpenAI
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from io import BytesIO
from PIL import Image
from datetime import datetime


# =====================================================================
# 1) SYSTEM PROMPT 정의 (기존 코드 그대로 사용)
# =====================================================================
SYSTEM_PROMPT = """
너는 PowderGuide의 전용 캐릭터 "파우디(Powdi)"야.  
밝고 다정하고, 스키/보드 문화를 누구보다 잘 아는 성향 분석 전문가이자 조언자야.  
너의 역할은 다음 흐름을 정확히 따르는 것이다:

────────────────────────────────────────
【파우디의 대화 방식 규칙】
────────────────────────────────────────
1. 질문은 반드시 **한 번에 하나씩** 한다.
2. 정보 수집이 끝나기 전까지 절대 타입을 암시하거나 언급하지 않는다.
3. 사용자가 편안하게 대답할 수 있도록 **따뜻하고 친근한 말투**로 묻는다.
4. 대화는 자연스러운 인터뷰처럼 진행되며, 필요 시 꼬리질문을 할 수 있다.
5. 정보가 충분히 모였다고 판단하면 자동으로 분석을 시작한다.
6. 분석 결과는 **단 한 번만**, 아래 정의된 “PowderGuide 사용자 카드” 형식으로 출력한다.
7. 카드 출력 후에는 **아무 말도 하지 않는다.** (추가 질문·대답 금지)

────────────────────────────────────────
【수집해야 하는 정보】
────────────────────────────────────────
- 스키어인지 보더인지
- 실력 (초보 / 중급 / 상급)
- 라이딩 스타일 (속도 / 트릭 / 카빙 / 파크 / 파우더 / 안정형 등)
- 성향 (MBTI 또는 기질적 특징 한두 가지)
- 선호 슬로프 난이도 (초급 / 중급 / 상급)
- 시즌 목표
- 장비·의류 예산대
- 혼자 타는지 / 여럿이 타는지
- 같이 타고 싶은 동료 스타일

────────────────────────────────────────
【PowderGuide 12 Archetype 성향 목록】
────────────────────────────────────────
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

────────────────────────────────────────
【최종 타입 산출 규칙】
────────────────────────────────────────
- 최종 타입은 반드시 “성향 + 장르(스키어/보더)” 형식이다.
  예: 도전형 보더, 리듬형 카빙러 스키어, 안전관리형 보더
- 총 24개 조합 중 하나만 선택해야 한다.
- 사용자의 키워드, 태도, 목표, 실력, 슬로프 취향에서 가장 지배적인 특징을 기반으로 성향(Type)을 결정한다.
- 임의로 새로운 타입을 만들지 않는다.

────────────────────────────────────────
【PowderGuide 사용자 카드 출력 형식】
────────────────────────────────────────
아래 형식을 정확히 따라 한 번만 출력한다.  
(대괄호, 굵은 글씨 포함 원문 그대로 출력)

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

────────────────────────────────────────
【주의】
────────────────────────────────────────
- 위 카드 형식은 절대 변경하지 않는다.
- 추론 과정은 절대로 드러내지 않는다.
- 카드 생성 후에는 **추가 메시지를 생성하지 않는다.**
- 오직 자연스러운 대화 속에서 정보를 수집한 뒤, 마지막에만 카드를 출력한다.
- 카드를 출력할 때는 따뜻하고 긍정적이며 사용자에게 기분 좋은 글로 작성한다.

────────────────────────────────────────
이제 너는 파우디로서 사용자에게 질문하며 정보를 수집한다.
사용자가 이름을 입력한 뒤 처음 말을 걸기 전까지는 조용히 기다린다.
────────────────────────────────────────

"""

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# =====================================================================
# 2) 세션 초기화 (✨가장 중요)
# =====================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "first_greeted" not in st.session_state:
    st.session_state.first_greeted = False

if "card_done" not in st.session_state:
    st.session_state.card_done = False



# =====================================================================
# 3) Google Sheet 저장 함수
# =====================================================================
def connect_gsheet(sheet_name: str):
    info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
    gc = gspread.authorize(creds)
    return gc.open(sheet_name)


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



# =====================================================================
# 4) Stability API — 타입별 타로 카드 이미지 생성
# =====================================================================
def generate_tarot_image(final_type: str) -> Image.Image:
    prompt = f"tarot card illustration of a {final_type}, full body, snow mountain, ornate golden frame"

    headers = {"Authorization": f"Bearer {st.secrets['STABILITY_API_KEY']}", "Accept": "image/*"}
    files = {"prompt": (None, prompt), "output_format": (None, "png")}

    res = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/core",
        headers=headers,
        files=files,
    )

    return Image.open(BytesIO(res.content))



# =====================================================================
# 5) UI — Powdi 챗봇 화면
# =====================================================================
st.title("⛷️🏂 Powdi 챗봇 — 사용자 카드 생성")



# =====================================================================
# 6) 사용자 이름 입력 + Powdi 자동 인사
# =====================================================================
input_name = st.text_input("당신의 이름을 입력해주세요!", value=st.session_state.user_name)

# "입력 완료" 시점 파악
if input_name and st.session_state.user_name == "":
    st.session_state.user_name = input_name

    # Powdi 첫 인사 자동 생성
    greet = (
        f"안녕 {input_name}! 난 파우디야 ⛷️❄️\n"
        "너의 스키/보드 성향을 알아볼 수 있도록 하나씩 질문해볼게!"
    )

    st.session_state.messages.append({"role": "assistant", "content": greet})
    st.session_state.first_greeted = True



# =====================================================================
# 7) 기존 메시지 출력
# =====================================================================
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])



# =====================================================================
# 8) Powdi 질문/답변 루프 — 이름 입력 후만!!
# =====================================================================
if st.session_state.first_greeted and not st.session_state.card_done:

    user_input = st.chat_input("파우디에게 답해주세요!")

    if user_input:

        # 사용자 메시지 저장
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # GPT 호출
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        reply = res.choices[0].message.content

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

        # 카드 생성 여부 확인
        if "PowderGuide 사용자 카드" in reply:
            st.session_state.card_done = True

            # 타입 추출
            m = re.search(r"\[(.*?)\]", reply)
            final_type = m.group(1) if m else "Unknown"

            # 시트 저장
            save_user_card_to_sheet(
                user_name=st.session_state.user_name,
                final_type=final_type,
                card_text=reply,
                conversation=st.session_state.messages,
            )

            st.success("Google Sheet 저장 완료!")

            # 이미지 생성
            st.markdown("### 🎨 Powdi가 타로 카드를 그리고 있어요...")
            img = generate_tarot_image(final_type)
            st.image(img, use_column_width=True)

