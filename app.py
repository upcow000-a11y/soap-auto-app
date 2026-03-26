import streamlit as st
from openai import OpenAI
import sqlite3
from datetime import datetime

st.set_page_config(page_title="SOAP 시뮬레이터", layout="wide")

st.title("SOAP 시뮬레이터")
st.caption("최소 입력으로 임상형 SOAP 자동 생성")

# -------- DB 연결 및 테이블 생성 --------
conn = sqlite3.connect("soap.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS soap_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    patient_name TEXT,
    body_part TEXT,
    nrs INTEGER,
    age INTEGER,
    sex TEXT,
    session_count INTEGER,
    extra_notes TEXT,
    result TEXT
)
""")
conn.commit()

# -------- OpenAI API Key --------
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
    patient_name = st.text_input("환자 이름")
    age = st.number_input("나이", min_value=0, max_value=120, step=1)
    sex = st.selectbox("성별", ["M", "F"])
    extra_notes = st.text_area(
        "추가 요청사항",
        placeholder="예: 식당 종업원으로 근무하는 여성. 총 1회부터 10회까지 치료했고 6회차까지 호전, 7회차부터 악화되어 추가 치료 필요.",
        height=140,
        max_chars=400
    )

# -------- SOAP 생성 함수 --------
def generate_soap(body_part, nrs, age, sex, session_count, extra_notes):
    prompt = f"""
너는 물리치료 임상 SOAP 노트를 작성하는 전문가다.

입력:
통증부위: {body_part}
초진 NRS: {nrs}
나이: {age}
성별: {sex}
회차 수: {session_count}
추가 요청사항: {extra_notes}

규칙:
- 허구 환자 케이스 생성
- 한글 기반으로 작성하되, 핵심 해부학/운동학 용어는 영어 원어 병행 사용
- 과도한 영어 사용 금지 (차트 기록 스타일 유지)
- 임상에서 실제 쓰는 혼합형 표현 사용 (예: "외전 시 painful arc", "supraspinatus 약화")
- 자연스러운 임상 기록 스타일 (한글+영어 혼용)
- 불필요한 풀네임 설명 금지 (약어 그대로 사용)
- 축약어 사용 (AROM, PROM, MMT, ER, IR, GH joint 등)
- 기록 스타일 유지, 설명문 금지
- 수치, 각도, 근력은 임상적으로 plausible하게 설정
- Special test, palpation 반드시 포함
- Key impairment 반드시 포함
- Plan은 반드시 아래 포함:
  (Manual Therapy / Exercise Therapy / Education / Progression)
- 각 항목은 핵심 위주로 작성
- 각 회차의 S, O, A, P는 각각 최대 4줄 이내
- 전체적으로 concise하게 작성
- 입력된 회차 수만큼 SOAP를 순차적으로 생성
- 반드시 1회차부터 {session_count}회차까지 모두 생성
- 각 회차는 동일 환자의 치료 경과를 반영해야 함
- 초진 NRS는 1회차 기준으로 사용
- 기본적으로 회차가 증가할수록 NRS는 점진적으로 감소하거나 안정화
- 기본적으로 ROM, strength, 기능은 점진적으로 개선되는 흐름으로 작성
- 기본적으로 Special test는 점진적으로 감소 경향 또는 부분 호전 양상 반영
- Plan은 회차가 지날수록 progression이 반영되어야 함
- 매 회차 내용은 서로 조금씩 달라야 하며, 복붙처럼 같으면 안 됨
- 실제 임상 차트처럼 짧고 딱딱하게 작성
- 추가 요청사항이 있으면 SOAP 흐름에 반영하되, 전체 형식과 기록 스타일은 유지
- 추가 요청사항은 직업, 활동 특성, 회차별 호전/악화 패턴, 기능 제한, 치료 목표, 경과 변화에 반영 가능
- 추가 요청사항에 특정 회차 이후 악화, flare-up, plateau, 추가 치료 필요 등의 내용이 있으면 반드시 회차 흐름에 반영
- 추가 요청사항을 그대로 복붙하지 말고 임상 기록 문체로 자연스럽게 반영
- 추가 요청사항이 비어 있으면 기본적인 임상 경과 패턴으로 생성
- 추가 요청사항이 기본 경과 규칙과 충돌하면, 추가 요청사항을 우선 반영하되 임상적 plausibility와 SOAP 형식은 유지
- 한 회차라도 지나치게 좋아지거나 급격히 완치되는 흐름은 피할 것
- 마지막 회차에서 증상이 남아있다면 Assessment와 Plan에 continued treatment 필요성을 반영할 것

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

# -------- DB 함수 --------
def save_history(patient_name, body_part, nrs, age, sex, session_count, extra_notes, result):
    cursor.execute("""
        INSERT INTO soap_history (
            created_at, patient_name, body_part, nrs, age, sex, session_count, extra_notes, result
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        patient_name,
        body_part,
        nrs,
        age,
        sex,
        session_count,
        extra_notes,
        result
    ))
    conn.commit()

def load_history(search_name=""):
    if search_name.strip():
        cursor.execute("""
            SELECT id, created_at, patient_name, body_part, nrs, age, sex, session_count, extra_notes, result
            FROM soap_history
            WHERE patient_name LIKE ?
            ORDER BY id DESC
        """, (f"%{search_name.strip()}%",))
    else:
        cursor.execute("""
            SELECT id, created_at, patient_name, body_part, nrs, age, sex, session_count, extra_notes, result
            FROM soap_history
            ORDER BY id DESC
        """)
    return cursor.fetchall()

def delete_history(record_id):
    cursor.execute("DELETE FROM soap_history WHERE id = ?", (record_id,))
    conn.commit()

# -------- 생성 버튼 --------
if st.button("SOAP 생성"):
    try:
        if not patient_name.strip():
            st.error("환자 이름을 입력해줘.")
        else:
            result = generate_soap(body_part, nrs, age, sex, session_count, extra_notes)
            save_history(patient_name, body_part, nrs, age, sex, session_count, extra_notes, result)

            st.success("생성 및 저장 완료")
            st.text_area("SOAP NOTE", result, height=900)

    except Exception as e:
        st.error(f"오류 발생: {e}")

# -------- 저장 기록 보기 --------
st.divider()
st.subheader("저장된 기록")

search_name = st.text_input("환자 이름 검색", placeholder="이름 일부만 입력해도 검색됨")

history = load_history(search_name)

if not history:
    st.info("저장된 기록이 없습니다.")
else:
    for item in history:
        record_id, created_at, h_patient_name, h_body_part, h_nrs, h_age, h_sex, h_session_count, h_extra_notes, h_result = item

        title = f"{record_id} | {created_at} | {h_patient_name} | {h_body_part} | NRS {h_nrs} | {h_age}세 | {h_sex} | {h_session_count}회차"

        with st.expander(title):
            if h_extra_notes:
                st.markdown(f"**추가 요청사항:** {h_extra_notes}")

            st.text_area(
                f"SOAP_NOTE_{record_id}",
                h_result,
                height=400,
                key=f"soap_result_{record_id}"
            )

            if st.button("삭제", key=f"delete_{record_id}"):
                delete_history(record_id)
                st.success(f"{record_id}번 기록 삭제 완료")
                st.rerun()
