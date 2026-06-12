import io
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

def evaluate_smartphone_model():
    # 1. VS Code 경로에 맞게 데이터 읽기 및 Git 충돌 찌꺼기 완벽 차단
    file_path = "cleaned_mobiles_2025.csv"  # 데이터 파일이 같은 폴더에 있으면 이름만 적으면 됩니다.
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ '{file_path}' 파일을 찾을 수 없습니다. 경로를 다시 확인해 주세요.")
        return

    # Git 충돌 흔적 기호 필터링
    clean_lines = [
        line for line in all_lines 
        if not (line.startswith('<<<<<<<') or line.startswith('=======') or line.startswith('>>>>>>>'))
    ]

    # DataFrame 변환 및 컬럼 전처리
    df = pd.read_csv(io.StringIO("".join(clean_lines)))
    df.columns = df.columns.str.replace('\ufeff', '').str.strip()
    df = df[df['Company Name'].str.contains('Company Name|HEAD|====|>>>>') == False]

    # 2. 수치형 데이터 변환 및 가성비(Value_Score) 공식 연산
    features_list = ['Launched Price (USA)', 'RAM', 'Battery Capacity', 'Mobile Weight', 'Screen Size', 'Front Camera', 'Back Camera']
    for col in features_list:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True), errors='coerce')
            
    df['Value_Score'] = ((df['RAM'] * 1000) + df['Battery Capacity']) / (df['Launched Price (USA)'] + 1)
    
    # 필수 변수 결측치 행 제거
    df = df.dropna(subset=['Launched Price (USA)', 'RAM', 'Battery Capacity'])

    # 3. 독립변수(X)와 종속변수(y, 타겟) 분리
    X = df[['RAM', 'Battery Capacity', 'Mobile Weight', 'Screen Size', 'Front Camera', 'Back Camera', 'Value_Score']]
    y = df['Launched Price (USA)']

    # 나머지 누락된 값들은 평균값으로 안전하게 채움 (모델 학습 에러 방지)
    X = X.fillna(X.mean())

    # 4. 학습 데이터와 검증 데이터 분리 (8:2 비율)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 5. 랜덤 포레스트 회귀 모델 생성 및 학습
    print("🤖 랜덤 포레스트 회귀 모델 학습 진행 중...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 6. 검증 데이터로 예측 진행
    y_pred = model.predict(X_test)

    # 7. 🔥 VS Code 터미널에 모델 성능 지표 출력 🔥
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\n" + "="*50)
    print("       📊 RANDOM FOREST MODEL PERFORMANCE INDICATORS")
    print("="*50)
    print(f" ▶ 평균 절대 오차 (MAE)    : ${mae:.2f}")
    print(f" ▶ 모델 설명력 (R² Score)  : {r2:.4f} ({r2*100:.2f}%)")
    print("="*50)
    print("🎉 수치 계산이 완료되었습니다! 위 지표를 보고서에 활용하세요.\n")

if __name__ == "__main__":
    evaluate_smartphone_model()
