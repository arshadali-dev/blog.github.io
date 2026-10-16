# Runs on Fabric Spark. Upload to OneLake; pass the output path as argv[1].
import sys
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
spark.range(1, 4).write.mode("errorifexists").json(sys.argv[1])
