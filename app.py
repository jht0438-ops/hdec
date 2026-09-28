import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="현대건설 프로젝트 사업관리 분석", page_icon="🏗️", layout="wide")
st.title("현대건설 프로젝트 사업관리 분석")
st.caption("생성형 AI 활용 구현 · 현대건설 공시자료 기반")

st.markdown("""
<style>
.block-container {padding-top:1.5rem; padding-bottom:3rem;}
div[data-testid="stMetric"] {border:1px solid #e6e6e6; padding:16px; border-radius:14px;}
.note {border-left:4px solid #2563eb;background:#f6f8ff;padding:16px 18px;border-radius:8px;margin:10px 0 20px;}
.card {border:1px solid #e6e6e6;border-radius:14px;padding:18px;background:white;margin:8px 0 18px;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA — 사용자 제공 현대건설 공시자료에서 확인한 값
# ============================================================

# 연결 재무상태표
total_unbilled = {2024: 4.684982, 2025: 3.937364, "2026H1": 4.482329}
receivables = {2024: 5.319211, 2025: 6.842276, "2026H1": 7.236172}

# 건설계약 수주잔고
backlog = {2024: 95.822036, 2025: 95.038562}

# 건설계약 매출
contract_sales = {2024: 31.248481, 2025: 31.062912, "2025H1": 14.476829, "2026H1": 13.123568}

# 도급공사 보고부문별 단기미청구공사
seg_2025 = {"토목":0.7786, "건축/주택":1.3945, "플랜트/전력":0.5317}
seg_2026 = {"토목":0.8946, "건축/주택":1.6470, "플랜트/전력":0.4587}

# 총계약수익·총계약원가 추정 변경 — 2025
est_2025 = pd.DataFrame({
    "부문":["토목","건축/주택","플랜트/전력"],
    "당기손익 영향(억원)":[-1073.68,-3005.59,-5741.07],
    "미청구공사 변동(억원)":[-1478.68,-5591.36,-5167.85],
    "공사손실충당부채(억원)":[3.82,89.39,606.19]
})

# 2026H1
est_2026 = pd.DataFrame({
    "부문":["토목","건축/주택","플랜트/전력"],
    "당기손익 영향(억원)":[-713.62,-437.65,-2331.35],
    "미청구공사 변동(억원)":[-1191.70,-799.68,-1529.22],
    "공사손실충당부채(억원)":[14.74,138.29,291.10]
})

cashflow = pd.DataFrame({
    "기간":["2025H1","2026H1"],
    "영업활동현금흐름(조원)":[-1.889152,-1.677087]
})

# ============================================================
# 탭 — 코오롱 프로그램과 같은 질문형 구조
# ============================================================
tabs = st.tabs([
    "1. 수주잔고 → 매출",
    "2. 프로젝트별 미청구공사 증감",
    "3. 전체 건설계약으로 넓혀 보면?",
    "4. 전체 미청구공사는 왜 변했나?",
    "5. 계약금액·원가추정 변경",
    "6. 현금회수",
    "최종결론"
])

# ============================================================
# 1. 수주잔고 → 매출
# ============================================================
with tabs[0]:
    st.header("1. 수주잔고 → 매출: 확보한 프로젝트가 실제 사업성과로 전환되고 있나?")
    st.markdown("""<div class="note"><b>왜 보는가?</b><br>
    수주잔고는 앞으로 수행할 프로젝트 규모를 보여줍니다. 그러나 수주가 곧 매출이나 현금은 아닙니다.
    수주잔고가 실제 매출로 전환되는 과정을 함께 봐야 프로젝트 사업관리의 의미가 드러납니다.</div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    c1.metric("2024말 수주잔고","95.82조원")
    c2.metric("2025말 수주잔고","95.04조원","-0.78조원")
    c3.metric("2025 건설계약 매출","31.06조원")

    df = pd.DataFrame({"연도":["2024","2025"],"수주잔고":[backlog[2024],backlog[2025]]})
    fig = px.bar(df,x="연도",y="수주잔고",text="수주잔고",title="건설계약 수주잔고")
    fig.update_traces(texttemplate="%{text:.2f}조",textposition="outside")
    st.plotly_chart(fig,use_container_width=True)

    st.subheader("수주잔고를 연간 매출 규모와 비교하면?")
    c1,c2 = st.columns(2)
    c1.metric("2024 수주잔고 / 건설계약 매출",f"{backlog[2024]/contract_sales[2024]:.1f}배")
    c2.metric("2025 수주잔고 / 건설계약 매출",f"{backlog[2025]/contract_sales[2025]:.1f}배")
    st.write("수주잔고는 약 3년치 건설계약 매출 규모에 해당합니다. 다만 이를 '3년 뒤 모두 매출화된다'고 해석해서는 안 되며 프로젝트별 공기·진행률·계약변경을 함께 봐야 합니다.")

# ============================================================
# 2. 프로젝트별 미청구공사 증감
# ============================================================
with tabs[1]:
    st.header("2. 미청구공사 증감: 어느 사업부문에서 나왔나?")
    st.markdown("""<div class="note"><b>코오롱 프로그램과 동일한 질문</b><br>
    회사 전체 미청구공사 변화만 보지 않고, 먼저 사업부문별 증감을 분해합니다.
    이후 개별 프로젝트 데이터가 공시된 범위에서는 프로젝트별 원인을 추적하는 방식입니다.</div>""", unsafe_allow_html=True)

    rows=[]
    for k in seg_2025:
        rows.append([k,seg_2025[k],seg_2026[k],seg_2026[k]-seg_2025[k]])
    seg=pd.DataFrame(rows,columns=["부문","2025말","2026H1말","증감"])
    fig=px.bar(seg.sort_values("증감"),x="증감",y="부문",orientation="h",text="증감",
               title="도급공사 보고부문별 단기미청구공사 증감",
               labels={"증감":"2025말 → 2026H1말 증감(조원)","부문":""})
    fig.update_traces(texttemplate="%{text:+.3f}조",textposition="outside")
    fig.add_vline(x=0,line_dash="dash")
    st.plotly_chart(fig,use_container_width=True)

    a,b=st.columns(2)
    with a:
        st.markdown("""<div class="card"><b>증가 측</b><br><br>
        건축/주택 약 1.395조원 → 1.647조원(<b>+0.253조원</b>)<br>
        토목 약 0.779조원 → 0.895조원(<b>+0.116조원</b>)</div>""",unsafe_allow_html=True)
    with b:
        st.markdown("""<div class="card"><b>감소 측</b><br><br>
        플랜트/전력 약 0.532조원 → 0.459조원(<b>-0.073조원</b>)<br><br>
        즉 모든 사업부문에서 미청구공사가 동시에 증가한 것은 아닙니다.</div>""",unsafe_allow_html=True)

    st.warning("현재 확보한 2026H1 공시 추출값만으로는 코오롱 프로그램처럼 '개별 프로젝트별 2025말→2026H1 미청구공사 증감 TOP10'을 정확하게 만들 수 없어 임의 수치를 넣지 않았습니다. 사업보고서·반기보고서의 동일 프로젝트 표가 확보되면 이 위치에 그대로 추가할 수 있습니다.")

# ============================================================
# 3. 전체 건설계약으로 넓혀 보면?
# ============================================================
with tabs[2]:
    st.header("3. 회사 전체 건설계약으로 넓혀 보면?")
    c1,c2,c3 = st.columns(3)
    c1.metric("2024 전체 미청구공사",f"{total_unbilled[2024]*10000:,.0f}억원")
    c2.metric("2025 전체 미청구공사",f"{total_unbilled[2025]*10000:,.0f}억원",
              f"{(total_unbilled[2025]-total_unbilled[2024])*10000:,.0f}억원")
    c3.metric("2026H1 전체 미청구공사",f"{total_unbilled['2026H1']*10000:,.0f}억원",
              f"{(total_unbilled['2026H1']-total_unbilled[2025])*10000:+,.0f}억원")

    comp = pd.DataFrame({
        "부문":["토목","건축/주택","플랜트/전력"],
        "2025말":[seg_2025[x]*10000 for x in ["토목","건축/주택","플랜트/전력"]],
        "2026H1말":[seg_2026[x]*10000 for x in ["토목","건축/주택","플랜트/전력"]]
    })
    long=comp.melt("부문",var_name="시점",value_name="억원")
    fig=px.bar(long,x="부문",y="억원",color="시점",barmode="group",
               title="전체 진행 중 도급공사: 부문별 단기미청구공사")
    st.plotly_chart(fig,use_container_width=True)

    st.write("2025년 말 전체 미청구공사는 2024년 말보다 감소했지만, 2026년 상반기에는 다시 증가했습니다. 사업부문별로 보면 건축/주택과 토목 증가가 플랜트/전력 감소를 상쇄했습니다.")
    st.caption("부문별 그래프는 건설계약 주석의 도급공사 단기미청구공사 기준이며, 연결 재무상태표 전체 미청구공사와 표시 범위가 달라 합계는 일치하지 않을 수 있습니다.")

# ============================================================
# 4. 전체 미청구공사는 왜 변했나?
# ============================================================
with tabs[3]:
    st.header("4. 전체 미청구공사는 왜 변했나?")
    diff = pd.DataFrame({
        "부문":["건축/주택","토목","플랜트/전력"],
        "증감(억원)":[
            (seg_2026["건축/주택"]-seg_2025["건축/주택"])*10000,
            (seg_2026["토목"]-seg_2025["토목"])*10000,
            (seg_2026["플랜트/전력"]-seg_2025["플랜트/전력"])*10000
        ]
    }).sort_values("증감(억원)")
    fig=px.bar(diff,x="증감(억원)",y="부문",orientation="h",text="증감(억원)",
               title="부문별 단기미청구공사 증감")
    fig.update_traces(texttemplate="%{text:+.0f}억원",textposition="outside")
    fig.add_vline(x=0,line_dash="dash")
    st.plotly_chart(fig,use_container_width=True)

    st.write("건축/주택과 토목에서 미청구공사가 증가한 반면 플랜트/전력에서는 감소했습니다. 따라서 회사 전체 미청구공사 증가는 특정 사업부문 하나만의 변화가 아니라 부문별 증감이 합쳐진 결과로 봐야 합니다.")

    with st.expander("계약금액·총원가 추정 변경도 영향을 줬나?"):
        st.write("그렇습니다. 장기 건설계약에서는 총계약수익과 총계약원가 추정 변경이 손익뿐 아니라 미청구공사에도 영향을 줄 수 있습니다.")
        st.dataframe(est_2026,hide_index=True,use_container_width=True)

# ============================================================
# 5. 계약금액·원가추정 변경
# ============================================================
with tabs[4]:
    st.header("5. 계약금액·원가추정 변경: 사업관리에서 무엇을 봐야 하나?")
    st.write("코오롱 프로그램의 '계약금액·총원가 추정 변경' 진단과 동일하게, 현대건설도 원가 추정 변경이 당기손익에 미친 영향을 부문별로 확인합니다.")

    fig=px.bar(est_2026.sort_values("당기손익 영향(억원)"),
               x="당기손익 영향(억원)",y="부문",orientation="h",
               text="당기손익 영향(억원)",title="2026H1 총계약수익·원가 추정 변경의 당기손익 영향")
    fig.update_traces(texttemplate="%{text:+,.0f}억원",textposition="outside")
    fig.add_vline(x=0,line_dash="dash")
    st.plotly_chart(fig,use_container_width=True)

    a,b,c=st.columns(3)
    a.metric("토목 당기손익 영향","-714억원")
    b.metric("건축/주택 당기손익 영향","-438억원")
    c.metric("플랜트/전력 당기손익 영향","-2,331억원")

    st.markdown("""<div class="card"><b>해석</b><br><br>
    2026년 상반기에는 총계약수익·총계약원가 추정 변경이 세 부문 모두 당기손익에 부정적 영향을 미쳤고,
    그 규모는 플랜트/전력이 가장 컸습니다. 따라서 프로젝트 사업관리에서는 이미 발생한 원가만 집계하는 것이 아니라
    <b>예상 총원가를 지속적으로 갱신하고 계획 대비 차이를 조기에 확인</b>해야 합니다.</div>""",unsafe_allow_html=True)

    st.subheader("2025년과 비교")
    st.dataframe(est_2025,hide_index=True,use_container_width=True)
    st.write("2025년에도 추정 변경의 당기손익 영향은 합계 약 -0.98조원이었습니다. 원가 추정 변화가 손익에 미치는 영향이 큰 만큼 예산관리와 프로젝트 관리가 직접 연결됩니다.")

# ============================================================
# 6. 현금회수
# ============================================================
with tabs[5]:
    st.header("6. 매출로 인식한 성과는 실제 현금으로 회수됐나?")
    c1,c2,c3 = st.columns(3)
    c1.metric("2025말 미청구공사","3.94조원")
    c2.metric("2026H1말 미청구공사","4.48조원","+0.55조원")
    c3.metric("2026H1말 매출채권","7.24조원","+0.39조원")

    wc=pd.DataFrame({
        "시점":["2024말","2025말","2026H1말"],
        "미청구공사":[total_unbilled[2024],total_unbilled[2025],total_unbilled["2026H1"]],
        "매출채권":[receivables[2024],receivables[2025],receivables["2026H1"]]
    }).melt("시점",var_name="항목",value_name="조원")
    fig=px.bar(wc,x="시점",y="조원",color="항목",barmode="group",
               title="매출 인식 이후 청구·회수 관련 잔액")
    st.plotly_chart(fig,use_container_width=True)

    st.subheader("영업활동현금흐름")
    fig=px.bar(cashflow,x="기간",y="영업활동현금흐름(조원)",text="영업활동현금흐름(조원)")
    fig.update_traces(texttemplate="%{text:.2f}조",textposition="outside")
    st.plotly_chart(fig,use_container_width=True)

    st.write("2026년 상반기 영업활동현금흐름은 약 -1.68조원으로 전년 동기 -1.89조원보다 음수 폭은 줄었지만 여전히 마이너스입니다. 미청구공사·매출채권 증가와 함께 프로젝트별 청구 및 회수 일정을 지속적으로 관리할 필요가 있습니다.")
    st.caption("미청구공사나 매출채권 증가만으로 영업현금흐름 악화의 전체 원인을 단정하지 않습니다.")

# ============================================================
# 최종 결론
# ============================================================
with tabs[6]:
    st.header("최종결론: 현대건설 경영일반 직무에서 무엇을 관리해야 하나?")
    st.markdown("""<div class="note">
    <b>수주 → 수행 → 매출 → 청구 → 회수</b>를 하나의 프로젝트 흐름으로 관리해야 합니다.
    </div>""",unsafe_allow_html=True)

    st.markdown("""
    ### ① 프로젝트 사업관리
    약 95조원의 수주잔고를 단순한 미래 매출로 보지 않고 프로젝트별 공정·진행률·계약조건을 관리합니다.

    ### ② 예산관리
    계획원가와 실제원가를 비교하고 총계약원가 추정 변경을 반영해 프로젝트 종료 시점의 예상손익을 지속적으로 갱신합니다.

    ### ③ 회계
    공사진행에 따라 인식된 매출이 미청구공사로 얼마나 남아 있는지, 어느 사업부문에서 변화가 발생했는지 분석합니다.

    ### ④ 재무
    청구 이후 매출채권이 실제 현금으로 회수되는지 확인하고 프로젝트별 청구·회수 일정을 관리합니다.
    """)

    st.success("프로그램의 핵심: 숫자를 각각 보는 것이 아니라 '왜 수주잔고가 매출로 전환됐는지, 왜 미청구공사가 변했는지, 왜 원가 추정이 손익을 바꿨는지'를 프로젝트 단위로 추적하는 것입니다.")

st.divider()
st.caption("출처: 사용자가 제공한 현대건설 2023~2025 사업보고서 및 2026년 반기보고서. 공시에서 확인되지 않은 프로젝트별 수치는 임의 추정하지 않았습니다.")
