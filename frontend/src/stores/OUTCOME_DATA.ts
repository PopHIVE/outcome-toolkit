import type { SpatialGranularity } from "@/stores/SPATIAL_GRANULARITY_DATA";
import type { MetricKeyType, OutcomeKeyType } from "@/types";
import { compactNumber, compactPercent } from "@/util/formatters";
import { DATA_SOURCE } from "@/util/Consts";

export type OutcomeType = {
  // Database key
  key: OutcomeKeyType;
  // Used for short presentations like button labels
  label: string;
  // Path to icon image
  icon: string;
  // Path to Outcome image used in about page
  image: string;

  /** Used to construct About pages. */
  aboutOverview: string;
  aboutProblem: string;
  aboutMetrics: string;
  aboutReferences: string;
  /** Minimum population to qualify */
  populationTarget: number;
  searchTitle: string;
  selectDescription: string;
  searchProblem: string;
  /** NEMSIS data is county-level, others are zcta3. */
  spatialGranularity: SpatialGranularity;
  /** The payment rate header. */
  payoutTableTargetHeader: string;
  /** Verbiage for the payout table U*/
  payoutPercentImprovement: string;

  /** Used in Project page payout wizard */
  denomination: number;
  unit: string;
  rate: string;
  rateLong: string;
  typeAndDenom: string;
  /**
   * Details of the metric and allowable range to qualify for the program.
   * FUTURE: Have an array or dict of metrics for each outcome.
   */
  metric: {
    /** Database key for this metric */
    key: MetricKeyType; // "alcohol_rate"
    /** Database key for trailing 6mo average of metric */
    keyT6mo: MetricKeyType;
    /** Whether we have actual values for this metric, or only the bins. */
    hasMetricValues: boolean;
    /** Human-readable explanation of this metric */
    label: string; // "Relative rate of emergency medical service encounters for alcohol-related emergencies per 100,000 population"
    /** Short human-readable label (used for Y axis), e.g. "Rate of EMS encounters per 100,000" */
    shortLabel: string;
    /** Human-readable source for the data, e.g., 'NEMSIS'. */
    dataSource: string;
    /** Detailed description of data use policy for this stream of data. */
    dataUsage: string;
    /** File containing the definitions for the metric */
    definitions: string;
    /** File containing the Coverage by State for the metric */
    coverageByState: string;
    // At least one of these must be defined
    /** The minimum value (e.g. 123.456) that this metric can have to qualify for the Outcome Toolkit program */
    min?: number; // undefined
    /** The maximum value (e.g. 234.567) that this metric can have to qualify for the Outcome Toolkit program */
    max?: number; // undefined
    /** The minimum rank (e.g. 5th overall) that this metric can have to qualify for the Outcome Toolkit program */
    minRank?: number; // 5
    /** The maximum rank (e.g. 5th overall) that this metric can have to qualify for the Outcome Toolkit program */
    maxRank?: number; // undefined
    /** Human-readable range of the time period of data.*/
    timeRange: string;
    /** Formatter for values of this metric type, e.g. ASCVD is shown as %0.2f */
    valueFormatter: (n: number) => string;
  };
};

export const OUTCOME_DATA: Record<OutcomeKeyType, OutcomeType> = {
  alcohol: {
    aboutMetrics:
      "The National Emergency Medical System Information System (NEMSIS) is a county-level dataset that includes all emergency medical system (e.g., ambulance) services nationwide. The metric used to monitor performance will be the rate of EMS patient encounters for alcohol-related emergencies per 100,000 population.",
    aboutOverview:
      "Excessive alcohol consumption includes binge drinking and heavy drinking. Binge drinking is defined as the intake of 5 or more alcoholic beverages in a single sitting for men, or 4 or more drinks for women. Heavy drinking refers to the consumption of 15 or more drinks per week for men, or 8 or more drinks per week for women. <sup>1,2</sup>",
    aboutProblem:
      "Excessive alcohol consumption contributes to over 140,000 fatalities in the United States annually, reducing the life expectancy of those affected by an average of 26 years.<sup>1</sup> Excessive alcohol consumption is also linked to an increased risk of injuries, as well as chronic illnesses like liver and heart diseases. It is associated with a higher incidence of various cancers and adverse pregnancy outcomes. In 2010, the economic burden of excessive alcohol use was estimated at $249 billion.<sup>2</sup>",
    aboutReferences: `
    <ol>
      <li><a href="https://www.cdc.gov/alcohol/excessive-drinking-data/">Data on Excessive Drinking | CDC</a></li>
      <li><a href="https://www.cdc.gov/alcohol/fact-sheets/states/excessive-alcohol-use-united-states.html">Addressing Excessive Alcohol Use: State Fact Sheets (cdc.gov)</a></li>
    </ol>`,
    icon: "/iv_bag.svg",
    image: "/alcohol.jpg",
    key: "alcohol",
    label: "Alcohol-Related Health Harms",
    payoutTableTargetHeader: " in rate of EMS encounters",
    payoutPercentImprovement:
      "relative % change in rate from the current geographic and national rates",
    denomination: 100_000,
    unit: "population",
    rate: "alcohol-related emergencies rate",
    rateLong: "rate of alcohol-related emergencies",
    typeAndDenom: "alcohol-related emergencies per 100,000",
    // FUTURE: source from DB the metrics associated with each outcome
    metric: {
      key: "alcohol_rate",
      keyT6mo: "alcohol_rate_6mo",
      hasMetricValues: false,
      label:
        "Rate of EMS patient encounters for alcohol-related emergencies per 100,000 population",
      shortLabel: "Alcohol-related EMS encounters per 100,000",
      definitions: "/Outcome Toolkit Program_Alcohol Related Health Harms_Measure Definition.xlsx",
      coverageByState: "",
      minRank: 5,
      dataUsage:
        "Data on Alcohol Related Health Harms is provided by National Highway Traffic Safety Administration (NHTSA), National Emergency Medical Services Information System (NEMSIS). The content reproduced from the NEMSIS Database remains the property of the National Highway Traffic Safety Administration (NHTSA). The National Highway Traffic Safety Administration is not responsible for any claims arising from works based on the original Data, Text, Tables, or Figures.",
      dataSource: "NEMSIS",
      timeRange: "Jan 2023. - Dec. 2023",
      valueFormatter: (n) => compactNumber(n, { precision: 0, hideBelow: 0 }),
    },
    populationTarget: 500_000,
    searchProblem:
      "Excessive alcohol consumption contributes to over 140,000 fatalities in the United States annually, and is linked to a high risk of injuries, diseases, and adverse pregnancy outcomes. In 2010, the economic burden of excessive alcohol use was estimated at $249 billion.",
    searchTitle: "Alcohol-Related Emergencies Relative Rate",
    selectDescription:
      "Excessive alcohol consumption contributes to over 140,000 fatalities in the United States annually, and is linked to a high risk of injuries, diseases, and adverse pregnancy outcomes.<sup>3,4</sup> In 2010, the economic burden of excessive alcohol use was estimated at $249 billion.",
    spatialGranularity: "COUNTY",
  },
  cardio: {
    aboutMetrics:
      "The ASCVD risk calculator will be used to track progress. It captures key clinical variables (i.e., age, sex, race, blood pressure, cholesterol, smoking history, diabetes history, hypertension treatment, statin medication, and aspirin therapy) that, in aggregate, are used to estimate a patient’s 10-year ASCVD risk. Tracking changes in ASCVD risk over time will allow the Health Catalyst to identify impacts of different interventions on patient risk.<sup>3</sup>",
    aboutOverview:
      "Nationally, heart disease is the leading cause of death in the United States. About 695,000 people died from heart disease in 2021 (this equates to 1 in every 5 deaths). In 2021, 1 in 6 deaths from cardiovascular disease was due to stroke. There are about 1.6M annual total heart attacks and stroke-related deaths and 1.2M first-time heart attack and strokes per year.<sup>1</sup>",
    aboutProblem:
      "Risk factors contributing to cardiovascular disease include lifestyle factors such as diet, physical activity, and smoking; disease factors such as obesity, diabetes, and high blood pressure; and lack of access to healthcare due to barriers such as cost, transportation, and language in addition to other social drivers.<sup>2</sup> Despite prevention guidelines, cardiovascular disease is still a leading cause of death in the U.S. Atherosclerotic Cardiovascular Disease (ASCVD) national expenditures are projected to reach $309 billion by 2035. The consequences of ASCVD are significant for patients, providers, and payers from a health and wellness point of view as well as financial. ",
    aboutReferences: `
    <ol>
      <li><a href="https://www.cdc.gov/heart-disease/data-research/facts-stats/">Heart Disease Facts | cdc.gov</a></li>
      <li><a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8351755/">2019 ACC/AHA Guideline on the Primary Prevention of Cardiovascular Disease: Executive Summary - PMC (nih.gov) </a></li>
      <li><a href="https://www.heart.org/en/professional/quality-improvement/ascvd">ASCVD | American Heart Association</a></li>
    </ol>`,
    icon: "/heart.svg",
    image: "/cardio.jpg",
    key: "cardio",
    label: "Heart Attack and Stroke Risk",
    payoutTableTargetHeader: " in ASCVD Risk Score",
    payoutPercentImprovement:
      "change in ASCVD risk score as a percentage from the current average geographic and national risk scores",
    denomination: 0,
    unit: "ASCVD risk score",
    rate: "change in ASCVD risk",
    rateLong: "10 year ASCVD risk change",
    typeAndDenom: "aggregate 10-year risk for people aged 40-70 years",
    metric: {
      key: "total_mean",
      keyT6mo: "total_mean_6mo",
      hasMetricValues: true,
      label: "Aggregate 10-year risk of heart attack and stroke for people aged 40-70 years",
      shortLabel: "ASCVD risk score (avg 40-70 yrs)",
      dataSource: "Veridigm",
      dataUsage:
        "Data for the 10-year Atherosclerotic Cardiovascular Disease (ASCVD) risk score is provided by Veradigm from multiple sources using the Veradigm Network Electronic Health Record (EHR) database for patients with all data elements necessary for score calculation. It is important to note that the data displayed in the Outcome Toolkit are not intended to represent the entire US population. Data may not be re-identified or used for any purposes other than the Outcome Toolkit program.",
      definitions: "",
      coverageByState: "",
      // TODO: Minimum rank is based on the lower end of an individual's 'Intermediate Risk'. This should be changed to something the program or Health SMEs agree upon. Source: https://tools.acc.org/ascvd-risk-estimator-plus/#!/calculate/estimate/
      minRank: 5,
      timeRange: "Jan. 2022 - Dec. 2023",
      valueFormatter: (n) => compactPercent(n, { hideBelow: 0, precision: 1 }),
    },
    populationTarget: 700_000,
    searchProblem:
      "Factors related to lifestyle, disease, and access to healthcare (such as high blood pressure, high cholesterol, smoking, obesity, diabetes) all contribute to heart attack and stroke risk with 1 in 3 US adults having at least one of these conditions or habits",
    searchTitle: "ASCVD Risk Rate",
    selectDescription:
      "Heart disease is the leading cause of death in the U.S., with 695,000 fatalities in 2021. Annually, there are 1.6 million heart attack and stroke-related deaths, including 1.2 million first-time occurrences. The presence of certain health conditions and unhealthy lifestyle choices can also lead to increased risk, contributing further to this national crisis.",
    spatialGranularity: "ZCTA3",
  },
  opioid: {
    aboutMetrics:
      "The National Emergency Medical Services Information System (NEMSIS) is the national system used to collect, store, and share EMS data from the U.S. States and Territories. The metric used to monitor performance will be the rate of EMS patient encounters for fatal and non-fatal opioid overdoses per 100,000 population.",
    aboutOverview:
      "Opioid Use Disorder (OUD) is the chronic use of opioids that causes an individual clinically significant problems or impairment.<sup>1</sup> OUD consists of an overpowering desire to use opioids, increased opioid tolerance, and withdrawal syndrome when discontinued. OUD includes dependence and addiction. OUD significantly contributes to overdose deaths among people who use illegal opioids or misuse prescription opioids.",
    aboutProblem:
      "OUD is a life-threatening condition associated with a 20-fold greater risk of early death due to overdose, infectious diseases, trauma, and suicide<sup>2</sup>. Fewer than 10 percent of U.S. patients with diagnosed OUD receive medication-assisted treatment. Behavioral therapies alone have limited efficacy in addressing the symptoms and physical issues related to OUD.",
    aboutReferences: `
    <ol>
      <li><a href="https://www.cdc.gov/overdose-prevention/">Opioid Use Disorder | Feature Topics | Drug Overdose (cdc.gov)</a></li>
      <li><a href="https://pubmed.ncbi.nlm.nih.gov/30896911/">Medications for Opioid Use Disorder Save Lives - PubMed (nih.gov)</a></li>
    </ol>`,
    icon: "/pills.svg",
    image: "/opioid.jpg",
    key: "opioid",
    label: "Opioid Overdose",
    populationTarget: 500_000,
    searchProblem:
      "Opioid Use Disorder is a life-threatening condition associated with a 20-fold greater risk of early death due to overdose, infectious diseases, trauma, and suicide",
    searchTitle: "Fatal and Non-fatal Opioid Overdose Relative Rate",
    selectDescription:
      "Opioid overdoses are the leading cause of death among young Americans and rates continue to rise. Identifying those with opioid use disorder and providing effective treatment can prevent overdose and death.",

    payoutTableTargetHeader: " in rate of EMS encounters",
    payoutPercentImprovement:
      "relative % change in rate from the current geographic and national rates",
    denomination: 100_000,
    unit: "population",
    rate: "overdose encounters rate",
    rateLong: "rate of overdose encounters",
    typeAndDenom: "overdose encounters per 100,000",
    metric: {
      key: "opioid_rate",
      keyT6mo: "opioid_rate_6mo",
      hasMetricValues: false,
      label:
        "Rate of EMS patient encounters for fatal and non-fatal opioid overdoses per 100,000 population",
      shortLabel: "Opioid overdose encounters per 100,000 population",
      dataSource: "NEMSIS",
      dataUsage:
        "Data on Opioid Overdose Incidents is provided by National Highway Traffic Safety Administration (NHTSA), National Emergency Medical Services Information System (NEMSIS). The content reproduced from the NEMSIS Database remains the property of the National Highway Traffic Safety Administration (NHTSA). The National Highway Traffic Safety Administration is not responsible for any claims arising from works based on the original Data, Text, Tables, or Figures.",
      definitions: "/Outcome Toolkit Program_Opioid Overdose_Measure Definition.xlsx",
      coverageByState: "",
      minRank: 5,
      timeRange: "Jan. 2023 - Dec. 2023",
      valueFormatter: (n) => compactNumber(n, { hideBelow: 0, precision: 1 }),
    },
    spatialGranularity: "COUNTY",
  },
  soc: {
    aboutMetrics:
      "The Severe Obstetric Complications (SOC) measure uses hospital claims to track the rate of complications developing during the delivery hospitalization and 60 days after delivery. The Outcome Toolkit Program uses a modified version of the SOC electronic clinical quality measures (eCQM) that was developed by Yale New Haven Health Services Corporation - Center for Outcomes Research and Evaluation (CORE) and The Joint Commission (TJC) through a contract with the Centers for Medicare & Medicaid Services (CMS).<sup>2</sup> In addition to extending the measurement period to 60-days post-delivery, the Outcome Toolkit program has added certain mental health conditions as SOCs (e.g., suicide, self-harm, and substance use) if they result in admissions to inpatient hospitals, psychiatric centers, or substance use treatment centers in the 60-day post-delivery period.",
    aboutOverview:
      "The United States is the only developed country with increasing maternal mortality and severe maternal morbidity (SMM) rates. Racial disparities exist within those increasing rates for non-Hispanic Black and Native American pregnant women being 2-3 times more likely to die from pregnancy-related death than non-Hispanic-white pregnant women. Pregnant women living in rural areas without access to obstetric care are 60% more likely to die from pregnancy related causes than those in non-rural areas. Many of these deaths and complications can be prevented.<sup>1</sup> ",
    aboutProblem:
      "Due to inconsistent maternal health data in the U.S., root causes of poor maternal health outcomes are difficult to discern and compare nationally. In addition to poor quality data, other areas that impact maternal health outcomes include: <ul><li>Access to care and coverage of maternal health services (often referred to as maternity care deserts)</li><li>Lack of economic and social support before, during, and after pregnancy</li><li>Co-occurring mental health and substance use concerns, including opioid abuse.</li></ul>",
    aboutReferences: `
    <ol>
      <li><a href="https://archive.cdc.gov/#/details?url=https://www.cdc.gov/media/releases/2022/p0919-pregnancy-related-deaths.html">Four in 5 pregnancy-related deaths in the U.S. are preventable | CDC Online Newsroom | CDC</a></li>
      <li><a href="https://ecqi.healthit.gov/sites/default/files/SevereObstetricComplications%20eCQM_Methodology%20Report%20-%20Dec%202022.pdf">SOC eCQM Methodology Report (healthit.gov)</a></li>
    </ol>`,
    icon: "/pregnant_person.svg",
    image: "/soc.jpg",
    key: "soc",
    label: "Maternal Health",
    payoutTableTargetHeader: " in rate of SOCs",
    payoutPercentImprovement:
      "relative % change in rate from the current geographic and national rates",
    denomination: 10_000,
    unit: "SOCs",
    rate: "SOC rate",
    rateLong: "rate of SOCs",
    typeAndDenom: "SOCs per 10,000 deliveries",
    metric: {
      key: "any_soc_rate",
      keyT6mo: "any_soc_rate_6mo",
      // Ingest maternal data only has binned ranges, not point values.
      hasMetricValues: DATA_SOURCE === "api",
      label:
        "Rate of severe obstetric complications (SOC) during the delivery hospitalization and 60 days postpartum per 10,000 deliveries (open claims only)",
      shortLabel: "SOC per 10,000 deliveries (open claims)",
      dataSource: "HealthVerity",
      dataUsage: `Data on maternal health severe obstetric complications (SOCs) are provided by HealthVerity
        from multiple sources and represent aggregate reports based upon open claims data,
        hospital charge data, and mortality data for the periods covered.
        It is important to note that the data displayed in the Outcome Toolkit are not intended to represent the entire US population.
        Data may not be re- identified or used for any purposes other than the Outcome Toolkit program.`,
      definitions: "",
      coverageByState: "",
      minRank: 5,
      timeRange: "Jan. 2021 - Oct. 2023",
      valueFormatter: (n) => compactNumber(n, { hideBelow: 0, precision: 1 }),
    },
    populationTarget: 5_000_000,
    searchProblem:
      "Although maternal mortality and severe maternal morbidity (SMM) rates continue to rise, root causes of poor maternal health outcomes are difficult to discern and compare nationally",
    searchTitle: "SOC Rate",
    selectDescription:
      "Severe Obstetric Complications (SOC) can occur during or after labor and delivery and can result in major disability and even death after pregnancy.",
    spatialGranularity: "ZCTA3",
  },
};
