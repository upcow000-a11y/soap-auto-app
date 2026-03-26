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
    session_count = st.number_input("회차 수", min_value=1, max_value=30, step=1, value=1)

with col2:
    age = st.number_input("나이", min_value=0, max_value=120, step=1)
    sex = st.selectbox("성별", ["M", "F"])


# -------- SOAP 생성 함수 --------
def generate_soap(body_part, nrs, age, sex, session_count):
    prompt = f"""
너는 물리치료 임상 SOAP 노트를 작성하는 전문가다.

입력:
통증부위: {body_part}
초진 NRS: {nrs}
나이: {age}
성별: {sex}
회차 수: {session_count}

규칙:
- 허구 환자 케이스 생성
- 한글 기반으로 작성하되, 핵심 해부학/운동학 용어는 영어 원어 병행 사용
- 과도한 영어 사용 금지 (차트 기록 스타일 유지)
- 임상에서 실제 쓰는 혼합형 표현 사용 (예: "외전 시 painful arc", "supraspinatus 약화")
- 자연스러운 임상 기록 스타일 (한글+영어 혼용)
- 불필요한 풀네임 설명 금지 (약어 그대로 사용)
- 축약어 사용 (AROM, PROM, MMT, ER, IR, GH joint 등)
- 기록 스타일 유지,설명문 금지
- 수치,각도,근력은 임상적으로 plausible하게 설정
- Special test, palpation 반드시 포함
- Key impairment 반드시 포함
- Plan은 반드시 아래 포함:
  (Manual Therapy / Exercise Therapy / Education / Progression)
- 각 항목은 핵심 위주로 작성
- 각 회차의 S,O,A,P는 각각 최대 4줄 이내
- 전체적으로 concise하게 작성
- 입력된 회차 수만큼 SOAP를 순차적으로 생성
- 반드시 1회차부터 {session_count}회차까지 모두 생성
- 각 회차는 동일 환자의 치료 경과를 반영해야 함
- 초진 NRS는 1회차 기준으로 사용
- 회차가 증가할수록 NRS는 점진적으로 감소하거나 안정화
- ROM, strength, 기능은 점진적으로 개선되는 흐름으로 작성
- Special test는 점진적으로 감소 경향 또는 부분 호전 양상 반영
- Plan은 회차가 지날수록 progression이 반영되어야 함
- 매 회차 내용은 서로 조금씩 달라야 하며,복붙처럼 같으면 안 됨
- 실제 임상 차트처럼 짧고 딱딱하게 작성

부위별 패턴 참고:
- Shoulder: painful arc, Hawkins, Neer, Empty can, supraspinatus, greater tuberosity
- L-spine: flexion limitation, paraspinal tightness, SLR, PA provocation
- C-spine: rotation limitation, UT/levator tightness, Spurling
- Knee: squat pain, step-down, patellar tracking
- Ankle: inversion sprain pattern, ATFL tenderness

출력 형식:
반드시 아래 형식을 회차 수만큼 반복할 것.

[1회차]
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

[2회차]
위와 동일 형식

[3회차]
위와 동일 형식

...
마지막 회차까지 반복
"""

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt
    )

    return response.output_text


# -------- 버튼 --------
if st.button("SOAP 생성"):
    try:
        result = generate_soap(body_part, nrs, age, sex, session_count)

        st.success("생성 완료")
        st.text_area("SOAP NOTE", result, height=900)

    except Exception as e:
        st.error(f"오류 발생: {e}")
