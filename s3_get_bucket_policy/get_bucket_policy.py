#!/usr/bin/env python3
import boto3
import argparse

parser = argparse.ArgumentParser(description="Prints the bucket policy for an S3 bucket on MSI.")
parser.add_argument("bucket", help=("The name of the s3 bucket to get the policy from." " Do not include the 's3://' prefix."))
parser.add_argument("aws_key", help=("Your S3 access key." " See https://www.msi.umn.edu/content/second-tier-storage"))
parser.add_argument("aws_secret", help=("Your S3 secret key." " See https://www.msi.umn.edu/content/second-tier-storage"))
args = parser.parse_args()

# Retrieve the policy of the specified bucket
session = boto3.Session()
s3host = 'https://s3.msi.umn.edu'
s3client = session.client(service_name='s3',
                            endpoint_url=s3host,
                            aws_access_key_id=args.aws_key,
                            aws_secret_access_key=args.aws_secret)

result = s3client.get_bucket_policy(Bucket=args.bucket)
print(result['Policy'])