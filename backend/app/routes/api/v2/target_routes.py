from app.ext.cache import cache

from flask import Blueprint, jsonify
from sqlalchemy.orm import Session
from app.db.database import db_session


# Import tables directly to avoid circular imports
from db.datasets.target_payouts.target_payout_tables import TargetPayoutRate

bp = Blueprint('target', __name__)

@bp.route('/targets', methods=['GET'])
@cache.cached(query_string=True)
def get_all_targets():
    """Get all target payout rates (static for all projects)"""
    try:
        session: Session = db_session()
        
        targets = session.query(TargetPayoutRate).all()
        
        targets_data = []
        for target in targets:
            targets_data.append({
                "outcome": target.outcome.value,
                "period": target.period.value,
                "minimum_payout": target.minimum_payout,
                "maximum_payout": target.maximum_payout,
                "target_rate": target.target_rate
            })
        
        return jsonify({"targets": targets_data}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
