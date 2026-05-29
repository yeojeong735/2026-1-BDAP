import streamlit as st
import pandas as pd
import plotly.express as px
import os

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
    absolute_model_path = r"C:\Users\6-112\Desktop\빅데이터분석프로그래밍\20241513_장여정\one1\Final_Project\phone_price_model.pkl"
    
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

# (1) 브랜드 멀티 선택 박스
all_companies = sorted(df['Company Name'].unique())
selected_companies = st.sidebar.multiselect(
    "분석할 브랜드를 선택하세요:",
    options=all_companies,
    default=['Apple', 'Samsung', 'Xiaomi', 'Google']  # 기본 선택값
)

# (2) 가격대 슬라이더 (USD 기준)
min_price = int(df['Launched Price (USA)'].min())
max_price = int(df['Launched Price (USA)'].max())
selected_price_range = st.sidebar.slider(
    "출시 가격 범위 ($)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)

# (3) 최소 RAM 용량 슬라이더
min_ram = int(df['RAM'].min())
max_ram = int(df['RAM'].max())
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
    
    # 선택된 브랜드의 평균값 계산
    brand_summary = filtered_df.groupby('Company Name')[['Launched Price (USA)', 'Battery Capacity', 'Mobile Weight']].mean().reset_index()
    
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
    fig_scatter = px.scatter(
        filtered_df, 
        x="Mobile Weight", 
        y="Launched Price (USA)", 
        color="Company Name",
        hover_name="Model Name",
        size="Screen Size",
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
            
            st.balloons() # 축하 효과 애니메이션