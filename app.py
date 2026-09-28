import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="HYUNDAI E&C Project Management Insight",
    page_icon="🏗️",
    layout="wide"
)

# -----------------------------
# 기본 스타일 — 코오롱 프로그램과 동일 구조
# -----------------------------
st.markdown("""
<style>
.block-container {padding-top: 1.8rem; padding-bottom: 2.5rem;}
h1, h2, h3 {letter-spacing: -0.03em;}
.hyundai-card {
    border: 1px solid #e8e8e8;
    border-radius: 16px;
    padding: 18px 20px;
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.hyundai-note {
    border-left: 4px solid #2458d3;
    background: #f6f8ff;
    padding: 14px 16px;
    border-radius: 8px;
    margin: 8px 0 14px 0;
}
.small {color:#666; font-size:0.9rem;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 공시자료 기반 데이터
# ============================================================

# 1) 수주잔고 → 건설계약 매출
# 연결 건설계약 주석 기준
backlog = pd.DataFrame({
    "시점": ["2024말", "2025말", "2026H1말"],
    "수주잔고_조원": [95.822, 95.039, 70.127]
})

contract_revenue = pd.DataFrame({
    "기간": ["2024", "2025", "2025H1", "2026H1"],
    "건설계약매출_조원": [31.248, 31.063, 14.477, 13.124]
})

# 2025말 수주잔고 / 2025 연결매출 참고 배수
backlog_sales_multiple = 95.039 / 31.063

# 2) 미청구공사: 연결 재무상태표
working = pd.DataFrame({
    "시점": ["2024말", "2025말", "2026H1말"],
    "미청구공사_조원": [4.685, 3.937, 4.482],
    "매출채권_조원": [5.319, 6.842, 7.236]
})
working["합계_조원"] = working["미청구공사_조원"] + working["매출채권_조원"]

# 3) 건설계약 주석상 부문별 '단기미청구공사'
# 동일한 도급공사 보고부문 기준
unbilled_segment = pd.DataFrame({
    "구분": ["토목", "건축/주택", "플랜트/전력"],
    "2025말_조원": [0.779, 1.395, 0.532],
    "2026H1말_조원": [0.895, 1.647, 0.459]
})
unbilled_segment["증감_조원"] = unbilled_segment["2026H1말_조원"] - unbilled_segment["2025말_조원"]

# 4) 총계약수익·총계약원가 추정 변경
estimate_2025 = pd.DataFrame({
    "구분": ["토목", "건축/주택", "플랜트/전력"],
    "당기손익영향_조원": [-0.107, -0.301, -0.574],
    "미청구공사변동_조원": [-0.148, -0.559, -0.517],
    "공사손실충당부채_조원": [0.000382, 0.008939, 0.060619]
})

estimate_2026h1 = pd.DataFrame({
    "구분": ["토목", "건축/주택", "플랜트/전력"],
    "당기손익영향_조원": [-0.071, -0.044, -0.233],
    "미청구공사변동_조원": [-0.119, -0.080, -0.153],
    "공사손실충당부채_조원": [0.001474, 0.013829, 0.029110]
})

# 5) 현금흐름
cashflow = pd.DataFrame({
    "기간": ["2025H1", "2026H1"],
    "영업활동현금흐름_조원": [-1.889, -1.677]
})

# ============================================================
# 공통 상단
# ============================================================
st.title("HYUNDAI E&C Project Management Insight")
st.caption("현대건설의 수주잔고 → 프로젝트 수행·매출 → 미청구공사·매출채권 → 현금회수를 연결해 보는 사업관리·재무분석 대시보드")

m1, m2, m3, m4 = st.columns(4)
m1.metric("2025 건설계약 매출", "약 31.06조원")
m2.metric("2025말 수주잔고", "약 95.04조원")
m3.metric("수주잔고 ÷ 2025 매출", f"약 {backlog_sales_multiple:.1f}배")
m4.metric("2026H1 미청구공사", "약 4.48조원", "+0.55조원")

st.markdown("""
<div class="hyundai-note">
<b>분석 방향</b><br>
① 확보한 프로젝트가 수주잔고와 미래 매출 기반으로 어떻게 이어지는가
→ ② 매출 인식 후 청구 전 단계의 미청구공사와 청구 후 회수 전 단계의 채권은 어떻게 변하는가
→ ③ 어느 사업부문에서 미청구공사가 늘었는가
→ ④ 예상원가 변경이 손익과 미청구공사에 어떤 영향을 주는가
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs([
    "① 수주잔고 → 프로젝트 수행 → 매출",
    "② 매출 → 청구 → 회수"
])

# ============================================================
# TAB 1 — 코오롱 프로그램의 '신규수주 → 수주잔고 → 매출' 구조
# ============================================================
with tab1:
    st.subheader("① 수주잔고 → 프로젝트 수행 → 매출 분석")
    st.write("수주잔고 총액만 보는 대신, 확보한 프로젝트가 실제 수행을 거쳐 건설계약 매출로 전환되는 흐름을 확인합니다.")

    st.markdown("#### 1. 확보한 프로젝트는 수주잔고로 얼마나 남아 있나?")
    a, b, c = st.columns(3)
    a.metric("2024말 수주잔고", "약 95.82조원")
    b.metric("2025말 수주잔고", "약 95.04조원", "-0.78조원")
    c.metric("2026H1말 수주잔고", "약 70.13조원")

    fig_backlog = px.line(
        backlog, x="시점", y="수주잔고_조원",
        markers=True, text="수주잔고_조원",
        labels={"수주잔고_조원":"수주잔고(조원)", "시점":""},
        title="건설계약 수주잔고 추이"
    )
    fig_backlog.update_traces(texttemplate="%{text:.2f}조", textposition="top center")
    fig_backlog.update_layout(yaxis_range=[60, 105])
    st.plotly_chart(fig_backlog, use_container_width=True)

    st.markdown("""
    <div class="hyundai-card"><b>해석</b><br><br>
    2024년 말 연결 건설계약 수주잔고는 약 <b>95.82조원</b>, 2025년 말에는 약 <b>95.04조원</b>입니다.
    수주잔고는 앞으로 수행해야 할 프로젝트 규모를 보여주지만, 계약변경·공정·원가·해지 등에 따라
    실제 매출 인식 시점과 금액은 달라질 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 2. 수주잔고는 실제 매출로 얼마나 전환되고 있나?")
    fig_sales = px.bar(
        contract_revenue,
        x="기간", y="건설계약매출_조원",
        text="건설계약매출_조원",
        labels={"건설계약매출_조원":"건설계약 매출(조원)", "기간":""},
        title="건설계약 매출"
    )
    fig_sales.update_traces(texttemplate="%{text:.2f}조", textposition="outside")
    st.plotly_chart(fig_sales, use_container_width=True)

    q1, q2, q3 = st.columns(3)
    q1.metric("2024 건설계약 매출", "약 31.25조원")
    q2.metric("2025 건설계약 매출", "약 31.06조원")
    q3.metric("2025말 잔고/매출", f"약 {backlog_sales_multiple:.1f}배")

    st.markdown(f"""
    <div class="hyundai-note"><b>수주잔고 → 미래 매출 기반</b><br><br>
    2025년 말 수주잔고 약 <b>95.04조원</b>은 2025년 건설계약 매출 약 <b>31.06조원</b>의
    약 <b>{backlog_sales_multiple:.1f}배</b>입니다. 이는 현재 매출 규모와 비교한 미래 사업 기반의 참고지표입니다.<br><br>
    다만 수주잔고가 동일 금액의 미래 매출을 보장하는 것은 아니므로,
    실제 사업관리에서는 <b>프로젝트별 진행률·예상원가·공사기한·청구조건</b>을 함께 관리해야 합니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 3. 반기 기준 프로젝트 매출은 어떻게 변했나?")
    half = contract_revenue[contract_revenue["기간"].isin(["2025H1","2026H1"])].copy()
    h1, h2 = st.columns(2)
    h1.metric("2025H1 건설계약 매출", "약 14.48조원")
    h2.metric("2026H1 건설계약 매출", "약 13.12조원", "-9.4%")

    st.markdown("""
    <div class="hyundai-card"><b>여기서 얻는 결론</b><br><br>
    2026년 상반기 건설계약 매출은 전년 동기보다 감소했습니다.
    따라서 수주잔고의 규모만으로 당기 성과를 판단하기보다,
    <b>어떤 프로젝트가 어느 속도로 수행되고 매출로 전환되는지</b>를 확인해야 합니다.
    사업관리 담당자는 수주 이후의 공정과 원가를 함께 연결해 향후 매출과 손익을 관리할 필요가 있습니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hyundai-card"><b>이 탭의 최종 결론</b><br><br>
    ① 현대건설은 2025년 말 약 <b>95조원</b>의 건설계약 수주잔고를 보유하고 있습니다.<br>
    ② 이는 2025년 건설계약 매출의 약 <b>3.1배</b>로, 장기간 관리해야 할 프로젝트 규모가 큽니다.<br>
    ③ 하지만 2026년 상반기 건설계약 매출은 전년 동기보다 감소했습니다.<br>
    ④ 따라서 <b>수주 확보에서 끝나는 것이 아니라 프로젝트별 진행률과 예상원가를 관리해 수주잔고가 계획한 매출과 손익으로 전환되는 과정을 관리하는 것</b>이 중요합니다.
    </div>
    """, unsafe_allow_html=True)

    st.caption("수주잔고는 연결 건설계약 주석 기준입니다. 2026H1은 반기 시점 잔액이므로 연말 수치와 단순한 연간 증감률 비교에는 주의가 필요합니다.")

# ============================================================
# TAB 2 — 코오롱 프로그램의 '매출 → 청구 → 회수' 구조
# ============================================================
with tab2:
    st.subheader("② 건설계약 매출 → 청구 → 회수 분석")
    st.write("미청구공사와 매출채권을 단순 잔액으로 보지 않고, 프로젝트 매출이 현금으로 전환되는 과정의 어느 단계에 금액이 쌓이는지 확인합니다.")

    st.markdown("""
    <div class="hyundai-note">
    <b>왜 이 두 계정을 보는가?</b><br><br>
    건설사업은 <b>공사진행 → 매출 인식 → 청구 → 현금 회수</b>의 과정을 거칩니다.<br>
    • <b>미청구공사</b>: 공사진행에 따라 수익은 인식됐지만 아직 청구 전 단계에 있는 계약자산<br>
    • <b>매출채권</b>: 청구가 이뤄진 뒤 아직 회수되지 않은 채권을 포함하는 계정<br><br>
    따라서 두 계정의 변화를 함께 보면 매출 인식 이후 <b>청구와 회수 단계에서 운전자본이 어떻게 변하는지</b> 확인할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 1. 회사 전체: 매출 인식 이후 잔액은 어떻게 변했나?")
    fig_wc = go.Figure()
    fig_wc.add_trace(go.Bar(x=working["시점"], y=working["미청구공사_조원"], name="미청구공사"))
    fig_wc.add_trace(go.Bar(x=working["시점"], y=working["매출채권_조원"], name="매출채권"))
    fig_wc.update_layout(
        barmode="group",
        title="연결 미청구공사·매출채권",
        yaxis_title="조원",
        legend_title_text=""
    )
    st.plotly_chart(fig_wc, use_container_width=True)

    latest = working.iloc[-1]
    prev = working.iloc[-2]
    col1, col2, col3 = st.columns(3)
    col1.metric("2026H1 미청구공사", f"{latest['미청구공사_조원']:.2f}조원",
                f"{latest['미청구공사_조원']-prev['미청구공사_조원']:+.2f}조")
    col2.metric("2026H1 매출채권", f"{latest['매출채권_조원']:.2f}조원",
                f"{latest['매출채권_조원']-prev['매출채권_조원']:+.2f}조")
    col3.metric("두 계정 합계", f"{latest['합계_조원']:.2f}조원",
                f"{latest['합계_조원']-prev['합계_조원']:+.2f}조")

    st.markdown("""
    <div class="hyundai-card">
    <b>1차 진단</b><br><br>
    2025년 말 대비 2026년 상반기 말 미청구공사는 약 <b>3.94조원 → 4.48조원</b>,
    매출채권은 <b>6.84조원 → 7.24조원</b>으로 모두 증가했습니다.
    즉 2026년 상반기에는 매출 인식 이후 청구·회수 과정에 묶여 있는 관련 잔액이 확대됐습니다.<br><br>
    다만 잔액 증가만으로 회수 악화나 부실을 의미한다고 단정할 수는 없으며,
    프로젝트 진행 규모와 계약별 청구조건을 함께 확인해야 합니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 2. +0.55조원의 미청구공사 증가: 어느 사업부문에서 나왔나?")
    drivers = unbilled_segment.sort_values("증감_조원")
    fig_driver = px.bar(
        drivers, x="증감_조원", y="구분", orientation="h", text="증감_조원",
        labels={"증감_조원":"2025말 → 2026H1말 증감(조원)", "구분":""},
        title="도급공사 보고부문별 단기미청구공사 증감"
    )
    fig_driver.update_traces(texttemplate="%{text:+.3f}조", textposition="outside")
    fig_driver.add_vline(x=0, line_width=1, line_dash="dash")
    st.plotly_chart(fig_driver, use_container_width=True)

    d1, d2 = st.columns(2)
    with d1:
        st.markdown("""
        <div class="hyundai-card">
        <b>증가 측</b><br><br>
        건축/주택은 약 <b>1.395조원 → 1.647조원(+0.253조원)</b>,
        토목은 <b>0.779조원 → 0.895조원(+0.117조원)</b>으로 증가했습니다.
        </div>
        """, unsafe_allow_html=True)
    with d2:
        st.markdown("""
        <div class="hyundai-card">
        <b>감소 측</b><br><br>
        플랜트/전력은 약 <b>0.532조원 → 0.459조원(-0.073조원)</b>으로 감소했습니다.
        따라서 모든 사업부문에서 미청구공사가 동시에 증가한 것은 아닙니다.
        </div>
        """, unsafe_allow_html=True)

    st.caption("부문별 수치는 건설계약 주석의 도급공사 단기미청구공사 기준입니다. 연결 재무상태표 미청구공사 총액과 표시 범위가 달라 합계가 정확히 일치하지 않을 수 있습니다.")

    st.markdown("#### 3. 미청구공사 증가는 원가 추정 변경과도 관련이 있나?")
    est_long = estimate_2026h1[["구분","당기손익영향_조원","미청구공사변동_조원"]].melt(
        id_vars="구분", var_name="영향", value_name="조원"
    )
    fig_est = px.bar(
        est_long, x="구분", y="조원", color="영향",
        barmode="group",
        title="2026H1 총계약수익·원가 추정 변경 영향",
        labels={"조원":"영향(조원)", "구분":""}
    )
    st.plotly_chart(fig_est, use_container_width=True)

    st.markdown("""
    <div class="hyundai-note">
    <b>범위를 넓히면 사업관리의 역할이 보입니다.</b><br><br>
    2026년 상반기 총계약수익·총계약원가 추정 변경은 당기손익에
    토목 <b>-0.071조원</b>, 건축/주택 <b>-0.044조원</b>, 플랜트/전력 <b>-0.233조원</b>의 영향을 미쳤습니다.<br><br>
    즉 장기 프로젝트에서는 이미 발생한 비용을 집계하는 것만으로 충분하지 않습니다.
    공사 진행 과정에서 <b>예상 총원가가 어떻게 바뀌는지 점검하고 이를 손익 전망과 예산에 반영</b>해야 합니다.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("2025년과 비교해서 원가 추정 영향 보기"):
        st.write("2025년에는 총계약수익·총계약원가 추정 변경이 당기손익에 합계 약 **-0.98조원**의 영향을 미쳤습니다.")
        show = estimate_2025.copy()
        show.columns = ["사업부문", "당기손익 영향(조원)", "미청구공사 변동(조원)", "공사손실충당부채(조원)"]
        st.dataframe(show, hide_index=True, use_container_width=True)
        st.write("특히 플랜트/전력의 당기손익 영향이 약 **-0.57조원**으로 가장 컸습니다. 프로젝트 사업관리에서는 원가 추정 변경의 규모와 원인을 사업부문·프로젝트별로 추적할 필요가 있습니다.")

    st.markdown("#### 4. 최종적으로 현금으로 이어졌나?")
    fig_cf = px.bar(
        cashflow, x="기간", y="영업활동현금흐름_조원",
        text="영업활동현금흐름_조원",
        labels={"영업활동현금흐름_조원":"영업활동현금흐름(조원)", "기간":""},
        title="연결 영업활동현금흐름"
    )
    fig_cf.update_traces(texttemplate="%{text:.2f}조", textposition="outside")
    st.plotly_chart(fig_cf, use_container_width=True)

    st.write(
        "2026년 상반기 영업활동현금흐름은 약 **-1.68조원**으로 전년 동기 약 **-1.89조원**보다 적자 폭이 축소됐지만 여전히 음수입니다. "
        "따라서 프로젝트의 성과를 매출과 이익에서 끝내지 않고 청구·회수 일정과 운전자본까지 연결해 관리할 필요가 있습니다."
    )

    st.markdown("""
    <div class="hyundai-card">
    <b>이 탭에서 얻는 최종 결론</b><br><br>
    ① 2026년 상반기 말에는 미청구공사와 매출채권이 모두 2025년 말보다 증가했습니다.<br>
    ② 도급공사 미청구공사를 사업부문별로 보면 <b>건축/주택과 토목이 증가한 반면 플랜트/전력은 감소</b>했습니다.<br>
    ③ 동시에 총계약수익·원가 추정 변경이 당기손익과 미청구공사에 영향을 주고 있어,
    장기 프로젝트에서는 <b>원가 추정의 변화까지 예산과 손익 전망에 반영</b>해야 합니다.<br>
    ④ 따라서 경영일반 담당자는 <b>수주 → 수행 → 매출 → 청구 → 회수</b>를 하나의 흐름으로 보고,
    프로젝트별 계획 대비 실적과 원가·회수 차이의 원인을 관리해야 합니다.
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 출처 / 유의사항
# ============================================================
st.divider()
with st.expander("데이터 출처 및 해석 유의사항"):
    st.markdown("""
    **출처**
    - 사용자가 제공한 현대건설 2023~2025 사업보고서 및 2026년 반기보고서
    - 연결 건설계약 주석의 수주잔고, 건설계약 수익, 계약자산, 총계약수익·총계약원가 추정 변경
    - 연결 재무상태표의 미청구공사·매출채권
    - 연결 현금흐름표의 영업활동현금흐름

    **유의사항**
    - 수주잔고는 향후 매출의 참고지표이며 실제 미래 매출액을 보장하지 않습니다.
    - 2026H1은 반기 시점 수치이므로 연간 수치와 단순 비교하지 않습니다.
    - 건설계약 주석의 '단기미청구공사'와 연결 재무상태표의 '미청구공사'는 표시 범위가 달라 합계가 일치하지 않을 수 있습니다.
    - 매출채권은 공사미수금만을 뜻하지 않으므로 '청구 후 미회수 공사대금'과 완전히 동일한 지표로 해석하지 않습니다.
    - 특정 잔액 증가만으로 부실·회수위험을 단정하지 않습니다.
    """)

st.caption("HYUNDAI E&C Project Management Insight · 생성형 AI를 활용한 개인 분석 프로젝트")
