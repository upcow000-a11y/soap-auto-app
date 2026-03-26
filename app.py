import streamlit as st

st.title("SOAP 자동화 시스템")

name = st.text_input("환자 이름")
pain = st.text_input("주요 통증")

if st.button("SOAP 생성"):
    st.write("### S (Subjective)")
    st.write(f"{name} 환자, {pain} 호소")

    st.write("### O (Objective)")
    st.write("ROM 제한 및 통증 유발")

    st.write("### A (Assessment)")
    st.write("근골격계 기능 저하 의심")

    st.write("### P (Plan)")
    st.write("운동치료 및 자세교정 진행")
