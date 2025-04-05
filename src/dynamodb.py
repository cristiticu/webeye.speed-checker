import boto3
import settings


def dynamodb_table(table_name: str, region: str):
    dynamodb = boto3.resource(
        'dynamodb', region_name=region, endpoint_url=settings.DYNAMODB_URL_OVERRIDE)
    return dynamodb.Table(f"{settings.TABLE_PREFIX}.{table_name}")
