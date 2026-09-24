
BUILD=build

# Adjacency Distance Miles
ADJACENCY_DISTANCE=5

CENSUS_FILES=$(BUILD)/cb_2020_us_state_500k.zip \
			 $(BUILD)/cb_2020_us_county_500k.zip \
			 $(BUILD)/cb_2020_us_zcta520_500k.zip \
			 $(BUILD)/cb_2020_us_zcta3_500k.shp.zip \
			 $(BUILD)/tab20_zcta520_county20_natl.txt \
			 $(BUILD)/cb_demographics_state_2020.csv \
			 $(BUILD)/cb_demographics_county_2020.csv \
			 $(BUILD)/cb_demographics_zcta5_2020.csv \
			 $(BUILD)/cb_demographics_zcta3_2020.csv \
			 $(BUILD)/cb_acs_state_2022.csv \
			 $(BUILD)/cb_acs_county_2022.csv \
			 $(BUILD)/cb_acs_zcta5_2022.csv \
			 $(BUILD)/cb_acs_zcta3_2022.csv \
			 $(BUILD)/adjacency_edge_list_state.csv \
			 $(BUILD)/adjacency_edge_list_county.csv \
			 $(BUILD)/adjacency_edge_list_zcta3.csv \
			 $(BUILD)/adjacency_edge_list_zcta5.csv \

NEMSIS_FILES=$(BUILD)/NEMRES-20240308-Y2022.zip \
			 $(BUILD)/NEMRES-20240318-Y2023.zip \
			 $(BUILD)/NEMSIS_Monthly_county_level_data_2023.zip \
			 $(BUILD)/NEMSIS_Monthly_county_level_data_2024_Q1.zip \
			 $(BUILD)/NEMSIS_Monthly_county_level_data_2024_Q2.zip \
			 $(BUILD)/NEMSIS_Monthly_county_level_data_2024_JUL.zip \
			 $(BUILD)/NEMSIS_Monthly_county_level_data_2024_AUG.zip \
			 $(BUILD)/NEMSIS_Monthly_county_level_data_2024_SEP.zip \
			 $(BUILD)/NEMSIS_Monthly_county_level_data_2024_OCT.zip \
			 $(BUILD)/data_submission_NEMSIS_2025-01-03.zip \
			 $(BUILD)/data_submission_NEMSIS_2025-01-31.zip \
			 $(BUILD)/data_submission_NEMSIS_2025-02-28.zip \
			 $(BUILD)/data_submission_NEMSIS_2025-03-31.zip \
			 $(BUILD)/data_submission_NEMSIS_2025-05-05.zip \
			 $(BUILD)/data_submission_NEMSIS_2025-05-30.zip \
			 $(BUILD)/data_submission_NEMSIS_2025-06-30.zip \
			 

HV_FILES=$(BUILD)/hv_aggregate_table_20240320 \
		 $(BUILD)/hv_aggregate_table_20240724 \
		 $(BUILD)/hv_aggregate_table_20240930 \
		 $(BUILD)/hv_aggregate_table_20241127 \
		 $(BUILD)/hv_aggregate_table_20241223 \
		 $(BUILD)/hv_aggregate_table_20250131 \
		 $(BUILD)/hv_aggregate_table_open_claims_20250228 \
		 $(BUILD)/hv_aggregate_table_open_claims_20250331 \
		 $(BUILD)/hv_aggregate_table_20250430_HV008626 \
		 $(BUILD)/hv_aggregate_table_20250430_HV009879 \
		 $(BUILD)/hv_aggregate_table_20250531_HV009879 \
		 $(BUILD)/hv_aggregate_table_20250630_HV009879 \

VERADIGM_FILES=$(BUILD)/Veradigm_ASCVD_score_2022_2023.xlsx \
			   $(BUILD)/Veradigm_ASCVD_score_2022_2024Q1.xlsx \
			   $(BUILD)/Veradigm_ASCVD_monthly_score2022_7_2024.xlsx \
			   $(BUILD)/Veradigm_ASCVD_monthly_score_2022_2024m8_v2.xlsx \
			   $(BUILD)/Veradigm_ASCVD_monthly_score_2022_2024m10.xlsx \
			   $(BUILD)/Veradigm_ASCVD_monthly_score_2022_2024m11.xlsx \
			   $(BUILD)/Veradigm_ASCVD_monthly_score_2022_2024m12.xlsx \
			   $(BUILD)/data_submission_VERADIGM_2025-01.xlsx \
			   $(BUILD)/data_submission_VERADIGM_2025-02.xlsx \
			   $(BUILD)/data_submission_VERADIGM_2025-03.xlsx \
			   $(BUILD)/data_submission_VERADIGM_2025-04.xlsx \
			   $(BUILD)/data_submission_VERADIGM_2025-05.xlsx \
			   $(BUILD)/data_submission_VERADIGM_2025-06.xlsx \

PROJECT_USER_FILES=$(BUILD)/fake-users-projects/project_measurements.csv \
				   $(BUILD)/fake-users-projects/mid_metrics.csv \
				   $(BUILD)/fake-users-projects/project_area_association.csv \
				   $(BUILD)/fake-users-projects/projects.csv \
				   $(BUILD)/fake-users-projects/target_payout_rate.csv \
				   $(BUILD)/fake-users-projects/user_project_association.csv \
				   $(BUILD)/fake-users-projects/users.csv \
				   $(BUILD)/real-users-projects/project_measurements.csv \
				   $(BUILD)/real-users-projects/mid_metrics.csv \
				   $(BUILD)/real-users-projects/project_area_association.csv \
				   $(BUILD)/real-users-projects/projects.csv \
				   $(BUILD)/real-users-projects/target_payout_rate.csv \
				   $(BUILD)/real-users-projects/user_project_association.csv \
				   $(BUILD)/real-users-projects/users.csv



all : $(BUILD) $(CENSUS_FILES) $(NEMSIS_FILES) $(HV_FILES) $(VERADIGM_FILES) $(PROJECT_USER_FILES)           

###############################################
###########  CENSUS FILES #####################
###############################################

$(BUILD)/cb_2020_us_state_500k.zip :
	 curl https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_state_500k.zip --output-dir $(BUILD) --output cb_2020_us_state_500k.zip

$(BUILD)/cb_2020_us_county_500k.zip :
	curl https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_county_500k.zip --output-dir $(BUILD) --output cb_2020_us_county_500k.zip

$(BUILD)/cb_2020_us_zcta520_500k.zip :
	curl https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip --output-dir $(BUILD) --output cb_2020_us_zcta520_500k.zip

$(BUILD)/cb_2020_us_zcta3_500k.shp.zip :
	PYTHONPATH="${PYTHONPATH}:${pwd}" python3 datagen/generate_zcta3_geos.py -i $(BUILD)/cb_2020_us_zcta520_500k.zip -o $(BUILD)/cb_2020_us_zcta3_500k.shp.zip

$(BUILD)/tab20_zcta520_county20_natl.txt :
	curl https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_county20_natl.txt --output-dir $(BUILD) --output tab20_zcta520_county20_natl.txt

$(BUILD)/cb_demographics_state_2020.csv :
	PYTHONPATH="${PYTHONPATH}:${pwd}" python3 datagen/CensusBureau.py -o $(BUILD)/cb_demographics_state_2020.csv -g STATE

$(BUILD)/cb_demographics_county_2020.csv :
	PYTHONPATH="${PYTHONPATH}:${pwd}" python3 datagen/CensusBureau.py -o $(BUILD)/cb_demographics_county_2020.csv -g COUNTY

$(BUILD)/cb_demographics_zcta5_2020.csv :
	PYTHONPATH="${PYTHONPATH}:${pwd}" python3 datagen/CensusBureau.py -o $(BUILD)/cb_demographics_zcta5_2020.csv -g ZCTA5

$(BUILD)/cb_demographics_zcta3_2020.csv :
	PYTHONPATH="${PYTHONPATH}:${pwd}" python3 datagen/CensusBureau.py -o $(BUILD)/cb_demographics_zcta3_2020.csv -g ZCTA3

$(BUILD)/cb_acs_state_2022.csv :
	PYTHONPATH="${PYTHONPATH}:${pwd}" python3 datagen/CensusBureauACS.py -o $(BUILD)/cb_acs_state_2022.csv -g STATE

$(BUILD)/cb_acs_county_2022.csv :
	PYTHONPATH="${PYTHONPATH}:${pwd}" python3 datagen/CensusBureauACS.py -o $(BUILD)/cb_acs_county_2022.csv -g COUNTY

$(BUILD)/cb_acs_zcta5_2022.csv :
	PYTHONPATH="${PYTHONPATH}:${pwd}" python3 datagen/CensusBureauACS.py -o $(BUILD)/cb_acs_zcta5_2022.csv -g ZCTA5

$(BUILD)/cb_acs_zcta3_2022.csv :
	PYTHONPATH="${PYTHONPATH}:${pwd}" python3 datagen/CensusBureauACS.py -o $(BUILD)/cb_acs_zcta3_2022.csv -g ZCTA3

$(BUILD)/adjacency_edge_list_state.csv :
	PYTHONPATH="${PYTHONPATH}:${pwd}" python3 datagen/generate_adjacency_edge_list.py -i $(BUILD)/cb_2020_us_state_500k.zip -o $(BUILD)/adjacency_edge_list_state.csv -g STATE -d $(ADJACENCY_DISTANCE)

$(BUILD)/adjacency_edge_list_county.csv :
	PYTHONPATH="${PYTHONPATH}:${pwd}" python3 datagen/generate_adjacency_edge_list.py -i $(BUILD)/cb_2020_us_county_500k.zip -o $(BUILD)/adjacency_edge_list_county.csv -g COUNTY -d $(ADJACENCY_DISTANCE)

$(BUILD)/adjacency_edge_list_zcta3.csv :
	PYTHONPATH="${PYTHONPATH}:${pwd}" python3 datagen/generate_adjacency_edge_list.py -i $(BUILD)/cb_2020_us_zcta3_500k.shp.zip -o $(BUILD)/adjacency_edge_list_zcta3.csv -g ZCTA3 -d $(ADJACENCY_DISTANCE)

$(BUILD)/adjacency_edge_list_zcta5.csv :
	PYTHONPATH="${PYTHONPATH}:${pwd}" python3 datagen/generate_adjacency_edge_list.py -i $(BUILD)/cb_2020_us_zcta520_500k.zip -o $(BUILD)/adjacency_edge_list_zcta5.csv -g ZCTA5 -e GEOID20 -d $(ADJACENCY_DISTANCE)


###############################################
###########  VERADIGM FILES ###################
###############################################

$(BUILD)/Veradigm_ASCVD_score_2022_2023.xlsx :
	@echo "WARNING: Please Download the ASCVD Data from the project raw-data store: Veradigm_ASCVD_score_2022_2023.xlsx"

$(BUILD)/Veradigm_ASCVD_score_2022_2024Q1.xlsx :
	@echo "WARNING: Please Download the ASCVD Data from the project raw-data store: Veradigm_ASCVD_score_2022_2024Q1.xlsx"

$(BUILD)/Veradigm_ASCVD_monthly_score2022_7_2024.xlsx :
	@echo "WARNING: Please Download the ASCVD Data from the project raw-data store: Veradigm_ASCVD_monthly_score2022_7_2024.xlsx"

$(BUILD)/Veradigm_ASCVD_monthly_score_2022_2024m8_v2.xlsx :
	@echo "WARNING: Please Download the ASCVD Data from the project raw-data store: Veradigm_ASCVD_monthly_score_2022_2024m8_v2.xlsx"

$(BUILD)/Veradigm_ASCVD_monthly_score_2022_2024m10.xlsx :
	@echo "WARNING: Please Download the ASCVD Data from the project raw-data store: Veradigm_ASCVD_monthly_score_2022_2024m10.xlsx"

$(BUILD)/Veradigm_ASCVD_monthly_score_2022_2024m11.xlsx :
	@echo "WARNING: Please Download the ASCVD Data from the project raw-data store: Veradigm_ASCVD_monthly_score_2022_2024m11.xlsx"

$(BUILD)/Veradigm_ASCVD_monthly_score_2022_2024m12.xlsx :
	@echo "WARNING: Please Download the ASCVD Data from the project raw-data store: Veradigm_ASCVD_monthly_score_2022_2024m12.xlsx"

$(BUILD)/data_submission_VERADIGM_2025-01.xlsx :
	@echo "WARNING: Please Download the ASCVD Data from the project raw-data store: data_submission_VERADIGM_2025-01.xlsx"
	
$(BUILD)/data_submission_VERADIGM_2025-02.xlsx :
	@echo "WARNING: Please Download the ASCVD Data from the project raw-data store: data_submission_VERADIGM_2025-02.xlsx"
	
$(BUILD)/data_submission_VERADIGM_2025-03.xlsx :
	@echo "WARNING: Please Download the ASCVD Data from the project raw-data store: data_submission_VERADIGM_2025-03.xlsx"

$(BUILD)/data_submission_VERADIGM_2025-04.xlsx :
	@echo "WARNING: Please Download the ASCVD Data from the project raw-data store: data_submission_VERADIGM_2025-04.xlsx"

$(BUILD)/data_submission_VERADIGM_2025-05.xlsx :
	@echo "WARNING: Please Download the ASCVD Data from the project raw-data store: data_submission_VERADIGM_2025-05.xlsx"

$(BUILD)/data_submission_VERADIGM_2025-06.xlsx :
	@echo "WARNING: Please Download the ASCVD Data from the project raw-data store: data_submission_VERADIGM_2025-06.xlsx"


###############################################
##############  HV FILES ######################
###############################################

$(BUILD)/hv_aggregate_table_20240320 :
	@echo "WARNING: Please Download HV Aggregate Table Data from the project raw-data store: hv_aggregate_table_20240320"

$(BUILD)/hv_aggregate_table_20240724 :
	@echo "WARNING: Please Download HV Aggregate Table Data from the project raw-data store: hv_aggregate_table_20240724"

$(BUILD)/hv_aggregate_table_20240930 :
	@echo "WARNING: Please Download HV Aggregate Table Data from the project raw-data store: hv_aggregate_table_20240930"

$(BUILD)/hv_aggregate_table_20241127 :
	@echo "WARNING: Please Download HV Aggregate Table Data from the project raw-data store: hv_aggregate_table_20241127"

$(BUILD)/hv_aggregate_table_20241223 :
	@echo "WARNING: Please Download HV Aggregate Table Data from the project raw-data store: hv_aggregate_table_20241223"

$(BUILD)/hv_aggregate_table_20250131 :
	@echo "WARNING: Please Download HV Aggregate Table Data from the project raw-data store: hv_aggregate_table_20250131"

$(BUILD)/hv_aggregate_table_open_claims_20250228 :
	@echo "WARNING: Please Download HV Aggregate Table Data from the project raw-data store: hv_aggregate_table_open_claims_20250228"

$(BUILD)/hv_aggregate_table_open_claims_20250331 :
	@echo "WARNING: Please Download HV Aggregate Table Data from the project raw-data store: hv_aggregate_table_open_claims_20250331"

$(BUILD)/hv_aggregate_table_20250430_HV008626 :
	@echo "WARNING: Please Download HV Aggregate Table Data from the project raw-data store: hv_aggregate_table_20250430_HV008626"

$(BUILD)/hv_aggregate_table_20250531_HV009879 :
	@echo "WARNING: Please Download HV Aggregate Table Data from the project raw-data store: hv_aggregate_table_20250531_HV009879"

$(BUILD)/hv_aggregate_table_20250630_HV009879 :
	@echo "WARNING: Please Download HV Aggregate Table Data from the project raw-data store: hv_aggregate_table_20250630_HV009879"


###############################################
##############  NEMSIS FILES ##################
###############################################


$(BUILD)/NEMRES-20240930.zip:
	@echo "WARNING: Please Download the NEMSIS County Level 2024 Q2 Data from the project raw-data store: NEMRES-20240930.zip"

$(BUILD)/NEMRES-20240308-Y2022.zip :
	@echo "WARNING: Please Download NEMRES 20240308 Data from the project raw-data store: NEMRES-20240308-Y2022.zip"

$(BUILD)/NEMRES-20240318-Y2023.zip :
	@echo "WARNING: Please Download NEMRES 20240318 Data from the project raw-data store: NEMRES-20240318-Y2023.zip"

$(BUILD)/NEMSIS_Monthly_county_level_data_2023.zip :
	@echo "WARNING: Please Download NEMSIS_Monthly_county_level_data_2023.zip from the project raw-data store: NEMSIS_Monthly_county_level_data_2023.zip"

$(BUILD)/NEMSIS_Monthly_county_level_data_2024_Q1.zip :
	@echo "WARNING: Please Download the NEMSIS County Level 2024 Q1 Data from the project raw-data store: NEMSIS_Monthly_county_level_data_2024_Q1.zip"
	
$(BUILD)/NEMSIS_Monthly_county_level_data_2024_Q2.zip :
	@echo "WARNING: Please Download the NEMSIS County Level 2024 Q2 Data from the project raw-data store: NEMSIS_Monthly_county_level_data_2024_Q2.zip"

$(BUILD)/NEMSIS_Monthly_county_level_data_2024_AUG.zip :
	@echo "WARNING: Please Download NEMSIS_Monthly_county_level_data_2024_AUG.zip from the project raw-data store: NEMSIS_Monthly_county_level_data_2024_AUG.zip"

$(BUILD)/NEMSIS_Monthly_county_level_data_2024_SEP.zip :
	@echo "WARNING: Please Download NEMSIS_Monthly_county_level_data_2024_SEP.zip from the project raw-data store: NEMSIS_Monthly_county_level_data_2024_SEP.zip"

$(BUILD)/NEMSIS_Monthly_county_level_data_2024_OCT.zip :
	@echo "WARNING: Please Download NEMSIS_Monthly_county_level_data_2024_OCT.zip from the project raw-data store: NEMSIS_Monthly_county_level_data_2024_OCT.zip"

$(BUILD)/data_submission_NEMSIS_2025-01-03.zip :
	@echo "WARNING: Please Download data_submission_NEMSIS_2025-01-03.zip from the project raw-data store: data_submission_NEMSIS_2025-01-03.zip"

$(BUILD)/data_submission_NEMSIS_2025-01-31.zip :
	@echo "WARNING: Please Download data_submission_NEMSIS_2025-01-31.zip from the project raw-data store: data_submission_NEMSIS_2025-01-31.zip"

$(BUILD)/data_submission_NEMSIS_2025-02-28.zip :
	@echo "WARNING: Please Download data_submission_NEMSIS_2025-02-28.zip from the project raw-data store: data_submission_NEMSIS_2025-02-28.zip"
	
$(BUILD)/data_submission_NEMSIS_2025-03-31.zip :
	@echo "WARNING: Please Download data_submission_NEMSIS_2025-03-31.zip from the project raw-data store: data_submission_NEMSIS_2025-03-31.zip"

$(BUILD)/data_submission_NEMSIS_2025-05-05.zip :
	@echo "WARNING: Please Download data_submission_NEMSIS_2025-05-05.zip from the project raw-data store: data_submission_NEMSIS_2025-05-05.zip"

$(BUILD)/data_submission_NEMSIS_2025-05-30.zip :
	@echo "WARNING: Please Download data_submission_NEMSIS_2025-05-05.zip from the project raw-data store: data_submission_NEMSIS_2025-05-30.zip"

$(BUILD)/data_submission_NEMSIS_2025-06-30.zip :
	@echo "WARNING: Please Download data_submission_NEMSIS_2025-06-30.zip from the project raw-data store: data_submission_NEMSIS_2025-06-30.zip"


$(BUILD) :
	@echo "Making Build Dir ..."
	@mkdir -p $(BUILD)

clean :
	@echo "Removing Build Dir ..."
	@rm -rf build

zip :
	@echo "Zipping Build Dir ..."
	cd $(BUILD) && zip -r ../bundles/data_bundle_$(shell date +'%y%m%d').zip *
