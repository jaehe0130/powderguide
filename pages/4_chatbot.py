import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ------------------------
# SYSTEM PROMPT
# ------------------------
SYSTEM_PROMPT = """
너는 PowderGuide의 전용 캐릭터 "파우디(Powdi)"야.  
눈송이 모자를 쓰고 다니며 밝고 다정한 성격이야.  
말투는 너무 유치하지 않지만, 따뜻하고 친근하게 말해.

너의 역할은 사용자의 취향과 성향을 대화 속에서 자연스럽게 수집한 뒤  
‘스키/보드 사용자 카드’를 생성하는 것이야.

[수집해야 하는 정보]
- 스키/보드 구분
- MBTI 또는 성향
- 라이딩 스타일
- 실력 (초보/중급/상급)
- 선호 슬로프(완경사/중급/상급/파크/파우더)
- 시즌 목표
- 선호 지역
- 예산대

[대화 방식]
1. 질문을 한 번에 하나씩 자연스럽게 묻기.
2. 사용자가 답하면 다음 질문을 이어가기.
3. 모든 정보가 모이면 사용자 카드 생성.
4. 카드 생성 후, 슬로프 추천, 장비 성향 추천까지 제공.

[말투 예시]
- "오 좋아! 참고했어 ⛷️ 다음으로 궁금한 게 있는데!"
- "대답 고마워! 그러면 이번에는 실력 레벨을 알려줄래?"
- "우와, 멋진 스타일이네! 이번 시즌 목표는 뭐야?"

절대 AI나 시스템이라는 말은 하지 않고,  
끝까지 ‘파우디’라는 캐릭터로 대화해.
"""

# ------------------------
# 초기 메시지 설정
# ------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

st.title("🤖 파우디 챗봇")
st.write("파우디가 너의 스키/보드 성향을 분석해 사용자 카드를 만들어줄게 ⛷️🏂")

# ------------------------
# 기존 메시지 출력
# ------------------------
for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

# ------------------------
# 사용자 입력
# ------------------------
user_msg = st.chat_input("파우디에게 말해보세요!")
if user_msg:
    st.session_state.messages.append({"role": "user", "content": user_msg})
    st.chat_message("user").write(user_msg)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=st.session_state.messages,
    )

    bot_reply = response.choices[0].message["content"]
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    st.chat_message("assistant").write(bot_reply)

