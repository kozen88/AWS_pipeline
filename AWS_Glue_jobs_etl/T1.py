"""
    ENGLISH

    WARNINGS!!

    The following script cannot be run locally as a regular Python script. It must be executed
    in an AWS Glue environment.

    Follow the detailed steps below to configure this script via AWS Glue:

    STEP_1: Create an IAM Role for an ETL Job in AWS Glue
    1. Create an IAM role for AWS Glue
    2. Go to the IAM console.
    3. Create a new role and choose "Glue" as the service.
    4. Attach the necessary policies, such as AmazonS3FullAccess and AmazonRedshiftFullAccess,
       or create a custom policy with specific permissions to access the required resources.
    5. Complete the role creation and note the role's ARN.

    STEP_2: Create an ETL Job in AWS Glue
    1. Go to the AWS Glue console.
    2. In the left navigation pane, select "Jobs" and then click on "Add job".
    3. Configure the job:
            - Name: Give your job a name.
            - Description: Provide a concise description of what the job does.
            - IAM Role: Select the IAM role created previously.
            - Type: Set the type to "Spark".
            - Glue version: Use the latest available version of Glue.
            - This job runs: Select "A new script to be authored by you".
    4. In the "Script" section, paste the code below present in this file:
    5. Save the job.
"""

"""
    ITALIANO
    
    ATTENZIONE!!!!

    Lo script seguente non può essere eseguito localmente come uno script Python normale. Deve essere eseguito
    in un ambiente AWS Glue.

    Seguire i sottostanti passaggi dettagliati per configurare questo script tramite AWS Glue:

    STEP_1: Creazione ruolo IAM per un Job ETL in AWS Glue
    1. Creare un ruolo IAM per AWS Glue
    2. Vai alla console IAM.
    3. Crea un nuovo ruolo e scegli "Glue" come servizio di destinazione.
    4. Assegna le policy necessarie, come AmazonS3FullAccess e AmazonRedshiftFullAccess,
       o crea una policy personalizzata con le autorizzazioni specifiche per accedere alle risorse necessarie.
    5. Completa la creazione del ruolo e prendi nota dell'ARN del ruolo.


    STEP_2: Creazione di un Job ETL in AWS Glue
    1. Vai alla console AWS Glue.
    2. Nel pannello di navigazione a sinistra, seleziona "Jobs" e poi clicca su "Add job".
    3. Configura il job:
            - Nome: Dai un nome al tuo job.
            - Descrizione: dai una descrizione concisa di quello che fa il job che crei.
            - Ruolo IAM: Seleziona il ruolo IAM creato precedentemente.
            - Type: Scala the type a "Spark".
            - Glue version: Usa l'ultima versione disponibile di Glue.
            - This job runs: Seleziona "A new script to be authored by you".
    4. Nella sezione "Script", incolla il codice sottostante presente in questo file:
    5. Salva il job così creato.
"""

# THE SCRIPT MUST BE RUN IN THE AWS GLUE ENVIRONMENT BY PASTING IT AS A SPARK SCRIPT TYPE

import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, mean
from pyspark.sql.window import Window
from concurrent.futures import ThreadPoolExecutor
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
spark = SparkSession.builder.appName(args['JOB_NAME']).getOrCreate()
glueContext = GlueContext(spark.sparkContext)
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Define S3 paths
raw_bucket = 's3://raw3'
silver_bucket = 's3://silver2step'

def process_price_data(file_path, output_path):
    # Load data
    df = spark.read.csv(file_path, header=True, inferSchema=True)

    # Select relevant columns and convert data types
    df = df.select(col('Date').cast('date'), col('Price').cast('float'))

    # Handle missing price values (-1) with the mean of the closest 4 values
    window_spec = Window.orderBy('Date').rowsBetween(-2, 2)
    df = df.withColumn('Price', when(df['Price'] == -1, None).otherwise(df['Price']))
    df = df.withColumn('Price', when(df['Price'].isNull(),
                                     mean('Price').over(window_spec)).otherwise(df['Price']))

    # Save cleaned data to S3 in Parquet format
    df.write.parquet(output_path)

def process_google_trend_data(file_path, output_path):
    # Load data
    df = spark.read.csv(file_path, header=True, inferSchema=True)

    # Convert data types and drop rows with missing values
    df = df.select(col('Settimana').cast('date'), col('interesse bitcoin').cast('int')).dropna()

    # Save cleaned data to S3 in Parquet format
    df.write.parquet(output_path)

# Use ThreadPoolExecutor to parallelize the processing
with ThreadPoolExecutor(max_workers=4) as executor:
    future_btc_price = executor.submit(process_price_data, f'{raw_bucket}/BTC-EUR-Historical-Data.csv', f'{silver_bucket}/btc_price_cleaned')
    future_btc_trend = executor.submit(process_google_trend_data, f'{raw_bucket}/google-trend-bitcoin.csv', f'{silver_bucket}/btc_google_trend_cleaned')
    future_xmr_price = executor.submit(process_price_data, f'{raw_bucket}/XMR-EUR-Kraken-Historical-Data.csv', f'{silver_bucket}/xmr_price_cleaned')
    future_xmr_trend = executor.submit(process_google_trend_data, f'{raw_bucket}/google-trend-monero.csv', f'{silver_bucket}/xmr_google_trend_cleaned')

    # Wait for all futures to complete
    future_btc_price.result()
    future_btc_trend.result()
    future_xmr_price.result()
    future_xmr_trend.result()

job.commit()