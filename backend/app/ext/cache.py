from flask import request
from flask_caching import Cache
from app.utilities.loggerfactory import LoggerFactory


logger = LoggerFactory.getLogger(__name__, log_level='DEBUG')

# Initialize Cache Object
# (in separate file to avoid circular imports)
cache = Cache()


def make_properties_key() -> str:
    """Generate Cache Key For Hashing Properties Requests."""

    mids = sorted(request.json.get('mids', []))
    return ':'.join(mids) + f'({request.path})'


def make_details_key() -> str:
    """Generate Cache Key For Hashing Details Requests."""
    outcome = request.args.get('outcome', '')
    mids = sorted(request.json.get('mids', []))
    metrics = sorted(request.json.get('metrics', []))
    aggregate = request.json.get('aggregate', False)

    return f"<{outcome}><{':'.join(mids)}><{':'.join(metrics)}><{aggregate}>"


def make_trendlines_key() -> str:
    """Generate Cache Key For Hashing Trendline Requests."""
    outcome = request.json.get('outcome')
    metrics = sorted(request.json.get('metrics', []))

    return f"<{outcome}><{':'.join(metrics)}>"
