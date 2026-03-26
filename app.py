import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="SOAP 시뮬레이터", layout="wide")

st.title("SOAP 시뮬레이터")
st.caption("최소 입력으로 임상형 SOAP 자동 생성")

# OpenAI API Key
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("OPENAI_API_KEY 설정 필요")
    st.stop()

# -------- 입력 --------
col1, col2 = st.columns(2)

with col1:
    st.subheader("기본 입력")
    body_part = st.selectbox("통증부위", ["Shoulder", "C-spine", "L-spine", "Knee", "Ankle"])
    nrs = st.slider("초진 NRS", 0, 10, 5)

with col2:
    age = st.number_input("나이", min_value=0, max_value=120, step=1)
    sex = st.selectbox("성별", ["M", "F"])


# -------- SOAP 생성 함수 --------
def generate_soap(body_part, nrs, age, sex):
    prompt = f"""
너는 물리치료 임상 SOAP 노트를 작성하는 전문가다.

입력:
통증부위: {body_part}
NRS: {nrs}
나이: {age}
성별: {sex}

규칙:
- 허구 환자 케이스 생성
- 해부학적 용어 및 영어 원어 적극 사용
- 축약어 사용 (AROM, PROM, MMT, ER, IR, GH joint 등)
- 기록 스타일 (설명 금지)
- 수치/각도/근력 임상적으로 plausible하게 설정
- Special test, palpation 반드시 포함
- Key impairment 반드시 포함
- Plan은 반드시 아래 포함:
  (Manual Therapy / Exercise Therapy / Education / Progression)

부위별 패턴 참고:
- Shoulder: painful arc, Hawkins, Neer, Empty can, supraspinatus, greater tuberosity
- L-spine: flexion limitation, paraspinal tightness, SLR, PA provocation
- C-spine: rotation limitation, UT/levator tightness, Spurling
- Knee: squat pain, step-down, patellar tracking
- Ankle: inversion sprain pattern, ATFL tenderness

출력 형식:

S (Subjective)
CC:
HPI:
NRS:
Aggravating:
Easing:
Goal:

O (Objective)
AROM:
PROM:
Strength:
Special test:
Palpation:

A (Assessment)
Impression:
Key impairment:

P (Plan)
Manual Therapy:
Exercise Therapy:
Education:
Progression:
"""

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt
    )

    return response.output_text


# -------- 버튼 --------
if st.button("SOAP 생성"):
    result = generate_soap(body_part, nrs, age, sex)

    st.success("생성 완료")

    st.text_area("SOAP NOTE", result, height=600)
