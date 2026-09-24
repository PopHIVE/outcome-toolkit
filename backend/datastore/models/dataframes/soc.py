from dagster_pandas import PandasColumn, create_dagster_pandas_dataframe_type


soc_metric_columns = [
        PandasColumn.integer_column('dist_hvid_cnt', is_required=True, min_value=0),
        PandasColumn.integer_column('acute_myocardial_infarction', is_required=True, min_value=0),
        PandasColumn.integer_column('aneurysm', is_required=True, min_value=0),
        PandasColumn.integer_column('acute_renal_failure', is_required=True, min_value=0),
        PandasColumn.integer_column('ards', is_required=True, min_value=0),
        PandasColumn.integer_column('amniotic_fluid_embolism', is_required=True, min_value=0),
        PandasColumn.integer_column('cardiac_arrest_vfib', is_required=True, min_value=0),
        PandasColumn.integer_column('convert_cardiac_rhythm', is_required=True, min_value=0),
        PandasColumn.integer_column('dic', is_required=True, min_value=0),
        PandasColumn.integer_column('transfusion', is_required=True, min_value=0),
        PandasColumn.integer_column('eclampsia', is_required=True, min_value=0),
        PandasColumn.integer_column('hf_arrest_during_surgery', is_required=True, min_value=0),
        PandasColumn.integer_column('puerperal_cvd', is_required=True, min_value=0),
        PandasColumn.integer_column('pe_acute_hf', is_required=True, min_value=0),
        PandasColumn.integer_column('anesthesia_comp', is_required=True, min_value=0),
        PandasColumn.integer_column('sepsis', is_required=True, min_value=0),
        PandasColumn.integer_column('shock', is_required=True, min_value=0),
        PandasColumn.integer_column('sickle_cell_crisis', is_required=True, min_value=0),
        PandasColumn.integer_column('air_thrombotic_embolism', is_required=True, min_value=0),
        PandasColumn.integer_column('hysterectomy', is_required=True, min_value=0),
        PandasColumn.integer_column('tracheostomy', is_required=True, min_value=0),
        PandasColumn.integer_column('ventilation', is_required=True, min_value=0),
        PandasColumn.integer_column('exclude_transfusion', is_required=True, min_value=0),
        PandasColumn.integer_column('any_soc', is_required=True, min_value=0),
        PandasColumn.integer_column('mortality', is_required=True, min_value=0),
        PandasColumn.integer_column('mh_suicide_self_harm', is_required=True, min_value=0),
        PandasColumn.integer_column('mh_abuse', is_required=True, min_value=0),
        PandasColumn.integer_column('mh_sud', is_required=True, min_value=0),
        PandasColumn.integer_column('mh_spmi', is_required=True, min_value=0),
        PandasColumn.integer_column('any_soc_mortality', is_required=True, min_value=0)
]

soc_added_columns = [
    # PandasColumn.integer_column('any_soc_rate',
    # PandasColumn.integer_column('any_soc_rate_rank',
    # PandasColumn.integer_column('any_soc_rate_rank_value',
]

RawSOCDataFrame = create_dagster_pandas_dataframe_type(
    name='RawSOCDataFrame',
    columns=[
        PandasColumn.string_column('zip3', is_required=True),
        PandasColumn.string_column('state', is_required=True),
        PandasColumn.string_column('date_delivery', is_required=True),
        PandasColumn.string_column('race_ethnicity', is_required=True),
        PandasColumn.string_column('age_category', is_required=True),
        *soc_metric_columns,
        PandasColumn.string_column('row_num', is_required=True)
    ]
)

AggregatedSOCDataFrame = create_dagster_pandas_dataframe_type(
    name='AggregatedSOCDataFrame',
    columns=[
        PandasColumn.string_column('zip3', is_required=True),
        PandasColumn.string_column('mid', is_required=True),
        *soc_metric_columns,
        PandasColumn.numeric_column('any_soc_rate', min_value=0, max_value=10_000, non_nullable=True),
        PandasColumn.integer_column('any_soc_rate_rank', min_value=0, max_value=9, non_nullable=True),
        PandasColumn.string_column('row_num', is_required=True)
    ]
)