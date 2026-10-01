"""Web UI for the club facility booking agent (Streamlit). Run with: streamlit run app.py"""
import contextlib
import io

import streamlit as st

from src.agent import CafeAgent
from src.tools import data_store

st.set_page_config(page_title="동아리 시설 예약 에이전트", page_icon="🏫")

if "agent" not in st.session_state:
    st.session_state.agent = CafeAgent()
if "messages" not in st.session_state:
    st.session_state.messages = []  # {"role", "content", "tool_log"}

with st.sidebar:
    st.header("🏫 동아리 시설 예약")

    st.subheader("시설 목록")
    facilities = data_store.load("facilities")
    st.table([
        {
            "시설": name,
            "수용인원": f"{info['capacity']}명",
            "운영시간": f"{info['open_time']}~{info['close_time']}",
            "시간당 요금": f"{info['hourly_rate']:,}원",
        }
        for name, info in facilities.items()
    ])

    st.subheader("예약 현황")
    reservations = data_store.load("reservations")["records"]
    sorted_records = sorted(reservations, key=lambda r: (r["date"], r["start_time"]))
    if sorted_records:
        st.table([
            {
                "날짜": r["date"],
                "시설": r["facility"],
                "시간": f"{r['start_time']}~{r['end_time']}",
                "동아리": r["club_name"],
                "목적": r["purpose"],
            }
            for r in sorted_records
        ])
    else:
        st.caption("등록된 예약이 없습니다.")

    col1, col2 = st.columns(2)
    col1.metric("전체 예약 건수", len(reservations))
    col2.metric("등록 시설 수", len(facilities))

    if st.button("새로고침"):
        st.rerun()

st.title("🏫 동아리 시설 예약 에이전트")
st.caption("자연어로 물어보세요: 빈 시간 찾기, 일정 확인, 예약까지 한 번에.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("tool_log"):
            with st.expander("🔧 tool calls"):
                st.code(msg["tool_log"])
        st.markdown(msg["content"])

if user_input := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": user_input, "tool_log": None})
    with st.chat_message("user"):
        st.markdown(user_input)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        reply = st.session_state.agent.run(user_input)
    tool_log = buf.getvalue().strip()

    st.session_state.messages.append({"role": "assistant", "content": reply, "tool_log": tool_log or None})
    with st.chat_message("assistant"):
        if tool_log:
            with st.expander("🔧 tool calls"):
                st.code(tool_log)
        st.markdown(reply)
