"""Attachment bytes in S3-compatible object storage (RustFS in Compose), path-style with SigV4."""

import asyncio
import os
from functools import cache
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


@cache
def _client() -> Any:
    return boto3.client(
        "s3",
        endpoint_url=os.environ["S3_ENDPOINT"],
        aws_access_key_id=os.environ["S3_ACCESS_KEY"],
        aws_secret_access_key=os.environ["S3_SECRET_KEY"],
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"),
    )


def _bucket() -> str:
    return os.environ.get("S3_BUCKET", "attachments")


def _put(key: str, data: bytes, content_type: str) -> None:
    client = _client()
    try:
        client.put_object(Bucket=_bucket(), Key=key, Body=data, ContentType=content_type)
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") != "NoSuchBucket":
            raise
        # Created on first use rather than at startup, so the API starts while storage is down.
        client.create_bucket(Bucket=_bucket())
        client.put_object(Bucket=_bucket(), Key=key, Body=data, ContentType=content_type)


def _get(key: str) -> bytes:
    body: bytes = _client().get_object(Bucket=_bucket(), Key=key)["Body"].read()
    return body


async def put(key: str, data: bytes, content_type: str) -> None:
    await asyncio.to_thread(_put, key, data, content_type)


async def get(key: str) -> bytes:
    return await asyncio.to_thread(_get, key)
