# ERDDAP Tools

This package aims to offer tools and additional features for those supporting
ERDDAP instances

## ERDDAP Server Management API

The file `app.py` contains a Flask application that offers
endpoints for managing your ERDDAP datasets. At the moment,
the following endpoints are offered

    POST /update-dataset

    Authentication: Bearer API-KEY

    BODY:
    {
        "id": "datasetID",
        "xml": "VALID XML FOR INSIDE A <dataset> tag",
        "is_active": true | false [optional, omit to not change the status]
    }


    POST /create-dataset

    Authentication: Bearer API-KEY

    BODY:
    {
        "id": "datasetID",
        "type": "VALID TYPE ATTRIBUTE FOR <dataset>",
        "xml": "VALID XML FOR INSIDE A <dataset> tag",
        "is_active": true | false [optional, defaults to true]
    }


    POST /deactivate-dataset

    Authentication: Bearer API-KEY

    BODY:
    {
        "id": "datasetID"
    }
 


    POST /activate-dataset

    Authentication: Bearer API-KEY

    BODY:
    {
        "id": "datasetID"
    }


## Command Line Interface

The four endpoints also have command-line components:

    # Specify only one of --active or --inactive, or neither to not change it.
    python cli.py update --active --inactive DATASET_ID DATASET_XML_FILE

    python cli.py create --active --inactive DATASET_TYPE DATASET_ID DATASET_XML_FILE

    python cli.py deactivate DATASET_ID
    python cli.py activate DATASET_ID


## API KEY Management

Access via the API keys is done using API keys. Use the command line to generate and manage these

     # Create a key named SHORT_NAME with accompanying description that expires in 52 weeks.
     > python cli.py keys generate --expiry-weeks=52 SHORT_NAME "DESCRIPTION"
     > New API key: SHORT_NAME.secure_key
     > Key generated
     # Save the API key displayed above, as it cannot be retrieved after the fact.

     # Rotates an API key. This tells it to stop accepting the old key after X weeks and start 
     # accept the new key immediately. This allows you to update key on the server without disruptions.
     python cli.py keys rotate SHORT_NAME --expiry-weeks=52 --old-expiry-weeks=2

     # Immediately expires an API key.
     python cli.py keys expire SHORT_NAME
