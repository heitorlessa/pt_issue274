import json
import boto3

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from botocore.exceptions import ClientError


# https://awslabs.github.io/aws-lambda-powertools-python/#features
tracer = Tracer()
logger = Logger()
session = boto3.Session()


@tracer.capture_method
def raise_non_boto_exception(event):
    """ Fail if ?fail query string is set """
    params = event.query_string_parameters
    if params is not None and params.get("fail"):
        raise ValueError("fail query string set....failing conditionally")

    return True


@tracer.capture_method
def create_client_error_exception():
    ssm = session.client("ssm")
    ssm.get_parameter(Name="do_not_exist")


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    event: APIGatewayProxyEvent = APIGatewayProxyEvent(event)
    try:
        # Cause a ClientError to trigger aws_error_handler to record an exception handled or not
        # https://github.com/aws/aws-xray-sdk-python/blob/508f929fee495710656c0c1478f8873a2e9e5666/aws_xray_sdk/ext/boto_utils.py#L73
        create_client_error_exception()

        return {"statusCode": 200, "body": json.dumps({"message": "All good"})}
    except ValueError:  #
        logger.info("Conditionally failed... we're gonna catch that!")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Non-Boto exception caught correctly"}),
        }
    except ClientError:
        logger.exception("Handling boto exception")
        raise_non_boto_exception(event)  # raise only if ?fail query string is set

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Boto exception caught correctly"}),
        }
