# Databricks notebook source
from pyspark.sql.functions import *
from pyspark.sql.types import *

# COMMAND ----------

# MAGIC %md
# MAGIC ### Setup access to Azure Data Lake 

# COMMAND ----------

spark.conf.set( "fs.azure.account.key.mdwt1lake.dfs.core.windows.net","BA50Dzu5z8Vt78Sq6oeB4NLDlvIsNt2MCvXSIIL+mImIwHWwMga+xGOeHIDtg/ZrFPlAxaeNigVkt7N44kdwOQ==")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Fourth Coffee

# COMMAND ----------

fourthCoffeeMovies = spark.read.parquet("abfss://southridge@mdwt1lake.dfs.core.windows.net/fourth_coffee/2020/08/31/Movies.parquet")
fourthCoffeeActors = spark.read.parquet("abfss://southridge@mdwt1lake.dfs.core.windows.net/fourth_coffee/2020/08/31/Actors.parquet")
fourthCoffeeMovieActors = spark.read.parquet("abfss://southridge@mdwt1lake.dfs.core.windows.net/fourth_coffee/2020/08/31/MovieActors.parquet")
fourthCoffeeMovieMappings =  spark.read.parquet("abfss://southridge@mdwt1lake.dfs.core.windows.net/fourth_coffee/2020/08/31/OnlineMovieMappings.parquet")

# COMMAND ----------

# join data frames
fourthCoffee = fourthCoffeeMovieActors.join(fourthCoffeeMovies, "MovieID").join(fourthCoffeeActors, "ActorID").join(fourthCoffeeMovieMappings, "MovieID", how='left')

# COMMAND ----------

fourthCoffee.printSchema()

# COMMAND ----------

# rename columns
fourthCoffee = fourthCoffee \
  .withColumnRenamed("MovieID", "SourceSystemMovieID") \
  .withColumnRenamed("MovieTitle", "Title") \
  .withColumnRenamed("Category", "Genre") \
  .withColumnRenamed("RunTimeMin", "RuntimeMinutes") \
  .withColumnRenamed("ReleaseDate", "PhysicalAvailabilityDate") \
  .withColumnRenamed("ActorName", "ActorName") \
  .withColumnRenamed("Gender", "ActorGender") \
  .withColumnRenamed("OnlineMovieID", "SouthridgeMovieID") \
  .withColumn("TheatricalReleaseYear", lit(None).cast(LongType())) \
  .withColumn("StreamingAvailabilityDate", lit(None).cast(DateType())) \
  .drop("MovieActorID")

# COMMAND ----------

# convert string to date
fourthCoffee = fourthCoffee.withColumn("PhysicalAvailabilityDate", to_date(col("PhysicalAvailabilityDate"), "MM-dd-yyyy")).withColumn("RuntimeMinutes", col("RuntimeMinutes").cast(LongType()))

# COMMAND ----------

# adding column (2 == FourthCoffee)
fourthCoffee = fourthCoffee.withColumn('SourceSystemID', lit(2))

# COMMAND ----------

# adding column (uuid)
import uuid
uuidUdf = udf(lambda : str(uuid.uuid4()), StringType())
fourthCoffee = fourthCoffee.withColumn("GlobalMovieID", uuidUdf())

# COMMAND ----------

fourthCoffee.show()

# COMMAND ----------

fourthCoffee.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Sourthridge

# COMMAND ----------

southRidgeSource = spark.read.option("multiline", True).json("abfss://southridge@mdwt1lake.dfs.core.windows.net/Movies/Movies.json")

# COMMAND ----------

southRidgeSource.show()

# COMMAND ----------

# rename columns
southRidgeSource = southRidgeSource \
  .withColumnRenamed("id", "SourceSystemMovieID") \
  .withColumn("SouthridgeMovieID", col("SourceSystemMovieID")) \
  .withColumnRenamed("title", "Title") \
  .withColumnRenamed("genre", "Genre") \
  .withColumnRenamed("rating", "Rating") \
  .withColumnRenamed("runtime", "RuntimeMinutes") \
  .withColumnRenamed("availabilityDate", "PhysicalAvailabilityDate") \
  .withColumnRenamed("streamingAvailabilityDate", "StreamingAvailabilityDate") \
  .withColumnRenamed("releaseYear", "TheatricalReleaseYear") \
  .withColumn("actors", explode("actors.name")) \
  .withColumnRenamed("actors", "ActorName") \
  .withColumn("ActorID", uuidUdf()) \
  .withColumn("ActorGender", lit("U")) \
  .drop("tier")


# COMMAND ----------

# convert string to date
southRidgeSource = southRidgeSource.withColumn("PhysicalAvailabilityDate", to_date(col("PhysicalAvailabilityDate"), "yyyy-MM-dd HH:mm:ss"))
southRidgeSource = southRidgeSource.withColumn("StreamingAvailabilityDate", to_date(col("StreamingAvailabilityDate"), "yyyy-MM-dd HH:mm:ss"))

# COMMAND ----------

southRidgeSource.printSchema()

# COMMAND ----------

# adding column (1 == SouthRidge)
southRidgeSource = southRidgeSource.withColumn('SourceSystemID', lit(1))

# COMMAND ----------

southRidgeSource = southRidgeSource.withColumn("GlobalMovieID", uuidUdf())

# COMMAND ----------

southRidgeSource.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Van Arsdel

# COMMAND ----------

vanArsdelMovies = spark.read.parquet("abfss://southridge@mdwt1lake.dfs.core.windows.net/vanarsdel/2020/09/01/dboMovies.parquet")
vanArsdelActors = spark.read.parquet("abfss://southridge@mdwt1lake.dfs.core.windows.net/vanarsdel/2020/09/01/dboActors.parquet")
vanArsdelMovieActors = spark.read.parquet("abfss://southridge@mdwt1lake.dfs.core.windows.net/vanarsdel/2020/09/01/dboMovieActors.parquet")
vanArsdelMovieMappings =  spark.read.parquet("abfss://southridge@mdwt1lake.dfs.core.windows.net/vanarsdel/2020/09/01/dboOnlineMovieMappings.parquet")

# COMMAND ----------

vanArsdel = vanArsdelMovieActors.join(vanArsdelMovies, "MovieID").join(vanArsdelActors, "ActorID").join(vanArsdelMovieMappings, "MovieID", how='left')

# COMMAND ----------

# rename columns
vanArsdel = vanArsdel \
  .withColumnRenamed("MovieID", "SourceSystemMovieID") \
  .withColumnRenamed("MovieTitle", "Title") \
  .withColumnRenamed("Category", "Genre") \
  .withColumnRenamed("RunTimeMin", "RuntimeMinutes") \
  .withColumnRenamed("ReleaseDate", "PhysicalAvailabilityDate") \
  .withColumnRenamed("ActorName", "ActorName") \
  .withColumnRenamed("Gender", "ActorGender") \
  .withColumnRenamed("OnlineMovieID", "SouthridgeMovieID") \
  .withColumn("TheatricalReleaseYear", lit(None).cast(LongType())) \
  .withColumn("StreamingAvailabilityDate", lit(None).cast(DateType())) \
  .drop("MovieActorID")

# COMMAND ----------

vanArsdel.printSchema()

# COMMAND ----------

vanArsdel = vanArsdel.withColumn("PhysicalAvailabilityDate", to_date(col("PhysicalAvailabilityDate"), "MM-dd-yyyy")).withColumn("RuntimeMinutes", col("RuntimeMinutes").cast(LongType()))

# COMMAND ----------

vanArsdel = vanArsdel.withColumn('SourceSystemID', lit(3))

# COMMAND ----------

vanArsdel = vanArsdel.withColumn("GlobalMovieID", uuidUdf())

# COMMAND ----------

vanArsdel.show()

# COMMAND ----------

vanArsdel.printSchema()

# COMMAND ----------



# COMMAND ----------

# MAGIC %md
# MAGIC ### Union

# COMMAND ----------

target = vanArsdel.unionByName(fourthCoffee).unionByName(southRidgeSource)

# COMMAND ----------

print(fourthCoffee.count())
print(vanArsdel.count())
print(southRidgeSource.count())
print(target.count())

# COMMAND ----------

target.show()

# COMMAND ----------

target.printSchema()

# COMMAND ----------



# COMMAND ----------

# MAGIC %md ## Standardization & checks

# COMMAND ----------

def unifyRating(rating):
  if rating == "PG=13":
    return "PG-13"
  return rating

# COMMAND ----------

ratingUdf = udf(lambda rating: unifyRating(rating), StringType())

# COMMAND ----------

target.where(col("Rating")=="PG-13").show()

# COMMAND ----------

def unifyGenre(genre):
  if genre == "Science Fact":
    return "Science Fiction"
  return genre

# COMMAND ----------

genreUdf = udf(lambda genre: unifyGenre(genre), StringType())

# COMMAND ----------

target = target.withColumn("Rating", lit(ratingUdf(col("Rating")))) \
  .withColumn("Genre", genreUdf(col("Genre")))

# COMMAND ----------

target.where(col("Rating")=="PG-13").show()

# COMMAND ----------

target.where(col("Rating")=="PG=13").show()

# COMMAND ----------

target.where(col("Genre")=="Science Fact").show()

# COMMAND ----------

# MAGIC %md ## Testing 😎

# COMMAND ----------

import pytest

def test_unifyRating():
  inputRating = "PG=13"
  expectedRating = "PG-13"
  actualRating = unifyRating(inputRating)
  if actualRating != expectedRating:
    pytest.fail("WTF!")
  else:
    pass

# COMMAND ----------

test_unifyRating()

# COMMAND ----------

def test_unifyGenre():
  inputGenre="Science Fact"
  expectedGenre="Science Fiction"
  actualGenre = unifyGenre(inputGenre)
  assert actualGenre == expectedGenre

# COMMAND ----------

test_unifyGenre()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Export

# COMMAND ----------

target.write.mode("overwrite").parquet("abfss://southridge@mdwt1lake.dfs.core.windows.net/datastaging/Catalog")

# COMMAND ----------

