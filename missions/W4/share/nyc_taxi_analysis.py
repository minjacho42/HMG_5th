from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import sys

"""
VendorID,tpep_pickup_datetime,tpep_dropoff_datetime,passenger_count,trip_distance,
RatecodeID,store_and_fwd_flag,PULocationID,DOLocationID,
payment_type,fare_amount,extra,mta_tax,tip_amount,tolls_amount,improvement_surcharge,total_amount,congestion_surcharge,Airport_fee
"""

def data_cleaning(df):
    # 가격이 음수인 경우 결측치로 처리
    df = df.withColumn(
        "total_amount",when(col("total_amount") <= 0, None)
        .otherwise(col("total_amount"))
    )
    df = df.dropna()
    # 이상한 값 결측치로 처리.
    df = df.withColumn(
        "trip_min", when((col("trip_min") <= 0) | (col("trip_min") > 1380), None)
        .otherwise(col("trip_min"))
    )
    # 결제 금액과 운행 거리가 비정상적인 경우 결측치로 처리.
    df = df.withColumn(
        "dollar_per_min",
        when((col("trip_min").isNull()) | (col("trip_min") == 0), None)
        .otherwise(col("total_amount") / col("trip_min"))
    )
    df = df.withColumn(
        "dollar_per_min",
        when((col("dollar_per_min") >= 5) | (col("dollar_per_min") <= 0.1), None)
        .otherwise(col("dollar_per_min"))
    )
    # 결측치 모두 제거
    df = df.dropna()
    # 이후 분석에 필요없는 column 제거
    df = df.drop("VendorID", "store_and_fwd_flag", "PULocationID", "DOLocationID")
    return df

def calculate_avg_trip_duration(df):
    avg_df = df.select(
        avg("trip_min").alias("avg_trip_duration_min")
        , avg("trip_distance").alias("avg_trip_distance_miles")
    )
    avg_df.show()
    return avg_df

def main(input_path, output_path):
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
    print("[NYC_Taxi_Analysis] Average calculation DONE")
    print("[NYC_Taxi_Analysis] Saving average calculation result")
    nyc_taxi_avg_df.write.mode("overwrite").csv(output_path + "/nyc_taxi_analysis_avg_data", header=True, sep=",")

    print("[NYC_Taxi_Analysis] Hourly analysis START")
    nyc_taxi_hour_df = nyc_taxi_df.withColumn(
        'hour', hour(col('tpep_pickup_datetime'))
    ).groupBy('hour').count().orderBy(col('hour'))
    print("[NYC_Taxi_Analysis] Hourly analysis DONE")
    nyc_taxi_hour_df.show(24)
    print("[NYC_Taxi_Analysis] Saving hourly analysis result")
    nyc_taxi_hour_df.write.mode("overwrite").csv(output_path + "/nyc_taxi_analysis_hour_data", header=True, sep=",")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: nyc_taxi_analysis <year> <input_path> <output_path>", file=sys.stderr)
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    main(input_path, output_path)