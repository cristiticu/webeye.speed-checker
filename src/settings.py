from dotenv import load_dotenv
import os

load_dotenv('.env')

ENVIRONMENT = os.environ.get('ENVIRONMENT')
AWS_REGION = os.environ.get('AWS_REGION', '')

DYNAMODB_URL_OVERRIDE = os.environ.get('DYNAMODB_URL_OVERRIDE')
TABLE_PREFIX = os.environ.get(
    'TABLE_PREFIX') or "production" if ENVIRONMENT == "production" else "stage"
DOWNTIMES_TABLE_REGION = "eu-central-1"
DOWNTIMES_TABLE_NAME = "webeye.downtimes"
DOWNTIMES_METATYPE_LSI = "metatype-lsi"
