
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import pickle  # 추가: 모델 로드를 위해 pickle import
from streamlit.components.v1 import html as st_html  # 추가: HTML/JS 임베딩용

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="2025 스마트폰 스펙 및 가격 분석 대시보드",
    page_icon="📱",
    layout="wide"
)

# 2. 데이터 불러오기
@st.cache_data
def load_data():
    # 앞 단계에서 저장한 전처리된 데이터를 불러옵니다.
    df = pd.read_csv("cleaned_mobiles_2025.csv")
    return df

df = load_data()

# 모델 로드 함수 정의
@st.cache_resource
def load_model():
    absolute_model_path = r"C:\Final_Project\phone_price_model.pkl"
    
    with open(absolute_model_path, "rb") as f:
        data = pickle.load(f)
    return data["model"], data["features"]

# 모델 로드 및 변수(model_loaded) 선언 예외 처리
try:
    ml_model, ml_features = load_model()
    model_loaded = True  # 성공 시 True 대입
except Exception as e:
    model_loaded = False # 실패 시 False 대입

# 3. 대시보드 제목
st.title("📱 2025 글로벌 스마트폰 사양 및 가격 분석 대시보드")
st.markdown("Kaggle의 최신 스마트폰 데이터를 활용하여 브랜드별 스펙 트렌드와 가격 요인을 분석합니다.")
st.write("---")

# 4. 사이드바 - 사용자 인터랙티브 필터 설정
st.sidebar.header("🔍 데이터 필터링 설정")

import io
import pandas as pd
import streamlit as st

# 1. 파일 읽기 및 Git 찌꺼기 정제 연산
file_path = "cleaned_mobiles_2025.csv"

with open(file_path, 'r', encoding='utf-8') as f:
    clean_lines = [
        line for line in f.readlines() 
        if not (line.startswith('<<<<<<<') or line.startswith('=======') or line.startswith('>>>>>>>'))
    ]

# 데이터프레임 생성
df = pd.read_csv(io.StringIO("".join(clean_lines)))

# 🌟 [핵심 보정] 컬럼명 양끝 공백 및 유니코드 깨짐 글자(\ufeff) 강제 제거
df.columns = df.columns.str.replace('\ufeff', '').str.strip()

# 중간에 중복 헤더나 Git 마크가 데이터 행으로 들어간 경우 필터링
if 'Company Name' in df.columns:
    df = df[df['Company Name'].str.contains('Company Name|HEAD|====|>>>>') == False]
    df['Company Name'] = df['Company Name'].str.strip()
else:
    # 혹시 컬럼명이 다르게 깨져 들어갔는지 디버깅하기 위해 현재 열 이름을 강제로 출력
    st.error(f"현재 데이터셋의 실제 컬럼명 목록입니다: {list(df.columns)}")

# 2. 문제의 49번째 줄: 안전하게 고쳐진 데이터로 유니크 브랜드 정렬 추출
all_companies = sorted(df['Company Name'].unique())

# --- 추가: 모든 브랜드 선택 체크박스 및 세션 상태 초기화/관리 ---
# 체크박스: 체크하면 모든 브랜드가 multiselect에 자동 선택됨
select_all = st.sidebar.checkbox("모든 브랜드 선택", value=False, key='select_all_brands')

# 초기값이 없으면 기존 기본값(원래 사용하던 일부 브랜드)을 설정
if 'selected_companies' not in st.session_state:
    st.session_state['selected_companies'] = ['Apple', 'Samsung', 'Xiaomi', 'Google']

# 체크박스가 켜져 있으면 모든 브랜드로 세션값 덮어쓰기
if st.session_state.get('select_all_brands', False):
    st.session_state['selected_companies'] = all_companies

# multiselect은 session_state의 'selected_companies'를 키로 사용하여 상태 유지 및 동기화
selected_companies = st.sidebar.multiselect(
    "분석할 브랜드를 선택하세요:",
    options=all_companies,
    key='selected_companies'
)

# (2) 가격대 슬라이더 (USD 기준)
df['Launched Price (USA)'] = pd.to_numeric(
    df['Launched Price (USA)'].astype(str).str.replace(r'[^0-9.]', '', regex=True), 
    errors='coerce'
)

# 소수점이 있을 수 있으므로 우선 float(실수)으로 최소/최대값을 구한 뒤 int(정수)로 변환합니다.
min_price = int(float(df['Launched Price (USA)'].dropna().min()))
max_price = int(float(df['Launched Price (USA)'].dropna().max()))
selected_price_range = st.sidebar.slider(
    "출시 가격 범위 ($)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)

# (3) 최소 RAM 용량 슬라이더
df['RAM'] = pd.to_numeric(
    df['RAM'].astype(str).str.replace(r'[^0-9.]', '', regex=True), 
    errors='coerce'
)

# 결측치를 제외한 순수 숫자 데이터셋에서 실수(float)로 최소/최대를 구한 뒤 정수(int)로 바꿉니다.
min_ram = int(float(df['RAM'].dropna().min()))
max_ram = int(float(df['RAM'].dropna().max()))
selected_ram = st.sidebar.slider(
    "최소 RAM 용량 (GB)",
    min_value=min_ram,
    max_value=max_ram,
    value=min_ram
)

# 필터링 적용 데이터 생성
filtered_df = df[
    (df['Company Name'].isin(selected_companies)) &
    (df['Launched Price (USA)'] >= selected_price_range[0]) &
    (df['Launched Price (USA)'] <= selected_price_range[1]) &
    (df['RAM'] >= selected_ram)
]

# 5. 메인 화면 구성 - 탭(Tab) 구조로 분리하여 가독성 높이기
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 브랜드별 시장 분석", 
    "📈 스펙 vs 가격 상관관계", 
    "💡 맞춤형 스마트폰 추천", 
    "🤖 AI 가격 예측기"
])

# --- 탭 1: 브랜드별 시장 분석 ---
with tab1:
    st.subheader("제조사별 평균 스펙 및 가격 비교")
    
    # 1. 안전하게 독립된 데이터프레임 복사본 생성 (SettingWithCopy 방지)
    filtered_df = filtered_df.copy()
    
    # 2. 계산에 필요한 3가지 핵심 컬럼을 수치형으로 전처리
    numeric_cols = ['Launched Price (USA)', 'Battery Capacity', 'Mobile Weight']
    
    for col in numeric_cols:
        if col in filtered_df.columns:
            # 문자열 찌꺼기를 날리고, 숫자가 아닌 문자는 NaN으로 강제 전환
            filtered_df[col] = pd.to_numeric(
                filtered_df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True), 
                errors='coerce'
            )
            
    # 3. 평균 집계 연산 시 에러를 방지하기 위해 결측치(NaN) 행 제거
    filtered_df = filtered_df.dropna(subset=numeric_cols)
    
    # 4. 모든 데이터가 정제되었으므로 안전하게 그룹화 평균 계산 🌟
    brand_summary = filtered_df.groupby('Company Name')[numeric_cols].mean().reset_index()
    
    # 5. 스트림릿 레이아웃 배치 및 Plotly 차트 출력
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### **💵 브랜드별 평균 출시 가격 ($)**")
        fig_price = px.bar(brand_summary, x='Company Name', y='Launched Price (USA)', 
                           labels={'Launched Price (USA)': '평균 가격 ($)', 'Company Name': '제조사'},
                           color='Company Name')
        st.plotly_chart(fig_price, use_container_width=True)
        
    with col2:
        st.markdown("#### **🔋 브랜드별 평균 배터리 용량 (mAh)**")
        fig_battery = px.bar(brand_summary, x='Company Name', y='Battery Capacity', 
                             labels={'Battery Capacity': '평균 배터리 (mAh)', 'Company Name': '제조사'},
                             color='Company Name')
        st.plotly_chart(fig_battery, use_container_width=True)

# --- 탭 2: 스펙 vs 가격 상관관계 ---
with tab2:
    st.subheader("스마트폰 성능 사양이 가격에 미치는 영향")
    st.markdown("> 화면 크기가 커지거나 무게가 무거워질 때 가격은 어떻게 변할까요? 산점도로 확인해 보세요.")
    
    # 산점도 그리기
    # filtered_df의 Screen Size 결측치로 인해 Plotly의 size 속성에 NaN이 전달되면 에러가 발생합니다.
    # 따라서 시각화 전용 복사본을 만들고 Screen Size의 NaN을 중앙값(또는 기본값)으로 채웁니다.
    df_plot = filtered_df.copy()
    if 'Screen Size' in df_plot.columns:
        df_plot['Screen Size'] = pd.to_numeric(
        df_plot['Screen Size'].astype(str).str.replace(r'[^0-9.]', '', regex=True), 
        errors='coerce'
        )
        median_screen = df_plot['Screen Size'].median()
        # median이 NaN이면 안전한 기본값 사용
        if pd.isna(median_screen):
            median_screen = 6.5
        df_plot['Screen Size (filled)'] = df_plot['Screen Size'].fillna(median_screen)
    else:
        # 컬럼 자체가 없을 경우 기본값 컬럼 생성
        df_plot['Screen Size (filled)'] = 6.5

    fig_scatter = px.scatter(
        df_plot, 
        x="Mobile Weight", 
        y="Launched Price (USA)", 
        color="Company Name",
        hover_name="Model Name",
        size="Screen Size (filled)",
        labels={'Mobile Weight': '무게 (g)', 'Launched Price (USA)': '가격 ($)'},
        title="스마트폰 무게 및 화면 크기 대비 출시 가격 산점도"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- 탭 3: 맞춤형 스마트폰 추천 시스템 ---
with tab3:
    st.subheader("🎯 나에게 맞는 스마트폰 찾기")
    st.markdown("왼쪽 사이드바에서 설정한 조건(브랜드, 가격, RAM)에 맞는 최신 스마트폰 리스트입니다.")
    
    # 결과 테이블 보여주기
    display_cols = ['Company Name', 'Model Name', 'RAM', 'Battery Capacity', 'Screen Size', 'Launched Price (USA)', 'Launched Year']
    result_df = filtered_df[display_cols].sort_values(by='Launched Price (USA)')
    
    st.dataframe(result_df, use_container_width=True)
    st.caption(f"조건에 맞는 스마트폰이 총 {len(result_df)}개 검색되었습니다.")

# --- 탭 4: 🤖 AI 가격 예측기 (신규 추가 파트) ---
with tab4:
    st.subheader("🔮 가상 스마트폰 스펙 기반 출시 가격 예측")
    st.markdown("원하는 성능 사양을 입력하면, 학습된 **Random Forest** 모델이 실시간으로 예상 출시 가격을 추론합니다.")
    
    if not model_loaded:
        st.error("🚨 머신러닝 모델 파일(`phone_price_model.pkl`)을 찾을 수 없습니다. 터미널에서 `python train_model.py`를 먼저 실행해 주세요.")
    else:
        st.write("---")
        # 수치 입력을 받기 위한 UI 레이아웃 분할
        col_in1, col_in2, col_in3 = st.columns(3)
        
        with col_in1:
            input_ram = st.number_input("RAM 용량 (GB)", min_value=2, max_value=24, value=8, step=2)
            input_battery = st.number_input("배터리 용량 (mAh)", min_value=2000, max_value=7000, value=5000, step=500)
            
        with col_in2:
            input_weight = st.number_input("기기 무게 (g)", min_value=100, max_value=300, value=190, step=10)
            input_screen = st.number_input("화면 크기 (Inches)", min_value=4.0, max_value=8.0, value=6.5, step=0.1)
            
        with col_in3:
            input_front = st.number_input("전면 카메라 (MP)", min_value=5, max_value=60, value=12, step=4)
            input_back = st.number_input("후면 메인 카메라 (MP)", min_value=12, max_value=200, value=50, step=12)
            
        st.write("---")
        
        # 사용자가 입력한 값으로 데이터프레임 데이터 구성
        input_data = pd.DataFrame([{
            'RAM': input_ram,
            'Battery Capacity': input_battery,
            'Mobile Weight': input_weight,
            'Screen Size': input_screen,
            'Front Camera': input_front,
            'Back Camera': input_back
        }])
        
        # --- 추가: 실시간 Value_Score 계산 및 컬럼 정렬 ---
        # 공식: (input_ram * 1000 + input_battery) / 583.0
        input_data['Value_Score'] = (input_ram * 1000 + input_battery) / 583.0

        # 모델이 기대하는 features 순서로 정렬하려 시도 (ml_features는 load_model로부터 로드됨)
        try:
            input_data = input_data[ml_features]
        except Exception:
            # ml_features가 없거나 컬럼 불일치 시 원래 데이터프레임 유지
            pass
        
        # 버튼을 누르면 추론(Prediction) 수행
        if st.button("🚀 예상 출시 가격 추론하기", type="primary"):
            # 모델 예측값 계산
            predicted_price = ml_model.predict(input_data)[0]
            
            # 결과 시각적 연출
            st.success("### 📊 AI 추론 결과")
            
            # 메트릭 컴포넌트로 가격 강조 표시
            st.metric(
                label="💡 예측된 스마트폰 출시 가격", 
                value=f"${predicted_price:,.2f}",
                delta=f"원화 약 {int(predicted_price * 1350):,} 원" # 환율 1350원 기준 가심사
            )
            
            # 기존 풍선 효과는 주석 처리
            # st.balloons()

            # --- 추가: Money Rain 애니메이션 임베딩 ---
            money_html = """
            <style>
            .money-rain {
              pointer-events: none;
              position: fixed;
              top: 0;
              left: 0;
              width: 100%;
              height: 100%;
              overflow: hidden;
              z-index: 9999999;
            }
            .money {
              position: absolute;
              top: -10%;
              font-size: 24px;
              opacity: 0.9;
              animation-name: fall;
              animation-timing-function: linear;
              animation-iteration-count: 1;
            }
            @keyframes fall {
              0% { transform: translateY(-10vh) rotate(0deg); opacity: 1; }
              100% { transform: translateY(110vh) rotate(360deg); opacity: 0.0; }
            }
            </style>
            <div class="money-rain" id="money-rain"></div>
            <script>
            (function() {
              const icons = ['💵','💸','💰'];
              const container = document.getElementById('money-rain');
              const count = 40;
              for (let i=0;i<count;i++){
                const span = document.createElement('div');
                span.className = 'money';
                span.style.left = Math.random()*100 + '%';
                span.style.fontSize = (12 + Math.random()*28) + 'px';
                span.style.animationDuration = (3 + Math.random()*5) + 's';
                span.style.animationDelay = (Math.random()*2) + 's';
                span.style.opacity = 0.8 + Math.random()*0.2;
                span.textContent = icons[Math.floor(Math.random()*icons.length)];
                container.appendChild(span);
              }
              // 일정 시간 후 제거
              setTimeout(()=>{ container.remove(); }, 7000);
            })();
            </script>
            """
            # 높이는 임베딩 내부의 fixed overlay가 전체 화면을 덮도록 충분히 크게 설정
            st_html(money_html, height=600, scrolling=False)
