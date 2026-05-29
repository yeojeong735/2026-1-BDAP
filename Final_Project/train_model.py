import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import codecs


# 1. 데이터 로드
file_path = r"C:\Users\6-112\Desktop\빅데이터분석프로그래밍\20241513_장여정\one1\Final_Project\cleaned_mobiles_2025.csv"


print("--- 데이터 안전하게 읽어오기 시도 ---")

# 특수문자 충돌을 방지하기 위해 codecs를 사용해 'latin-1' 혹은 에러 무시('ignore') 옵션으로 오픈
with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    df = pd.read_csv(f)

# 2. 특성 추출 (Feature Selection) 및 결측치 제거
# 가격 예측에 유의미한 수치형 변수들을 선택합니다.
features = ['RAM', 'Battery Capacity', 'Mobile Weight', 'Screen Size', 'Front Camera', 'Back Camera']
target = 'Launched Price (USA)'

# 학습에 사용할 필드만 추출하고 혹시 모를 빈 값(NaN) 제거
ml_df = df[features + [target]].dropna()

X = ml_df[features]
y = ml_df[target]

# 3. 데이터 분할 (학습용 80%, 검증용 20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. 머신러닝 모델 생성 및 학습 (Random Forest Regressor)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 5. 모델 평가 (보고서 작성용 데이터)
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("=== 🎉 모델 학습 완료 ===")
print(f"훈련 데이터 개수: {len(X_train)}개")
print(f"테스트 데이터 개수: {len(X_test)}개")
print(f"평균 절대 오차 (MAE): ${mae:.2f}")
print(f"모델 설명력 (R2 Score): {r2:.2f}")

# 6. 학습된 모델과 특성 이름을 파일로 저장 (Streamlit에서 불러다 쓸 예정)
with open("phone_price_model.pkl", "wb") as f:
    pickle.dump({"model": model, "features": features}, f)

print("\n--- 'phone_price_model.pkl' 파일로 모델이 성공적으로 저장되었습니다! ---")