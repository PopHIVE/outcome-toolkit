import pytest
from app.db.database import db_session
from db.datasets.geoms.geoms_tables import CBGeom, CBGeomIndex, AdjacencyEdgeList
from db.datasets.alcohol.alcohol_tables import NEMSISAlcohol_v2
from db.datasets.opioid.opioid_tables import NEMSISOpioid_v2
from db.datasets.demographics.demographics_tables import CBDemographics
from db.datasets.ascvd.ascvd_tables import ASCVDScore_v2
from db.datasets.soc.soc_tables import RawSOCData, AggregatedSOCV1, AggregatedSOCV2


@pytest.mark.cicd
def test_geoms_table():
    """Test that the GEOMS Table has the correct number of Rows."""
    assert db_session.query(CBGeom).count() == 37_977, 'Unexpected Number of Rows'


@pytest.mark.cicd
def test_geoms_index_table():
    """Test that the GEOMS Index has the correct number of Rows."""
    assert db_session.query(CBGeomIndex).count() == 47_863, 'Unexpected Number of Rows'


@pytest.mark.cicd
def test_demographics_table():
    """Test that the Demographics Table has the correct number of Rows."""
    assert db_session.query(CBDemographics).count() == 37_977, 'Unexpected Number of Rows'


@pytest.mark.cicd
def test_ascvd_score_table():
    """Test that the ASCVD Scores Table has the correct number of Rows."""
    # Changing to a greater than since moving forward we should always have more than these rows
    assert db_session.query(ASCVDScore_v2).count() > 37_978, 'Unexpected Number of Rows'


@pytest.mark.cicd
def test_adjacency_table():
    """Test that the Adjacency Table has the correct number of Rows."""
    assert db_session.query(AdjacencyEdgeList).count() > 223_000, 'Unexpected Number of Rows'


@pytest.mark.cicd
def test_raw_soc_table():
    """Test that the Raw SOC Table has the correct number of Rows."""
    assert db_session.query(RawSOCData).count() > 0, 'Unexpected Number of Rows'


@pytest.mark.cicd
def test_aggregate_soc_table():
    """Test that the Aggregate SOC Table has the correct number of Rows."""
    assert db_session.query(AggregatedSOCV2).count() > 0, 'Unexpected Number of Rows'

@pytest.mark.cicd
def test_nemsis_opioid_table():
    """Test that the NEMSIS Opioid Table has the correct number of Rows."""
    # Changing to a greater than since moving forward we should always have more than these rows
    assert db_session.query(NEMSISOpioid_v2).count() > 41_113, 'Unexpected Number of Rows'


@pytest.mark.cicd
def test_nemsis_alcohol_table():
    """Test that the NEMSIS Alcohol Table has the correct number of Rows."""
    # Changing to a greater than since moving forward we should always have more than these rows
    assert db_session.query(NEMSISAlcohol_v2).count() > 41_113, 'Unexpected Number of Rows'
