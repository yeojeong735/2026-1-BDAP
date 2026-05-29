import pandas as pd
import numpy as np
import codecs

# 1. 파일 경로 지정
file_path = r"C:\Users\6-112\Desktop\빅데이터분석프로그래밍\20241513_장여정\one1\Final_Project\Mobiles_Dataset(2025).csv"

print("--- 데이터 안전하게 읽어오기 시도 ---")

# 특수문자 충돌을 방지하기 위해 codecs를 사용해 'latin-1' 혹은 에러 무시('ignore') 옵션으로 오픈
with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    df = pd.read_csv(f)

print("--- 전처리 시작 ---")

# 2. 정규표현식을 활용한 문자열 제거 및 숫자 변환 함수
def clean_numeric(column, unit_regex):
    # 단위 제거, 콤마 제거, 공백 제거 후 숫자로 변환 (변환 실패 시 NaN 처리)
    cleaned = df[column].astype(str).str.replace(unit_regex, '', regex=True)
    cleaned = cleaned.str.replace(',', '', regex=False).str.strip()
    return pd.to_numeric(cleaned, errors='coerce')

# [무게] '174g' -> 174
df['Mobile Weight'] = clean_numeric('Mobile Weight', r'g')

# [RAM] '6GB' -> 6
df['RAM'] = clean_numeric('RAM', r'GB')

# [배터리] '5000 mAh' -> 5000
df['Battery Capacity'] = clean_numeric('Battery Capacity', r'(mAh|MAh|mah|\s)')

# [화면 크기] '6.1 inches' -> 6.1
df['Screen Size'] = clean_numeric('Screen Size', r'(inches|Inches|inch|\s)')

# [가격 - USA] 'USD 799' -> 799
df['Launched Price (USA)'] = clean_numeric('Launched Price (USA)', r'USD\s?')

# [가격 - China] 'CNY 5,799' -> 5799
df['Launched Price (China)'] = clean_numeric('Launched Price (China)', r'CNY\s?')

# 3. 카메라 데이터 정제 (숫자만 추출)
df['Front Camera'] = clean_numeric('Front Camera', r'(MP|Mp|mp|\s)')
df['Back Camera'] = clean_numeric('Back Camera', r'(MP|Mp|mp|\s)')

# 이상치 제거
df_clean = df[df['Launched Price (USA)'] <= 3000].copy()

print(f"이상치 제거 전 데이터 수: {len(df)}개")
print(f"이상치 제거 후 데이터 수: {len(df_clean)}개")
print(f"제거된 이상치 데이터 수: {len(df) - len(df_clean)}개")

# 4. 전처리 결과 확인
print("\n=== 전처리 후 데이터 타입 정보 ===")
print(df_clean[['Mobile Weight', 'RAM', 'Battery Capacity', 'Screen Size', 'Launched Price (USA)', 'Front Camera']].info())

print("\n=== 전처리 후 데이터 샘플 ===")
print(df_clean[['Company Name', 'Model Name', 'RAM', 'Battery Capacity', 'Launched Price (USA)']].head(3))

print(len(df_clean))
# 5. 전처리된 데이터를 새로운 파일로 저장 (Streamlit에서 안전하게 불러올 수 있도록 utf-8-sig 지정)
df_clean.to_csv("cleaned_mobiles_2025.csv", index=False, encoding='utf-8-sig')
print("\n--- 전처리 완료! 'cleaned_mobiles_2025.csv'로 저장되었습니다. ---")