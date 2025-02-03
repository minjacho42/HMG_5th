from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql.functions import *
import sys

BASE_FILENAME = "/{}-{}-{}.parquet"

def extract_data_rdd(year, month, category, path, spark: SparkSession):
    df = spark.read.parquet(
        path + "/nyc_taxi_data" + BASE_FILENAME.format(year, str(month).zfill(2), category)
    ).select("tpep_pickup_datetime", "tpep_dropoff_datetime", "trip_distance", "total_amount")
    return df.rdd

def filter_data(rdd):
    rdd = rdd.filter(lambda row: row['trip_distance'] > 0)
    return rdd

def get_total_info(rdd):
    total_rides = rdd.count()
    total_amount = rdd.map(lambda row: row['total_amount']).sum()
    avg_distance = rdd.map(lambda row: row['trip_distance']).sum() / total_rides

    return total_rides, total_amount, avg_distance

def get_daily_info(rdd):
    rdd_date = rdd.map(lambda row: (row['tpep_pickup_datetime'].date(), (row['total_amount'], 1)))
    rdd_date_total_amount_count = rdd_date.reduceByKey(lambda x, y: (x[0] + y[0], x[1] + y[1]))
    return rdd_date_total_amount_count

if __name__ == "__main__":
    arg_year = sys.argv[1]
    arg_month = sys.argv[2]
    arg_category = sys.argv[3]
    arg_path = sys.argv[4]
    print(f"Year: {arg_year}, Month: {arg_month}, Category: {arg_category}, Path: {arg_path}")
    spark = SparkSession.builder.appName("NYC Taxi Analysis").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    rdd = extract_data_rdd(arg_year, arg_month, arg_category, arg_path, spark)
    rdd = filter_data(rdd)
    total_rides, total_amount, avg_distance = get_total_info(rdd)
    print(f"Total rides: {total_rides}")
    print(f"Total amount: {total_amount}")
    print(f"Average distance: {avg_distance}")
    df_total_info = spark.createDataFrame([Row(total_rides=total_rides, total_amount=total_amount, avg_distance=avg_distance)])
    df_total_info.coalesce(1).write.mode("overwrite").json(arg_path+f"/total_info_{arg_year}-{str(arg_month).zfill(2)}-{arg_category}")
    daily_info = get_daily_info(rdd)
    df_daily_info = daily_info.map(lambda x: Row(date=x[0], total_amount=x[1][0], ride_count=x[1][1])).toDF()
    df_daily_info.coalesce(1).write.mode("overwrite").parquet(arg_path+f"/daily_info_{arg_year}-{str(arg_month).zfill(2)}-{arg_category}")