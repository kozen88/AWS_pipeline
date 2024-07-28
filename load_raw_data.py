"""
    ENGLISH HELP!
    Before running the script, you need to manually create the S3 bucket where we will upload the files.
    To do this, we will use the AWS console.

    Steps to create an S3 bucket:
    1. Access the AWS console:
        Go to the AWS Management Console and log in with your credentials.
    2. Select S3 after typing it into the search bar:
        From the services panel, select "S3" under the "Storage" section.
    3. Create a new bucket:
        Click on "Create bucket".
        Enter a unique name for your bucket.
        Select the AWS region where you want to create the bucket.
        Leave the other settings at their default values, unless you have specific requirements
        (such as versioning, encryption, etc.).
        Click on "Create bucket".

    Once the bucket is created, you can proceed with running the Python script locally to upload
    the CSV files to the S3 bucket.

"""

"""
    ITALIANO AIUTO!
    Prima di eseguire lo script, bisogna creare manualmente il bucket S3 sul quale caricheremo i file,
    per farlo andremo a utilizzare la console AWS.

    Passaggi per creare un bucket S3:
    1. Accedi alla console AWS
        Vai alla console di gestione AWS e accedi con le tue credenziali.
    2. Selezione S3 dopo averlo digitato nella barra di ricerca:
        Dal pannello dei servizi, seleziona "S3" sotto la sezione "Storage".
    3. Crea un nuovo bucket:
        Clicca su "Create bucket".
        Inserisci un nome univoco per il tuo bucket.
        Seleziona la regione AWS in cui vuoi creare il bucket.
        Lascia le altre impostazioni ai loro valori predefiniti, a meno che tu non abbia esigenze specifiche
        (come versioning, crittografia, ecc.).
        Clicca su "Create bucket".

    Una volta creato il bucket, puoi procedere con l'esecuzione dello script Python in locale per caricare
    i file CSV nel bucket S3.
"""

# THIS SCRIPT SHOULD BE RUN LOCALLY AND IS USED TO UPLOAD THE FILES WE START WITH

import boto3
import os

# region where the bucket has been created
region = "eu-west-3"
# credential of the user created with the AWS console.
aws_access_key_id = "AKIAW3MD6URL73DJ6BNI"
aws_secret_access_key = "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"

# istanciate a client s3 with the credential to gain access
s3_client = boto3.client("s3",
                         region_name=region,
                         aws_access_key_id=aws_access_key_id,
                         aws_secret_access_key=aws_secret_access_key
                         )

bucket_name = 'raw3'
files = ['BTC-EUR-Historical-Data.csv',
         'google-trend-bitcoin.csv',
         'XMR-EUR-Kraken-Historical-Data.csv',
         'google-trend-monero.csv']


# check current path
print(f"Percorso corrente: {os.getcwd()}")

print(f"\n\nCaricamento dei file nel bucket {bucket_name}:")
# Upload dei file into the bucket specified
for file in files:
    # check file existence
    if os.path.isfile(file):
        s3_client.upload_file(file, bucket_name, f'{file}')
        print(f"File '{file}' caricato con successo.")
    else:
        print(f"File '{file}' non trovato. Assicurati che sia nel percorso corretto.")
