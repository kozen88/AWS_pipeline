"""
    ENGLISH HELP

    Create a State Machine in AWS Step Functions:

    1. Access the AWS console
    2. Type Step Function in the search bar
    3. Select Step Function
    4. On the initial page, click on Get started at the top right
    5. Close the pop-up with the offered instructions for creating a step function
    6. On the top bar of the step function creation page, there are 3 options:
        - Design
        - Code
        - Configuration
    7. Click on Code
    8. Paste the JSON below in place of the default one
    9. Click on Create
    10. Proceed with the confirmations


    ITALIANO AIUTO

    Creare una State Machine in AWS Step Functions:

    1. Accedere alla console di AWS
    2. digita Step function nella barra di ricerca
    3. seleziona Step Function
    4. nella pagina iniziale cliccare su inizia in alto a destra
    5. chiudere il pop up con le indicazioni offerte per la creazione di una step function
    6. Nella top bar della pagina di creazione della step fuction ci sono le 3 opzioni
        - Progettazione
        - Codice
        - Configurazione
    7. cliccare su Codice
    8. Incollare il sottostante json al posto di quello di default
    9. clicca su crea
    10. proseguire con le conferme



JSON TO DEFINE STATE MACHINE ON AWS

{
  "Comment": "Pipeline ETL per dati Bitcoin e Monero",
  "StartAt": "RawToSilver",
  "States": {
    "RawToSilver": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "RawToSilverJob"
      },
      "Next": "SilverToGold",
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Next": "Fail",
          "Comment": "get all errors on T1"
        }
      ]
    },
    "SilverToGold": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "SilverToGoldJob"
      },
      "Next": "LoadToRedshift",
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Comment": "get all errors on T2",
          "Next": "Fail"
        }
      ]
    },
    "LoadToRedshift": {
      "Type": "Task",
      "Resource": "arn:aws:states:::glue:startJobRun.sync",
      "Parameters": {
        "JobName": "LoadToRedshiftJob"
      },
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "Next": "Fail",
          "Comment": "get all errors on Load"
        }
      ],
      "End": true
    },
    "Fail": {
      "Type": "Fail"
    }
  }
}

"""


"""
    ENGLISH NOTE:
    
    In the provided JSON code, I used the following names for the AWS Glue jobs:
    
    RawToSilverJob: for the job that transforms data from raw to silver.
    SilverToGoldJob: for the job that transforms data from silver to gold.
    LoadToRedshiftJob: for the job that loads the gold data into the Redshift data warehouse.
    So, when you create your AWS Glue jobs, use these names:
    
    T1: RawToSilverJob
    T2: SilverToGoldJob
    Load: LoadToRedshiftJob
"""
"""
   ITALINO NOTE:
   
    Nel codice JSON fornito, ho usato i seguenti nomi per i job AWS Glue:
    
    RawToSilverJob: per il job che trasforma i dati da raw a silver.
    SilverToGoldJob: per il job che trasforma i dati da silver a gold.
    LoadToRedshiftJob: per il job che carica i dati gold nel data warehouse Redshift.
    Quindi, quando crei i tuoi job AWS Glue, utilizza questi nomi:
    
    T1: RawToSilverJob
    T2: SilverToGoldJob
    Load: LoadToRedshiftJob
"""