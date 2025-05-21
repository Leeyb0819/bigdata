import pandas as pd

df = pd.read_excel("서울대기오염_2019.xlsx")

# 1. 날짜 타입 변환
df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

# 2. 컬럼 이름 정리 (줄바꿈 제거 + 이름 정돈)
df.columns = df.columns.str.replace("\n", " ").str.strip()
df.rename(columns={
    "미세먼지": "PM10",
    "초미세먼지": "PM2.5",
    "이산화질소 NO2 (ppm)": "NO2",
    "일산화탄소 CO (ppm)": "CO",
    "아황산가스 SO2(ppm)": "SO2"
}, inplace=True)

# 3. 이상행 제거 (날짜가 '전체'이거나, 측정소명이 '평균'인 행 제거)
df = df[(df["날짜"] != "전체") & (df["측정소명"] != "평균")]

# 4. 결측치 처리 (선택적으로 평균값으로 채움)
df["PM10"] = df["PM10"].fillna(df["PM10"].mean())
df["PM2.5"] = df["PM2.5"].fillna(df["PM2.5"].mean())

# 등급 분류 함수 정의
def classify_pm10(value):
    if value <= 30:
        return "좋음"
    elif value <= 80:
        return "보통"
    elif value <= 150:
        return "나쁨"
    else:
        return "매우 나쁨"

def classify_pm25(value):
    if value <= 15:
        return "좋음"
    elif value <= 35:
        return "보통"
    elif value <= 75:
        return "나쁨"
    else:
        return "매우 나쁨"

# 파생변수 생성
df["PM10등급"] = df["PM10"].apply(classify_pm10)
df["PM2.5등급"] = df["PM2.5"].apply(classify_pm25)

print(df["PM10등급"].value_counts())
print(df["PM2.5등급"].value_counts())

# 1. PM10, PM2.5 전체 요약 통계
print("전체 요약 통계 (describe)")
print(df[["PM10", "PM2.5"]].describe())

# 2. PM10, PM2.5 평균 / 표준편차 / 최대 / 최소 / 중앙값
print("\n평균 / 표준편차 / 최대 / 최소 / 중앙값 (agg)")
print(df[["PM10", "PM2.5"]].agg(["mean", "std", "min", "max", "median"]))

# 3. 측정소별 PM10, PM2.5 평균값
print("\n측정소별 평균 농도")
print(df.groupby("측정소명")[["PM10", "PM2.5"]].mean())

# 4. 날짜별(일별) 평균값
print("\n날짜별 평균 농도")
print(df.groupby("날짜")[["PM10", "PM2.5"]].mean())

# 5. PM10 등급 분포
print("\nPM10 등급별 빈도")
print(df["PM10등급"].value_counts())

# 6. PM2.5 등급 분포
print("\nPM2.5 등급별 빈도")
print(df["PM2.5등급"].value_counts())

import matplotlib.pyplot as plt

# PM10 히스토그램
plt.hist(df["PM10"], bins=30, color="skyblue", edgecolor="black")
plt.title("PM10 분포 (미세먼지)")
plt.xlabel("PM10 농도")
plt.ylabel("빈도")
plt.grid(True)
plt.show()

# PM2.5 히스토그램
plt.hist(df["PM2.5"], bins=30, color="salmon", edgecolor="black")
plt.title("PM2.5 분포 (초미세먼지)")
plt.xlabel("PM2.5 농도")
plt.ylabel("빈도")
plt.grid(True)
plt.show()
