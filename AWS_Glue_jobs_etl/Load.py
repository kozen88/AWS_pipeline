"""
   ENGLISH
   WARNINGS!!

    This script must be run in the AWS Glue environment as a Spark script type!

    Before running it, since external libraries are used outside of the AWS environment, we need to upload these
    libraries to a dedicated bucket. We will indicate this bucket during the job creation to use the external libraries.
    Specifically, you need to create a zip file containing the boto3 and psycopg2 libraries downloaded via the Python
    package manager pip. Once you have the zip file, upload it to a bucket on AWS.

    Then, follow the detailed steps below to configure this script via AWS Glue:

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
    ATTENZIONE!!!

    Questo script deve essere eseguito in ambiente AWS Glue come script type spark!

    Prima di eseguirlo, poichè vengono usate librerie esterne all'ambiebte AWS dobbiamo caricare tali librerie
    in un bucket apposito dal quale daremo indicazione durante la creazione del job di attingere da tale bucket
    per l'utilizzo delle librerie esterne. In particolare bisogna creare uno zip che contenga le librerie
    boto3 e psycopg2 scaricate tramite il gestore dei pacchetti di python pip. Una volta ottenuto il file zip
    caricarlo in un bucket su AWS.

    In seguito seguire i sottostanti passaggi dettagliati per configurare questo script tramite AWS Glue:

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

# THE SCRIPT MUST BE RUN ON THE AWS GLUE ENVIRONMENT BY PASTING IT AS A SPARK SCRIPT TYPE

import sys
import boto3
import psycopg2
from psycopg2 import sql
from concurrent.futures import ThreadPoolExecutor
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext

# Ottieni argomenti dal contesto AWS Glue
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Configurazioni S3 e Redshift
s3_bucket = 's3://gold3step'
redshift_endpoint = 'your-redshift-serverless-endpoint.redshift-serverless.amazonaws.com'
database = 'CryptoDataDB'
port = '5439'
iam_role = 'arn:aws:iam::your-account-id:role/your-redshift-role'

# Funzione per ottenere le credenziali temporanee da Redshift Serverless
def get_redshift_credentials():
    client = boto3.client('redshift-serverless')
    response = client.get_credentials(
        workgroupName='your-workgroup-name',
        dbName=database
    )
    return response['dbUser'], response['dbPassword']

# Funzione per caricare i dati su Redshift
def load_data_to_redshift(file_path, table_name):
    user, password = get_redshift_credentials()

    conn = psycopg2.connect(
        dbname=database,
        user=user,
        password=password,
        port=port,
        host=redshift_endpoint
    )

    cursor = conn.cursor()

    # Crea la copia del comando SQL
    copy_sql = sql.SQL("""
        COPY {table}
        FROM {file}
        IAM_ROLE '{iam_role}'
        FORMAT AS PARQUET;
    """).format(
        table=sql.Identifier(table_name),
        file=sql.Literal(file_path),
        iam_role=sql.Literal(iam_role)
    )

    try:
        cursor.execute(copy_sql)
        conn.commit()
        print(f"Data loaded successfully into {table_name}")
    except Exception as e:
        print(f"Error loading data into {table_name}: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Usa ThreadPoolExecutor per parallelizzare il caricamento
with ThreadPoolExecutor(max_workers=2) as executor:
    future_btc = executor.submit(
        load_data_to_redshift,
        f'{s3_bucket}/btc_final',
        'btc_data'
    )
    future_xmr = executor.submit(
        load_data_to_redshift,
        f'{s3_bucket}/xmr_final',
        'xmr_data'
    )

    # Aspetta che entrambi i future siano completati
    future_btc.result()
    future_xmr.result()

job.commit()