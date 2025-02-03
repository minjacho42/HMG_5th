from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import sys

"""
VendorID,tpep_pickup_datetime,tpep_dropoff_datetime,passenger_count,trip_distance,
RatecodeID,store_and_fwd_flag,PULocationID,DOLocationID,
payment_type,fare_amount,extra,mta_tax,tip_amount,tolls_amount,improvement_surcharge,total_amount,congestion_surcharge,Airport_fee
"""

# 이상치를 제거하는 함수. 표준점수가 3.5이상 넘어가면 필터링된다.
def remove_outliers_zscore(df, columns, threshold=3.5):
    stats = df.select(
        *[mean(col(c)).alias(f"{c}_mean") for c in columns],
        *[stddev(col(c)).alias(f"{c}_stddev") for c in columns]
    ).collect()[0]

    for c in columns:
        mean_val = stats[f"{c}_mean"]
        stddev_val = stats[f"{c}_stddev"]
        df = df.filter(((col(c) - mean_val) / stddev_val).between(-threshold, threshold))

    return df

def data_cleaning(df):
    df = df.filter(col("trip_min") > 0)
    df = df.filter(col("total_amount") > 0)
    df = df.filter(col("trip_distance") > 0)
    df = remove_outliers_zscore(df, ["trip_distance", "total_amount", "trip_min"])
    df = df.dropna()

    # 이후 분석에 필요없는 column 제거
    df = df.drop("VendorID", "store_and_fwd_flag", "RatecodeID", "PULocationID", "DOLocationID", "payment_type")
    return df

def calculate_avg_trip_duration(df):
    avg_df = df.select(
        avg("trip_min").alias("avg_trip_duration_min")
        , avg("trip_distance").alias("avg_trip_distance_miles")
    )
    avg_df.show()
    return avg_df

def main(input_path, output_path, weather_dataset_path):
    spark = SparkSession.builder.appName("NYC_Taxi_Analysis").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    nyc_taxi_df = spark.read.option("header", True).csv(input_path+"/*.csv")
    nyc_taxi_df = nyc_taxi_df.withColumn("tpep_pickup_datetime", nyc_taxi_df["tpep_pickup_datetime"].cast("timestamp"))
    nyc_taxi_df = nyc_taxi_df.withColumn("tpep_dropoff_datetime", nyc_taxi_df["tpep_dropoff_datetime"].cast("timestamp"))

    # trip_min column 추가
    nyc_taxi_df = nyc_taxi_df.withColumn(
        "trip_min",
        floor((unix_timestamp(col("tpep_dropoff_datetime")) - unix_timestamp(col("tpep_pickup_datetime"))) / 60)
    )
    print("[NYC_Taxi_Analysis] Row count before clean DataFrame : ", nyc_taxi_df.count())
    print("[NYC_Taxi_Analysis] DataFrame cleaning START")
    nyc_taxi_df = data_cleaning(nyc_taxi_df)
    print("[NYC_Taxi_Analysis] DataFrame cleaning DONE")
    # nyc_taxi_df.write.mode("overwrite").csv(output_path + "/nyc_taxi_analysis_data_cleand", header=True, sep=",")
    print("[NYC_Taxi_Analysis] Row count after clean DataFrame : ", nyc_taxi_df.count())

    print("[NYC_Taxi_Analysis] Average calculation START")
    nyc_taxi_avg_df = calculate_avg_trip_duration(nyc_taxi_df)
    print("[NYC_Taxi_Analysis] Saving average calculation result")
    nyc_taxi_avg_df.write.mode("overwrite").csv(output_path + "/nyc_taxi_analysis_avg_data", header=True, sep=",")
    print("[NYC_Taxi_Analysis] Average calculation DONE")

    print("[NYC_Taxi_Analysis] Hourly analysis START")
    nyc_taxi_hour_df = nyc_taxi_df.withColumn(
        'hour', hour(col('tpep_pickup_datetime'))
    ).groupBy('hour').count().orderBy(col('hour'))
    nyc_taxi_hour_df.show(24)
    print("[NYC_Taxi_Analysis] Saving hourly analysis result")
    nyc_taxi_hour_df.write.mode("overwrite").csv(output_path + "/nyc_taxi_analysis_hour_data", header=True, sep=",")
    print("[NYC_Taxi_Analysis] Hourly analysis DONE")

    print("[NYC_Taxi_Analysis] Weather related analysis START")
    print("[NYC_Taxi_Analysis] Weather dataset loading")
    nyc_weather_df = spark.read.option("header", True).csv(weather_dataset_path)
    print("[NYC_Taxi_Analysis] Weather dataset loaded")
    print("[NYC_Taxi_Analysis] Aggregating hourly data trip_count, avg_trip_distance, avg_total_amount, avg_trip_min")
    nyc_taxi_hourly_df = nyc_taxi_df.withColumn(
        'pickup_date_hour', date_format(
            col('tpep_pickup_datetime'), 'yyyy-MM-dd HH:00:00')
    )
    nyc_taxi_hourly_summary = nyc_taxi_hourly_df.groupBy(
        'pickup_date_hour'
    ).agg(
        count(col('tpep_pickup_datetime')).alias('trip_count'),
        avg(col('trip_distance')).alias('avg_trip_distance'),
        avg(col('total_amount')).alias('avg_total_amount'),
        avg(col('trip_min')).alias('avg_trip_min')
    )
    """date,temperature_2m,apparent_temperature,precipitation,cloud_cover,wind_speed_10m"""
    nyc_weather_df = nyc_weather_df.withColumn("date", nyc_weather_df["date"].substr(1,19).cast("timestamp"))
    nyc_weather_df = nyc_weather_df.withColumn("date", date_format(col("date"), "yyyy-MM-dd HH:00:00"))

    print("[NYC_Taxi_Analysis] Weather DataFrame join with nyc taxi hourly data")
    nyc_taxi_weather_hourly_df = nyc_taxi_hourly_summary.join(nyc_weather_df, nyc_taxi_hourly_summary["pickup_date_hour"] == nyc_weather_df["date"], "left")
    nyc_taxi_weather_hourly_df = nyc_taxi_weather_hourly_df.drop("date")
    nyc_taxi_weather_hourly_df = nyc_taxi_weather_hourly_df.dropna()
    nyc_taxi_weather_hourly_df.orderBy(col('pickup_date_hour')).show(24)
    print("[NYC_Taxi_Analysis] Saving hourly analysis result")
    nyc_taxi_weather_hourly_df.write.mode("overwrite").csv(output_path + "/nyc_taxi_analysis_weather_hourly_data", header=True, sep=",")
    print("[NYC_Taxi_Analysis] Weather related analysis DONE")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: nyc_taxi_analysis <input_path> <output_path> <weather_dataset_path>", file=sys.stderr)
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    weather_dataset_path = sys.argv[3]
    main(input_path, output_path, weather_dataset_path)