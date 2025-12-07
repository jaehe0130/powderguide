# app.py  (HuggingFace 이미지 생성 버전)

import streamlit as st
from openai import OpenAI
from PIL import Image
from io import BytesIO
import requests
import traceback

# ================================
# 0) 기본 설정 & 클라이언트
# ================================
st.set_page_config(
    page_title="파우디 스키복/보드복 스타일 챗봇",
    page_icon="⛷️",
    layout="centered",
)

st.title("⛷️🏂 파우디의 스키복/보드복 스타일 챗봇")
st.markdown(
"""
스키장 환경과 너의 취향을 반영해서 **스키복/보드복 스타일을 추천**하고,  
그 결과를 바탕으로 **AI로 스키장 패션 일러스트**를 생성할게!
"""
)

# API KEY 가져오기
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
HF_TOKEN = st.secrets["HUGGINGFACE_TOKEN"]

client = OpenAI(api_key=OPENAI_API_KEY)

MODEL = "gpt-4o-mini"

# ================================
# 1) 프롬프트 기법별 System Prompt
# ================================
SYS_COT = """당신은 수많은 스키어와 보더의 스타일을 담당해본 '스노우 스타일리스트 AI'입니다.
- 내부 사고과정은 숨기고, 최종 결과 요약과 핵심 근거만 출력합니다.
- 사용자의 실력, 라이딩 스타일(속도/트릭/카빙/파크/파우더), 체형, 체감온도, 선호 색감,
  스키복/보드복 브랜드 취향, 예산을 반드시 반영합니다.
- 한국어로 답변합니다.
"""

SYS_TOT = """당신은 '스키장 스타일 전략가'입니다.
- 서로 다른 3가지 스타일 경로를 제시합니다.
- 각 안마다 장점/리스크를 설명합니다.
- 한국어로 작성합니다.
"""

SYS_SELFCONS = """당신은 '스키장 스타일 제안 컨설턴트'입니다.
- 관점이 다른 3안 제시 후 가장 이상적인 디자인을 선정합니다.
- 한국어로 작성합니다.
"""

SYS_REACT = """당신은 '스키장 스타일링 오퍼레이션 매니저'입니다.
- Plan → Action → Observation → Update 단계를 2회 반복해 최종 스타일 제안을 도출합니다.
- 한국어로 작성합니다.
"""

METHOD_TO_SYS = {
    "Chain-of-Thought(요약형)": SYS_COT,
    "Tree-of-Thought": SYS_TOT,
    "Self-Consistency": SYS_SELFCONS,
    "ReAct": SYS_REACT,
}

# ================================
# 2) RCCF 스타일 프롬프트 빌더
# ================================
def build_rccf_prompt(role: str, context: str, constraints: str, fmt: str) -> str:
    return f"""[Role]
{role}
[Context]
{context}
[Constraints]
{constraints}
[Format]
{fmt}
"""

# ================================
# 3) 스타일 텍스트 추천
# ================================
def run_chat(
    method_name: str,
    role: str,
    context: str,
    constraints: str,
    fmt: str,
    model: str = MODEL,
    temperature: float = 0.7,
) -> str:

    system_prompt = METHOD_TO_SYS.get(method_name)
    user_prompt = build_rccf_prompt(role, context, constraints, fmt)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=float(temperature),
    )

    return f"### 🎨 프롬프트 기법: **{method_name}**\n\n" + resp.choices[0].message.content


# ================================
# 4) GPT가 이미지 프롬프트 요약
# ================================
def build_image_prompt_from_text(style_text: str) -> str:
    system_msg = (
        "You are a fashion illustration prompt engineer. "
        "Convert the Korean recommendation into one concise English prompt "
        "for a stylish snowboard or ski outfit. Keep it under 40 words."
    )

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": style_text},
        ],
        temperature=0.4,
    )

    return resp.choices[0].message.content.strip()


# ================================
# 5) HuggingFace Image Generation
# ================================
def generate_fashion_image_huggingface(style_text: str):
    prompt = build_image_prompt_from_text(style_text)

    response = requests.post(
        "https://api-inference.huggingface.co/models/stabilityai/sdxl-turbo",
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        json={"inputs": prompt, "parameters": {"num_inference_steps": 25}}
    )

    if response.status_code != 200:
        raise RuntimeError(f"HF API Error: {response.text}")

    return Image.open(BytesIO(response.content))


# ================================
# 6) Streamlit UI
# ================================
with st.form("style_form"):

    col1, col2 = st.columns(2)

    with col1:
        role = st.text_area("Role", "파우디의 스키장 스타일 컨설턴트", height=60)

        method = st.selectbox(
            "프롬프트 기법",
            options=list(METHOD_TO_SYS.keys()),
            index=0,
        )

        temperature = st.slider("Temperature", 0.0, 1.2, 0.7, 0.1)

    with col2:
        context = st.text_area(
            "Context (사용자 프로필)",
            "보더, 중급자, 뉴트럴톤 선호, 사진 잘 나오는 룩 선호",
            height=90,
        )

        constraints = st.text_area(
            "Constraints (제약 조건)",
            "보온 균형 필수, 예산 고려, 고글 포함, 실제 스키장 환경 반영",
            height=90,
        )

    fmt = st.text_area(
        "Format",
        "1) 콘셉트\n2) 스키복/보드복 코디 제안\n3) 장비 & 액세서리\n4) 사진 잘 나오는 팁\n5) 리스크 & 완화",
        height=140,
    )

    submitted = st.form_submit_button("🎿 스타일 추천 + AI 이미지 생성")

if submitted:
    with st.spinner("파우디가 스타일을 디자인하는 중... ⛷️"):
        try:
            style_text = run_chat(
                method_name=method,
                role=role,
                context=context,
                constraints=constraints,
                fmt=fmt,
                temperature=temperature,
            )

            st.markdown("## 📝 스키장 스타일 추천 결과")
            st.markdown(style_text)

            st.markdown("## 🧊 AI 패션 일러스트 생성중...")
            style_image = generate_fashion_image_huggingface(style_text)

            st.image(style_image, caption="PowderGuide AI 패션 일러스트", use_column_width=True)

        except Exception as e:
            st.error(f"⚠ 오류 발생: {e}")
            with st.expander("Traceback (디버깅용)"):
                st.text("".join(traceback.format_exc()))
