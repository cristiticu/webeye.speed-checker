import boto3
import settings


def dynamodb_table(table_name: str):
    dynamodb = boto3.resource(
        'dynamodb', region_name=settings.DOWNTIMES_TABLE_REGION, endpoint_url=settings.DYNAMODB_URL_OVERRIDE)
    return dynamodb.Table(f"{settings.TABLE_PREFIX}.{table_name}")
