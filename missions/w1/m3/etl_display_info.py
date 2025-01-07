import pandas as pd

def display_info(df: pd.DataFrame):
    print("\033[31m--- Country have more than 100B GDP ---\033[0m")
    pd.options.display.float_format = "{:.2f}".format  # 소수점 둘째자리 까지 프린트
    pd.options.display.max_rows = 100  # 최대 row 개수 조정
    print(df[df['GDP'] >= 100])
    print()
    print("\033[31m--- Each region's mean GDP of top 5 country ---\033[0m")
    for idx, region in enumerate(df['region'].unique()):
        if pd.notna(region):
            print(f"""\033[{32 + idx}m{region.upper():8}\033[0m : {df[df['region'] == region]
                  .sort_values(ascending=False, by='GDP')
                  .head(5)['GDP'].mean():.2f}""")