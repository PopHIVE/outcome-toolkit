import json
from flask import jsonify, Flask, g
from typing import Tuple, Dict, Any
from app.utilities.loggerfactory import LoggerFactory
from app.ext.exceptions.errors import (
    InvalidMID,
    InvalidOutcome,
    InvalidGeography,
    InvalidMetric,
    InvalidDatetime,
    InvalidColumn,
)
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException


logger = LoggerFactory.getLogger(__name__, log_level='DEBUG')


def add_error_handlers(app: Flask) -> None:
    """Register Error Handlers. Modifies the provided app."""

    app.register_error_handler(ValidationError, handle_generic_validation_error)
    app.register_error_handler(InvalidGeography, handle_invalid_geography_exception)
    app.register_error_handler(InvalidMID, handle_invalid_mid_exception)
    app.register_error_handler(InvalidOutcome, handle_invalid_outcome_exception)
    app.register_error_handler(InvalidMetric, handle_invalid_metric_exception)
    app.register_error_handler(InvalidDatetime, handle_invalid_datetime_exception)
    app.register_error_handler(HTTPException, handle_generic_http_exception)
    app.register_error_handler(InvalidColumn, handle_generic_invalid_column_exception)


def handle_generic_validation_error(e: ValidationError) -> Tuple[Dict[str, Any], int]:
    """This function executes whenever the app raises a ValidationError."""

    response = {
        'message': json.loads(e.json()),
        'description': 'Unprocessable entity.',
        'request_id': g.request_id,
    }
    logger.error(f'Generic Validation Error  <{g.request_id}>')
    return jsonify(response), 422


def handle_invalid_geography_exception(
    e: InvalidGeography,
) -> Tuple[Dict[str, Any], int]:
    """This function executes whenever the app raises a InvalidGeography."""

    response = {
        # 'outcome': e.geography,
        'message': e.message,
        'description': 'Unprocessable entity.',
        'request_id': g.request_id,
    }
    logger.error(f'Invalid Geography Provided ({e.geography} <-> c.422)! <{g.request_id}>')
    return jsonify(response), 422


def handle_invalid_mid_exception(e: InvalidMID) -> Tuple[Dict[str, Any], int]:
    """This function executes whenever the app raises a InvalidMID."""

    response = {
        # 'mid': e.mid,
        'message': e.message,
        'description': 'Unprocessable entity.',
        'request_id': g.request_id,
    }
    logger.error(f'Invalid MID Provided ({e.mid} <-> c.422)! <{g.request_id}>')
    return jsonify(response), 422


def handle_invalid_outcome_exception(e: InvalidOutcome) -> Tuple[Dict[str, Any], int]:
    """This function executes whenever the app raises a InvalidOutcome."""

    response = {
        # 'outcome': e.outcome,
        'message': e.message,
        'description': 'Unprocessable entity.',
        'request_id': g.request_id,
    }
    logger.error(f'Invalid Outcome Provided ({e.outcome} <-> c.422)! <{g.request_id}>')
    return jsonify(response), 422


def handle_invalid_metric_exception(e: InvalidMetric) -> Tuple[Dict[str, Any], int]:
    """This function executes whenever the app raises a InvalidMetric."""

    response = {
        # 'metric': e.metric,
        'message': e.message,
        'description': 'Unprocessable entity.',
        'request_id': g.request_id,
    }
    logger.error(f'Invalid Metric Provided ({e.metric} <-> c.422)! <{g.request_id}>')
    return jsonify(response), 422


def handle_invalid_datetime_exception(e: InvalidDatetime) -> Tuple[Dict[str, Any], int]:
    """This function executes whenever the app raises a InvalidDatetime."""

    response = {
        # 'datetime_str': e.datetime_str,
        'message': e.message,
        'description': 'Unprocessable entity.',
        'request_id': g.request_id,
    }
    logger.error(f'Invalid DateTime Provided ({e.datetime_str} <-> c.422)! <{g.request_id}>')
    return jsonify(response), 422


def handle_generic_http_exception(e: HTTPException):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps(
        {
            'code': e.code,
            'name': e.name,
            'description': e.description,
        }
    )
    response.content_type = 'application/json'
    return response


def handle_generic_invalid_column_exception(e: InvalidColumn):
    """This function executes whenever the app raises a InvalidColumn."""

    response = {
        'message': e.message,
        'description': 'Unprocessable entity.',
        'request_id': g.request_id,
    }
    logger.error(f'Invalid Value Provided. {e.provided_value}')
    return jsonify(response), 422
