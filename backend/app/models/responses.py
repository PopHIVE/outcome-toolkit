from enum import Enum
import gzip
import shapely.wkt
from typing import Union, List, Set, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, validator, EmailStr
from sqlalchemy.engine import Row
from flask import make_response, json, Response
from app.utilities.serialize import serialize_row, format_time_interval
from app.configs.consts import ValidCharacteristics, ValidOutcomes
from app.configs.settings import GeometrySettings
from db.datasets.core import Area
from geojson import Feature, FeatureCollection
from datetime import date, datetime
from collections import OrderedDict
from app.models.common import OutcomesEnum, ProjectPerformerType, UserRole, PayoutPeriod

import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)


class ResponseBase(BaseModel):
    """Base Pydantic Model for Responses. Includes helper functions for serialization."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_json(self) -> Dict[str, Any]:
        """Return a dictionary of the Model."""
        def enum_to_str(obj):
            if isinstance(obj, Enum):
                return obj.value
            return obj

        data = self.model_dump(by_alias=True)
        return json.loads(json.dumps(data, default=enum_to_str))

    def to_json_str(self) -> str:
        """Return the JSON dumps as a string."""

        return json.dumps(self.to_json(), sort_keys=False)

    def to_compressed_json(self, compressionlevel: int = 9) -> bytes:
        """GZIP Compress JSON to bytes."""

        content = self.to_json_str()
        gzipped_content = gzip.compress(content.encode('utf8'), compressionlevel)
        return gzipped_content

    def to_response(self, compress=True, compressionlevel: int = 9, status_code: int = 200) -> Response:
        """Generate a Wrapped Flask Response. Allow compression options."""

        if compress:
            content = self.to_compressed_json(compressionlevel)
            response = make_response(content, status_code)
            response.headers['Content-length'] = len(content)
            response.headers['Content-Encoding'] = 'gzip'
        else:
            content = self.to_json_str()
            response = make_response(content, status_code)

        return response
    
class AreaBase(BaseModel):
    mid: str
    type: str
    
    model_config = {
        "from_attributes": True
    }


class ProjectBase(BaseModel):
    id: str
    project_name: str
    performer_type: ProjectPerformerType
    performance_period_from: date
    performance_period_to: date
    outcome: OutcomesEnum

    model_config = {
        "from_attributes": True
    }

class UserBase(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    organization: str
    role: UserRole

    model_config = {
        "from_attributes": True
    }


class UserResponse(UserBase, ResponseBase):
    projects: List[ProjectBase] 


class SendEmailResponse(ResponseBase):
    message: str

class ProjectMeasurementBase(BaseModel):
    period: PayoutPeriod
    date_of_payout: date
    actual_payout: float
    project_metric: float
    national_metric: float

    model_config = {
        "from_attributes": True
    }

class TargetPayoutRateBase(BaseModel):
    outcome: OutcomesEnum
    period: PayoutPeriod
    minimum_payout: float
    maximum_payout: float
    target_rate: float

    model_config = {
        "from_attributes": True
    }

class ProjectResponse(ProjectBase, ResponseBase):
    users: List[UserBase]
    project_measurements: List[ProjectMeasurementBase]  
    areas: List[AreaBase]

class MidMetricBase(BaseModel):
    mid: str
    metric: float

    model_config = {
        "from_attributes": True
    }


class ProjectBaseRequest(BaseModel):
    project_id: str

class TargetPayoutResponse(ResponseBase):
    outcome: OutcomesEnum
    period: PayoutPeriod
    minimum_payout: float
    maximum_payout: float
    target_rate: float

    model_config = {
        "from_attributes": True
    }

# New response for getting all targets
class AllTargetsResponse(ResponseBase):
    targets: List[TargetPayoutRateBase]

class LogoutResponse(ResponseBase):
    message: str

class ErrorResponse(ResponseBase):
    error: str

class HTMLResponse(ResponseBase):
    html_text: Optional[str] = None

class DataBundle(BaseModel):
    """V1 Format Data Bundle. The Core object that wraps a row column value."""

    display_name: Optional[str] = None
    label: Optional[str] = None
    metric: Optional[str] = None
    value: Optional[Union[float, int, str]] = None

    @validator('value', pre=True)
    def parse_value(cls, v: Any) -> Any:
        if isinstance(v, datetime):
            return v.strftime('%Y-%m-%dT%H:%M:%SZ')
        return v


class StandardDataBundleCollection(ResponseBase):
    """V1 Format For responses."""

    metadata: Dict[str, Union[str, int, datetime]] = Field(
        serialization_alias=ValidCharacteristics.METADATA, default_factory=dict
    )
    geometry: Dict[str, Union[str, int]] = Field(
        serialization_alias=ValidCharacteristics.GEOMETRY, default_factory=dict
    )
    age: List[DataBundle] = Field(serialization_alias=ValidCharacteristics.AGE, default_factory=list)
    sex: List[DataBundle] = Field(serialization_alias=ValidCharacteristics.SEX, default_factory=list)
    race: List[DataBundle] = Field(serialization_alias=ValidCharacteristics.RACE, default_factory=list)
    rurality: List[DataBundle] = Field(serialization_alias=ValidCharacteristics.RURALITY, default_factory=list)
    general: List[DataBundle] = Field(serialization_alias=ValidCharacteristics.GENERAL, default_factory=list)
    income: List[DataBundle] = Field(serialization_alias=ValidCharacteristics.INCOME, default_factory=list)
    age_p_sex: List[DataBundle] = Field(serialization_alias=ValidCharacteristics.AGE_P_SEX, default_factory=list)

    def __getitem__(self, item) -> Any:
        if item == ValidCharacteristics.METADATA:
            return self.metadata
        if item == ValidCharacteristics.GEOMETRY:
            return self.geometry
        if item == ValidCharacteristics.AGE:
            return self.age
        if item == ValidCharacteristics.SEX:
            return self.sex
        if item == ValidCharacteristics.RACE:
            return self.race
        if item == ValidCharacteristics.RURALITY:
            return self.rurality
        if item == ValidCharacteristics.GENERAL:
            return self.general
        if item == ValidCharacteristics.INCOME:
            return self.income
        if item == ValidCharacteristics.AGE_P_SEX:
            return self.age_p_sex

        return getattr(self, item)

    def add_row(self, row: Row, mappings: Dict[str, str]) -> None:
        """Add row to the response. Mappings is the Data Dictionary Mappings to wrap
        the values into the Data Bundles.

        """

        srow = serialize_row(row)

        for col, value in srow.items():
            if mappings[col]['include'].lower()[0] == 'n':
                continue

            characteristic = mappings[col]['characteristic']
            data_bundle = DataBundle(
                value=value,
                label=mappings[col]['label'],
                metric=mappings[col]['metric'],
                display_name=mappings[col]['display_name'],
            )

            if characteristic == ValidCharacteristics.METADATA:
                self.metadata[data_bundle.label] = value
            elif characteristic == ValidCharacteristics.GEOMETRY:
                self.geometry[data_bundle.label] = value
            else:
                self[characteristic].append(data_bundle)


class IntersectionsV1(ResponseBase):
    """V1 Response Format for Intersections."""

    state: Set[str] = Field(default_factory=set)
    county: Set[str] = Field(default_factory=set)
    zcta3: Set[str] = Field(default_factory=set)
    zcta5: Set[str] = Field(default_factory=set)

    def add_area(self, area: Area) -> None:
        """Add Area to the intersections."""

        for intersection in area.intersections:
            if intersection.state_mid is not None:
                self.state.add(intersection.state_mid)
            if intersection.county_mid is not None:
                self.county.add(intersection.county_mid)
            if intersection.zcta3_mid is not None:
                self.zcta3.add(intersection.zcta3_mid)
            if intersection.zcta5_mid is not None:
                self.zcta5.add(intersection.zcta5_mid)

    def to_json(self) -> Dict[str, Any]:
        payload = {
            'STATE': list(self.state),
            'COUNTY': list(self.county),
            'ZCTA3': list(self.zcta3),
            'ZCTA5': list(self.zcta5),
        }
        return payload


class StandardV1DataKindBundle(BaseModel):
    """V1 Standard Properties Response Format at the MID Key Level."""

    demographics: StandardDataBundleCollection = Field(default_factory=StandardDataBundleCollection)
    acs_estimates: StandardDataBundleCollection = Field(default_factory=StandardDataBundleCollection)
    soc: StandardDataBundleCollection = Field(default_factory=StandardDataBundleCollection)
    opioid: StandardDataBundleCollection = Field(default_factory=StandardDataBundleCollection)
    alcohol: StandardDataBundleCollection = Field(default_factory=StandardDataBundleCollection)
    ascvd_scores: StandardDataBundleCollection = Field(default_factory=StandardDataBundleCollection)
    adjacency: List[str] = Field(default_factory=list)
    intersections: IntersectionsV1 = Field(default_factory=IntersectionsV1)
    metadata: Dict[str, Union[str, int]] = Field(default_factory=dict)
    geometry: Dict[str, Union[str, int]] = Field(default_factory=dict)

    def to_json(self) -> Dict[str, Any]:
        payload = {
            'demographics': self.demographics.to_json(),
            'acs_estimates': self.acs_estimates.to_json(),
            'soc': self.soc.to_json(),
            'opioid': self.opioid.to_json(),
            'alcohol': self.alcohol.to_json(),
            'cardio': self.ascvd_scores.to_json(),
            'adjacency': self.adjacency,
            'intersections': self.intersections.to_json(),
        }
        # TO DO: Deprecate These Fields Or Update Models
        payload['metadata'] = payload['demographics']['metadata']
        payload['geometry'] = payload['demographics']['geometry']
        return payload


class StandardV1Response(ResponseBase):
    """V1 Standard Properties Response Format."""

    data: Dict[str, StandardV1DataKindBundle] = Field(default_factory=dict)

    def __getitem__(self, area: Area) -> Any:
        return self.data[area.mid]

    def add_area(self, area: Area) -> Any:
        self.data[area.mid] = StandardV1DataKindBundle()

    def to_json(self) -> Dict[str, Any]:
        payload = {}
        for mid, bundle in self.data.items():
            payload[mid] = bundle.to_json()

        return payload


class GeoJSONResponse(ResponseBase):
    """V1 GeoJSON Response Format."""

    tolerance: float = GeometrySettings.GEOMETRY_TOLERANCE
    features: List[Feature] = Field(default_factory=list)

    @property
    def feature_collection(self) -> FeatureCollection:
        return FeatureCollection(self.features)

    def add_area(self, area: Area) -> None:
        """Add Area to the GeoJSON response."""

        geom = shapely.wkt.loads(area.geoms.geometry)

        if self.tolerance is not None:
            geom = geom.simplify(tolerance=self.tolerance)

        feature = Feature(
            id=area.geoms.geoid,
            geometry=geom,
            properties={
                'mid': area.mid,
                'state_usps': list(set([i.state_usps for i in area.intersections])),
            },
        )
        self.features.append(feature)

    def to_json(self) -> Dict[str, Any]:
        return dict(self.feature_collection)


class DetailsResponseV2(ResponseBase):
    data: Dict[str, Any] = Field(default_factory=OrderedDict)

    def add_value(
        self,
        mid: str,
        metric: str,
        start_date: datetime,
        end_date: datetime,
        value: Any,
        bin_rank: Any = None,
    ) -> None:
        if mid not in self.data:
            self.data[mid] = OrderedDict()

        if metric not in self.data[mid]:
            self.data[mid][metric] = OrderedDict()

        self.data[mid][metric][format_time_interval(start_date, end_date)] = {
            'value': value,
            'bin_rank': bin_rank,
        }

    def to_json(self) -> Dict[str, Any]:
        return self.data
    
class DataDetailsResponse(ResponseBase):
    data: Dict[str, Any] = Field(default_factory=OrderedDict)

    def add_value(
        self,
        outcome: str,
        earliest_date: datetime,
        latest_date: datetime,
        data_release: datetime,
    ) -> None:
        self.data[outcome] = OrderedDict({
            'earliest_date': earliest_date,
            'latest_date': latest_date,
            'data_release': data_release,
        })
    
    def to_json(self) -> Dict[str, Any]:
        return self.data


class BinsResponseV2(ResponseBase):
    data: Dict[str, Any] = Field(default_factory=OrderedDict)

    def add_value(
        self,
        outcome: str,
        metric: str,
        start_date: datetime,
        end_date: datetime,
        bin_stats: Dict[str, Any],
    ) -> None:
        time_interval = format_time_interval(start_date, end_date)

        if outcome not in self.data:
            self.data[outcome] = OrderedDict()

        if metric not in self.data[outcome]:
            self.data[outcome][metric] = OrderedDict()

        if time_interval not in self.data[outcome][metric]:
            self.data[outcome][metric][time_interval] = []

        self.data[outcome][metric][time_interval].append(bin_stats)

    def to_json(self) -> Dict[str, Any]:
        return self.data


class OverviewResponseV2(ResponseBase):
    data: Dict[str, Any] = Field(default_factory=OrderedDict)

    def add_value(self, mid: str, bin_rank: Any) -> None:
        self.data[mid] = bin_rank

    def to_json(self) -> Dict[str, Any]:
        return self.data


class DemographicsResponse(ResponseBase):
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            'source': '',
            'demographic_categories': {},
            'display_names': {},
        }
    )
    data: Dict[str, Dict[str, Union[float, str, List[str]]]] = Field(default_factory=OrderedDict)

    def add_value(self, mid: str, col_name: str, value: Any):
        if mid not in self.data:
            self.data[mid] = {}

        assert col_name not in self.data[mid], 'collison'

        self.data[mid][col_name] = value

    def add_adjacency_value(self, mid: str, value: str):
        if mid not in self.data:
            self.data[mid] = {}

        if 'adjacency' not in self.data[mid].keys():
            self.data[mid]['adjacency'] = []

        self.data[mid]['adjacency'].append(value)

    def add_intersections_value(self, mid: str, type_: str, other_mid: str):

        if mid not in self.data:
            self.data[mid] = {}

        if 'intersections' not in self.data[mid].keys():
            self.data[mid]['intersections'] = {}
        
        if type_ not in self.data[mid]['intersections'].keys():
            self.data[mid]['intersections'][type_] = []
        
        self.data[mid]['intersections'][type_].append(other_mid)


    def add_source(self, source: str):
        self.metadata['source'] = source

    def add_demographic_category(self, col: str, category: str):
        if category not in self.metadata['demographic_categories']:
            self.metadata['demographic_categories'][category] = {'bands': []}
        self.metadata['demographic_categories'][category]['bands'].append(col)

    def add_display_name(self, col: str, display_name: str):
        self.metadata['display_names'][col] = display_name

    def to_json(self) -> Dict[str, Any]:
        return {'metadata': self.metadata, 'data': self.data}


class TrendlinesResponseV2(ResponseBase):
    data: Dict[str, Any] = Field(default_factory=OrderedDict)

    def add_value(self, metric: str, start_date: datetime, end_date: datetime, value: Any) -> None:
        if metric not in self.data:
            self.data[metric] = OrderedDict()

        self.data[metric][format_time_interval(start_date, end_date)] = {'value': value}

    def to_json(self) -> Dict[str, Any]:
        return self.data