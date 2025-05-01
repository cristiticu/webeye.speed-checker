import boto3
import settings


def s3_bucket(bucket_name: str, region: str):
    bucket = boto3.resource("s3", region_name=region)
    return bucket.Bucket(f"{settings.BUCKET_PREFIX}.{bucket_name}")
