from dagster_pandas import PandasColumn, create_dagster_pandas_dataframe_type


RawBinStatisticsDataFrame = create_dagster_pandas_dataframe_type(
    name='RawNEMSISBinStatisticsDataFrame',
    columns=[
        PandasColumn.integer_column('MeasureRank', is_required=True, min_value=0, max_value=9),
        PandasColumn.string_column('_TYPE_', is_required=True),
        PandasColumn.float_column('_VALUE_', is_required=True),
    ],
)


BinStatisticsDataFrame = create_dagster_pandas_dataframe_type(
    name="BinStatisticsDataFrame",
    columns=[
        PandasColumn.datetime_column('start_date', is_required=True),
        PandasColumn.datetime_column('end_date', is_required=True),
        PandasColumn.string_column('outcome', is_required=True),
        PandasColumn.string_column('measure', is_required=True),
        PandasColumn.integer_column('rank', is_required=True, min_value=0, max_value=9),
        PandasColumn.string_column('rankValue', is_required=True),
        PandasColumn.integer_column('n', is_required=True),
        PandasColumn.float_column('min', is_required=True),
        PandasColumn.float_column('median', is_required=True),
        PandasColumn.float_column('mean', is_required=True),
        PandasColumn.float_column('midpoint', is_required=True),
        PandasColumn.float_column('max', is_required=True),
        PandasColumn.string_column('type', is_required=True),
        PandasColumn.string_column('source_file', is_required=True),
        PandasColumn.string_column('row_num', is_required=True),
    ]
)
