# app.py
# ⛷️🏂 파우디 스키복/보드복 스타일 + Stable Diffusion 이미지 생성 Streamlit 앱

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
그 결과를 바탕으로 **Stable Diffusion으로 스키장 패션 일러스트**를 생성할게!
"""
)

# 🔐 API 키는 Streamlit secrets 에서 가져오기
# - Streamlit Cloud 기준: Settings → Secrets 에 아래처럼 등록
#   OPENAI_API_KEY = "sk-xxxx"
#   STABILITY_API_KEY = "sk-xxxx"
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
STABILITY_API_KEY = st.secrets["STABILITY_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

# 텍스트용 LLM 모델
MODEL = "gpt-4o-mini"

# Stability AI 이미지 엔드포인트
STABILITY_ENDPOINT = "https://api.stability.ai/v2beta/stable-image/generate/core"


# ================================
# 1) 프롬프트 기법별 System Prompt
# ================================
SYS_COT = """당신은 수많은 스키어와 보더의 스타일을 담당해본 '스노우 스타일리스트 AI'입니다.
- 내부 사고과정은 숨기고, 최종 결과 요약과 핵심 근거만 출력합니다.
- 사용자의 실력, 라이딩 스타일(속도/트릭/카빙/파크/파우더), 체형, 체감온도, 선호 색감,
  스키복/보드복 브랜드 취향, 예산을 반드시 반영합니다.
- 스키장 조명, 설질, 슬로프 환경, 활동량 등을 고려해 실제로 어울리는 스타일만 제안합니다.
- 한국어로 답변합니다.
"""

SYS_TOT = """당신은 '스키장 스타일 전략가'입니다.
- 서로 다른 3가지 스타일 경로(예: 테크웨어·스트릿 보더룩 / 미니멀 스키룩 / 포토제닉 뉴트럴 룩)를 각각 5~7줄로 제시합니다.
- 이후 간단한 평가표(1~5점: 실용성/보온성/사진발/활동성/난이도)를 제공합니다.
- 마지막으로 최종 추천안을 제시합니다.
- 내부 나뭇가지 추론 과정은 숨기고 결과만 출력합니다.
- 한국어로 응답합니다.
"""

SYS_SELFCONS = """당신은 '스키장 스타일 제안 컨설턴트'입니다.
- 관점이 다른 3안(예: 클래식 스키어룩 / 모던 스트릿 보더룩 / 대담한 컬러 포토제닉 룩)을 제시합니다.
- 각 안에 대해 기준별 점수(슬로프 적합성/사진발/착용 난이도/보온성/안전성)를 제공합니다.
- 3안 중 가장 일관성 높은 스타일을 최종안으로 선정합니다.
- 내부 합의 과정은 숨기고 결과만 출력합니다.
- 한국어로 작성합니다.
"""

SYS_REACT = """당신은 '스키장 스타일링 오퍼레이션 매니저'입니다.
- Plan → Action → Observation → Update 단계를 2~3회 반복해 최종 스타일 제안을 도출합니다.
- Plan: 방향성 설정(보온/실용/사진발/브랜드 무드 등)
- Action: 아이템 추천(자켓/팬츠/고글/장갑/부츠/비니 등)
- Observation: 사용자 조건 반영(실력·라이딩 스타일·예산·선호 색감·체형·체감 온도)
- Update: 수정 및 보완
- 마지막에 Final 스타일 제안을 제공합니다.
- 내부 사고과정은 숨기고 각 단계는 1~3줄로만 출력합니다.
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
# 3) 스타일 텍스트 추천 (OpenAI Chat)
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
    if method_name not in METHOD_TO_SYS:
        raise ValueError("프롬프트 기법 선택이 올바르지 않습니다.")

    system_prompt = METHOD_TO_SYS[method_name]
    user_prompt = build_rccf_prompt(role, context, constraints, fmt)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=float(temperature),
    )

    return f"### 기법: **{method_name}**\n\n" + resp.choices[0].message.content


# ================================
# 4) 이미지 프롬프트 생성용 GPT 호출
# ================================
def build_image_prompt_from_text(style_text: str) -> str:
    """
    스타일 추천 텍스트(한국어)를 받아
    스키/보드 패션 일러스트용 짧은 영어 프롬프트로 변환.
    """
    system_msg = (
        "You are a fashion illustration prompt engineer specializing in ski and snowboard outfits. "
        "Given a Korean styling recommendation, output ONE concise English prompt "
        "for a full-body fashion illustration at a snowy ski resort. "
        "Focus on ski jacket, pants silhouette, color palette, texture, goggles, gloves, boots, and vibe. "
        "Do not add location names. No explanations, just the prompt. 40 words or less."
    )

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": style_text},
        ],
        temperature=0.4,
    )

    prompt_en = resp.choices[0].message.content.strip()
    return prompt_en


# ================================
# 5) Stability AI로 스키장 패션 이미지 생성
# ================================
def generate_fashion_image_with_stability(style_text: str) -> Image.Image:
    """
    1) 스타일 추천 텍스트 → 영어 이미지 프롬프트 생성 (OpenAI)
    2) Stability AI Stable Diffusion API로 이미지 생성
    3) PIL.Image 객체 반환
    """
    img_prompt = build_image_prompt_from_text(style_text)

    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/*",
    }

    # multipart/form-data 형식
    files = {
        "prompt": (None, img_prompt),
        "output_format": (None, "png"),
    }

    response = requests.post(
        STABILITY_ENDPOINT,
        headers=headers,
        files=files,
        timeout=120,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Stability API 오류: {response.status_code} - {response.text[:500]}"
        )

    img_bytes = BytesIO(response.content)
    img = Image.open(img_bytes)
    return img


# ================================
# 6) Streamlit UI
# ================================
with st.form("style_form"):
    col1, col2 = st.columns(2)

    with col1:
        role = st.text_area(
            "Role",
            value="파우디의 스키장 스타일 컨설턴트",
            height=60,
        )

        method = st.selectbox(
            "프롬프트 기법",
            options=list(METHOD_TO_SYS.keys()),
            index=0,
        )

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.2,
            value=0.7,
            step=0.1,
        )

    with col2:
        context = st.text_area(
            "Context (사용자 프로필)",
            value=(
                "사용자 프로필 예시: 보더, 중급자, 스트릿 & 뉴트럴 선호, "
                "체감온도 추움, 사진 잘 나오는 룩 선호. "
                "선호 브랜드: Burton/Volcom/Goldwin."
            ),
            height=90,
        )

        constraints = st.text_area(
            "Constraints (제약 조건)",
            value=(
                "보온성과 활동성 균형 필수, 2벌 추천(메인 룩 + 서브 룩), "
                "고글/장갑/비니 포함, 예산 범위 내 아이템 구성. "
                "실제 스키장 환경(설질·기온·주간/야간)을 반영."
            ),
            height=90,
        )

    fmt = st.text_area(
        "Format (출력 형식)",
        value=(
            "1) 스키장 룩 콘셉트(한 줄)\n"
            "2) 스키복/보드복 코디 제안(메인 1안 + 대안 1안)\n"
            "3) 장비 & 액세서리(고글·장갑·부츠·비니)\n"
            "4) 헤어·메이크업/사진발 팁(키포인트 3개)\n"
            "5) 리스크 & 완화(최대 3개 — 보온/습기/핏 문제)\n"
            "6) 스키장 체크리스트(6단계 — 레이어링/장비 세팅/체온 관리)"
        ),
        height=140,
    )

    submitted = st.form_submit_button("🎿 스타일 추천 + 이미지 생성")

if submitted:
    with st.spinner("파우디가 스타일을 고민하는 중... ⛷️"):
        try:
            # 1) 스타일 텍스트 추천
            style_text = run_chat(
                method_name=method,
                role=role,
                context=context,
                constraints=constraints,
                fmt=fmt,
                model=MODEL,
                temperature=temperature,
            )

            st.markdown("## 📝 스키장 스타일 추천 결과")
            st.markdown(style_text)

            # 2) 이미지 생성
            st.markdown("## 🎨 스키장 패션 일러스트")
            style_image = generate_fashion_image_with_stability(style_text)
            st.image(style_image, caption="PowderGuide 스키장 패션 일러스트", use_column_width=True)

        except Exception as e:
            st.error(f"⚠ 오류가 발생했습니다: {e}")
            with st.expander("Traceback 보기 (디버깅용)"):
                st.text("".join(traceback.format_exc()))
