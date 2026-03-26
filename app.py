import streamlit as st
import json
from openai import OpenAI

st.set_page_config(page_title="SOAP 자동화 시스템", layout="wide")

st.title("SOAP 자동화 시스템")
st.caption("환자 정보를 입력하면 SOAP 노트를 자동 생성합니다.")

# OpenAI API Key 불러오기
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("Streamlit Secrets에 OPENAI_API_KEY가 설정되지 않았습니다.")
    st.stop()

SYSTEM_PROMPT = """
너는 물리치료 SOAP 노트를 작성하는 보조도구다.

규칙:
1. 반드시 SOAP 형식으로 작성한다.
2. 입력값에 없는 사실은 추정하지 않는다.
3. 과장된 표현이나 확정 진단 표현을 피한다.
4. 보험 제출용 문체로 간결하고 객관적으로 작성한다.
5. 결과는 반드시 아래 JSON 형식으로 반환한다.

{
  "subjective": "...",
  "objective": "...",
  "assessment": "...",
  "plan": "..."
}
"""

def generate_soap(data):
    user_prompt = f"""
다음 환자 정보를 바탕으로 SOAP 노트를 작성하라.
입력값에 없는 내용은 쓰지 말 것.

환자정보:
{json.dumps(data, ensure_ascii=False, indent=2)}
"""

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=[
            {"role": "developer", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )

    text = response.output_text
    return json.loads(text)

col1, col2 = st.columns(2)

with col1:
    st.subheader("환자 기본정보")
    patient_id = st.text_input("환자 ID")
    patient_name = st.text_input("환자명")
    age = st.number_input("나이", min_value=0, max_value=120, step=1)
    sex = st.selectbox("성별", ["M", "F"])
    diagnosis = st.text_input("진단명")
    body_part = st.text_input("치료부위")
    session_no = st.number_input("회차", min_value=1, step=1)
    visit_date = st.date_input("치료일자")

with col2:
    st.subheader("당일 상태")
    chief_complaint = st.text_area("주호소")
    nrs = st.slider("통증점수 NRS", 0, 10, 5)
    aggravating = st.text_input("악화요인")
    relieving = st.text_input("완화요인")
    functional_limits = st.text_area("기능제한")
    rom_findings = st.text_area("ROM 소견")
    mmt_findings = st.text_area("MMT 소견")
    special_findings = st.text_area("특이소견")
    treatments_done = st.text_area("시행한 치료")
    response_to_treatment = st.text_area("치료 후 반응")
    plan_note = st.text_area("다음 계획 메모")

if st.button("SOAP 생성"):
    data = {
        "patient_id": patient_id,
        "patient_name": patient_name,
        "age": age,
        "sex": sex,
        "diagnosis": diagnosis,
        "body_part": body_part,
        "session_no": session_no,
        "visit_date": str(visit_date),
        "chief_complaint": chief_complaint,
        "nrs": nrs,
        "aggravating_factors": aggravating,
        "relieving_factors": relieving,
        "functional_limitations": functional_limits,
        "rom_findings": rom_findings,
        "mmt_findings": mmt_findings,
        "special_findings": special_findings,
        "treatments_done": treatments_done,
        "response_to_treatment": response_to_treatment,
        "plan_note": plan_note
    }

    try:
        soap = generate_soap(data)

        st.success("SOAP 생성 완료")

        st.subheader("S")
        st.text_area("Subjective", soap["subjective"], height=150)

        st.subheader("O")
        st.text_area("Objective", soap["objective"], height=180)

        st.subheader("A")
        st.text_area("Assessment", soap["assessment"], height=150)

        st.subheader("P")
        st.text_area("Plan", soap["plan"], height=150)

    except Exception as e:
        st.error(f"오류 발생: {e}")
