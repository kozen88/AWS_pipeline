"""
    ENGLISH
    WARNINGS!!

    This script must be run in an AWS Glue environment as a Spark script type.

    To do this and create an AWS Glue job that implements this pipeline, follow the detailed steps below to configure
    this script via AWS Glue:

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
    ITTALIANO
    ATTENZIONE!!!

    Questo script deve essere eseguito in un ambiente AWS Glue come script type spark.

    Per farlo e creare un job AWS Glue che implementi questa pipeline seguire i sottostanti
    passaggi dettagliati per configurare questo script tramite AWS Glue:

    STEP_1: Creazione ruolo IAM per un Job ETL in AWS Glue
    1. Creare un ruolo IAM per AWS Glue
    2. Vai alla console IAM.
    3. Crea un nuovo ruolo e scegli "Glue" come servizio di destinazione.
    4. Assegna le policy necessarie, come AmazonS3FullAccess e AmazonRedshiftFullAccess,
       o crea una policy personalizzata
       con le autorizzazioni specifiche per accedere alle risorse necessarie.
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
from pyspark.sql.functions import col, avg
from pyspark.sql.window import Window
from concurrent.futures import ThreadPoolExecutor
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
spark = SparkSession.builder.appName(args['JOB_NAME']).getOrCreate()
glueContext = GlueContext(spark.sparkContext)
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Define S3 paths
silver_bucket = 's3://silver2step'
gold_bucket = 's3://gold3step'


def process_and_merge_data(price_file, trend_file, output_path):
    # Load data
    price_df = spark.read.parquet(price_file)
    trend_df = spark.read.parquet(trend_file)

    # Calculate 10-day moving average for Price
    window_spec = Window.orderBy('Date').rowsBetween(-9, 0)
    price_df = price_df.withColumn('Price_MA', avg('Price').over(window_spec))

    # Join on the closest week
    merged_df = price_df.join(
        trend_df,
        price_df.Date.cast('date') == trend_df.Settimana.cast('date'),
        'inner'
    ).select(
        price_df.Date.alias('data'),
        price_df.Price_MA.alias('prezzo'),
        trend_df['interesse bitcoin'].alias('indice_google_trend')
    )

    # Save merged data to S3 in Parquet format
    merged_df.write.parquet(output_path)


# Use ThreadPoolExecutor to parallelize the processing
with ThreadPoolExecutor(max_workers=2) as executor:
    future_btc = executor.submit(
        process_and_merge_data,
        f'{silver_bucket}/btc_price_cleaned',
        f'{silver_bucket}/btc_google_trend_cleaned',
        f'{gold_bucket}/btc_final'
    )
    future_xmr = executor.submit(
        process_and_merge_data,
        f'{silver_bucket}/xmr_price_cleaned',
        f'{silver_bucket}/xmr_google_trend_cleaned',
        f'{gold_bucket}/xmr_final'
    )

    # Wait for both futures to complete
    future_btc.result()
    future_xmr.result()

job.commit()