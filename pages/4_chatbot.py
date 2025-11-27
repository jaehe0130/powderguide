import streamlit as st
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("🤖 파우디 챗봇")
st.write("파우디가 너의 스키/보드 성향을 분석해 사용자 카드를 만들어줄게 ⛷️🏂")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": YOUR_SYSTEM_PROMPT_HERE}
    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

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

