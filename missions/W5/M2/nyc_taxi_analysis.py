import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql.functions import *
import sys

BASE_FILENAME = "nyc_taxi_data/{}-{}-{}.parquet"

COLUMNS = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "fare_amount",
    "extra",
    "tip_amount",
    "tolls_amount",
    "total_amount",
    "congestion_surcharge",
    "Airport_fee"
]

def extract_data_df(year, month, category, path, spark: SparkSession):
    df = spark.read.parquet(
        path + BASE_FILENAME.format(year, str(month).zfill(2), category)
    ).select(COLUMNS)
    return df

def filter_data(df:pyspark.sql.DataFrame, year, month):
    drop_na_subset = ["tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count", "trip_distance", "total_amount"]
    df = df.dropna(subset=drop_na_subset)
    df = df.fillna(0, subset=list(set(COLUMNS) - set(drop_na_subset)))
    df = df.filter(array_min(array(*[col(c) for c in COLUMNS[2:]])) >= 0)
    df = df.filter(col("tpep_pickup_datetime") < col("tpep_dropoff_datetime"))
    df = df.filter(month(col("tpep_pickup_datetime")) == month)
    df = df.filter(col("trip_distance") <= 100) # 이상치 제거
    df = df.filter(col("total_amount") <= 1000) # 이상치 제거
    return df

def add_columns(df:pyspark.sql.DataFrame):
    df = df.withColumn(
        "trip_duration_min",
        (col("tpep_dropoff_datetime").cast("long") - col("tpep_pickup_datetime").cast("long")) / 60
    ) # trip_duration_min column 생성.
    df = df.withColumn(
        "pickup_date_hour",
        date_trunc("hour", col("tpep_pickup_datetime"))
    ) # pickup_date_hour 설정.
    return df

def group_by_hourly_data(df:pyspark.sql.DataFrame):
    hourly_df = df.groupBy("pickup_date_hour").agg(
        count(col("tpep_pickup_datetime")).alias("trip_count"),
        avg(col("trip_distance")).alias("avg_trip_distance"),
        avg(col("total_amount")).alias("avg_total_amount"),
        avg(col("trip_duration_min")).alias("avg_trip_duration_min")
    ).orderBy(col("pickup_date_hour"))
    return hourly_df

if __name__ == "__main__":
    arg_year = sys.argv[1]
    arg_month = sys.argv[2]
    arg_category = sys.argv[3]
    arg_path = sys.argv[4]
    print(f"Year: {arg_year}, Month: {arg_month}, Category: {arg_category}, Path: {arg_path}")
    spark = SparkSession.builder.appName("NYC Taxi Analysis").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    df = extract_data_df(arg_year, arg_month, arg_category, arg_path, spark)
    df = filter_data(df, arg_year, arg_month)
    df = add_columns(df)
    df.cache()
    hourly_df = group_by_hourly_data(df)
    hourly_df.cache()
    hourly_weather_df = spark.read.csv(arg_path+f"nyc_weather_data/nyc_taxi_weather_hourly_data.csv")
    hourly_weather_df = hourly_weather_df.withColumnRenamed("date", "pickup_date_hour")
    hourly_df.withColumn("pickup_date_hour", col("pickup_date_hour").cast("date")).show()
    hourly_nyc_taxi_weather_df = hourly_df.join(hourly_weather_df, "pickup_date_hour", "left")
    hourly_nyc_taxi_weather_df.coalesce(1).write.mode("overwrite").json(arg_path+f"/hourly_info_with_weather_{arg_year}-{str(arg_month).zfill(2)}-{arg_category}")