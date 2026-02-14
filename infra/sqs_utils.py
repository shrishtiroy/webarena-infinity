"""SQS helper functions: send, receive, delete messages with JSON payloads."""

from __future__ import annotations

import json
import logging
from typing import Any

import boto3

from config import AWS_REGION, SQS_WAIT_TIME

log = logging.getLogger(__name__)

_client = None


def _sqs():
    """Lazy-initialised SQS client (created once per process)."""
    global _client
    if _client is None:
        _client = boto3.client("sqs", region_name=AWS_REGION)
    return _client


def send_message(queue_url: str, body: dict[str, Any]) -> str:
    """Send a JSON message to *queue_url*.  Returns the SQS message ID."""
    resp = _sqs().send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(body),
    )
    msg_id = resp["MessageId"]
    log.debug("sent %s → %s", msg_id, queue_url.rsplit("/", 1)[-1])
    return msg_id


def receive_message(
    queue_url: str,
    visibility_timeout: int = 3600,
    wait_time: int = SQS_WAIT_TIME,
) -> tuple[dict[str, Any], str] | None:
    """Long-poll for one message.

    Returns ``(parsed_body, receipt_handle)`` or *None* if nothing arrived
    within *wait_time* seconds.
    """
    resp = _sqs().receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=wait_time,
        VisibilityTimeout=visibility_timeout,
    )
    messages = resp.get("Messages", [])
    if not messages:
        return None
    msg = messages[0]
    body = json.loads(msg["Body"])
    return body, msg["ReceiptHandle"]


def delete_message(queue_url: str, receipt_handle: str) -> None:
    """Delete a message after successful processing."""
    _sqs().delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle,
    )
    log.debug("deleted message from %s", queue_url.rsplit("/", 1)[-1])


def get_queue_attributes(queue_url: str) -> dict[str, str]:
    """Return approximate message counts for monitoring."""
    resp = _sqs().get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=[
            "ApproximateNumberOfMessages",
            "ApproximateNumberOfMessagesNotVisible",
        ],
    )
    return resp.get("Attributes", {})
