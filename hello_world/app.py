import json

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent

# https://awslabs.github.io/aws-lambda-powertools-python/#features
tracer = Tracer()
logger = Logger()

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    event: APIGatewayProxyEvent = APIGatewayProxyEvent(event)
    try:
        params = event.query_string_parameters
        logger.info(params)
        if params is not None and params.get("fail"):
            raise ValueError("fail query string set....failing conditionally")
        
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "All good"})
        }
    except ValueError: #
        logger.info("Conditionally failed... we're gonna catch that!")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Caught exception..."})
        }
