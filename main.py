import pandas as pd

df = pd.read_excel("서울대기오염_2019.xlsx")

# 1. 날짜 타입 변환
df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

# 컬럼명 변경 
df.rename(columns={
    "날짜": "date",
    "측정소명": "district",
    "미세먼지": "pm10",
    "초미세먼지": "pm25"
}, inplace=True)

# 3. 이상행 제거 (날짜가 '전체'이거나, 측정소명이 '평균'인 행 제거)
df = df[(df["date"] != "전체") & (df["district"] != "평균")]

# 4. 결측치 처리 (선택적으로 평균값으로 채움)
df["pm10"] = df["pm10"].fillna(df["pm10"].mean())
df["pm25"] = df["pm25"].fillna(df["pm25"].mean())

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

# 파생변수 생성 1
df["pm10등급"] = df["pm10"].apply(classify_pm10)
df["pm25등급"] = df["pm25"].apply(classify_pm25)


#  파생변수 생성 2
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day

#  season 파생 (계절: spring/summer/autumn/winter)
def get_season(month):
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"
    else:
        return "winter"

df["season"] = df["month"].apply(get_season)

# 7. 최종 데이터 저장
df.to_csv("card_output.csv", index=False, encoding="utf-8-sig")

#연간 미세먼지 평균 구하기
print("전체 PM10 평균:", df["pm10"].mean())

#미세먼지 최댓값 날짜 확인
max_row = df[df["pm10"] == df["pm10"].max()]
print("PM10 최대값 발생:")
print(max_row[["date", "district", "pm10"]])

#구별 pm10 평균비교
district_avg = df.groupby("district")["pm10"].mean().reset_index()
district_avg = district_avg.sort_values(by="pm10", ascending=False)
top5_districts = district_avg.head(5)
print("PM10 평균 상위 5개 구:")
print(top5_districts)


# 계절별 평균 pm10, pm2.5 평균 비교
season_avg = df.groupby("season")[["pm10", "pm25"]].mean().reset_index()
season_avg.columns = ["season", "avg_pm10", "avg_pm25"]
season_avg = season_avg.sort_values(by="avg_pm10", ascending=True)
print("계절별 평균 미세먼지:")
print(season_avg)

# pm10 등급 분류 및 분포 확인
pm_grade_counts = df["pm10등급"].value_counts().reset_index()
pm_grade_counts.columns = ["pm_grade", "n"]
pm_grade_counts["pct"] = pm_grade_counts["n"] / pm_grade_counts["n"].sum()
print("\nPM10 등급 분포 및 비율:")
print(pm_grade_counts)

# 구별 good 빈도수 계산
good_counts = df[df["pm10등급"] == "good"].groupby("district").size().reset_index(name="n")

# 전체 빈도수와 합쳐서 비율 계산
total_counts = df.groupby("district").size().reset_index(name="total")
merged = pd.merge(good_counts, total_counts, on="district")
merged["pct"] = merged["n"] / merged["total"]

# 상위 5개 추출
top5_good = merged.sort_values(by="pct", ascending=False).head(5)
print("PM10 good 비율 상위 5개 구:")
print(top5_good)

import matplotlib.pyplot as plt

# 1. 일별 PM10 추이 선그래프
daily_avg = df.groupby("date")["pm10"].mean()

plt.figure(figsize=(12, 5))
plt.plot(pd.to_datetime(daily_avg.index), daily_avg.values, color="orange")
plt.title("Daily Trend of PM10 in Seoul, 2019")
plt.xlabel("Date")
plt.ylabel("PM10 (㎍/㎥)")
plt.grid(True)
plt.tight_layout()
plt.xticks(rotation=45)
plt.show()

# 2. 계절별 PM10 등급 비율 막대그래프
# 비율 계산
season_grade = df.groupby(["season", "pm10등급"]).size().reset_index(name="n")
season_total = df.groupby("season").size().reset_index(name="total")
season_pct = pd.merge(season_grade, season_total, on="season")
season_pct["pct"] = season_pct["n"] / season_pct["total"]

# 계절별 등급 분포 시각화
seasons = ["spring", "summer", "autumn", "winter"]
grades = ["좋음", "보통", "나쁨", "매우 나쁨"]

# 데이터 정렬
season_pct["season"] = pd.Categorical(season_pct["season"], categories=seasons, ordered=True)
season_pct["pm10등급"] = pd.Categorical(season_pct["pm10등급"], categories=grades, ordered=True)
season_pct = season_pct.sort_values(["season", "pm10등급"])

# 누적 막대그래프 그리기
pivot = season_pct.pivot(index="season", columns="pm10등급", values="pct")
pivot.fillna(0, inplace=True)
pivot.plot(kind="bar", stacked=True, figsize=(10, 5))

plt.title("Seasonal Distribution of PM10 Grades in Seoul, 2019")
plt.xlabel("Season")
plt.ylabel("Proportion")
plt.legend(title="PM10 등급")
plt.tight_layout()
plt.show()

