import random
from locust import HttpUser, task, constant, tag

OUTCOMES = ['soc', 'opioid', 'alcohol', 'cardio']
GEOGRAPHIES = ['state', 'county', 'zcta3']


class APIUserV2(HttpUser):
    wait_time = constant(1)

    @tag('v2')
    @task(1)
    def api_geometry_route_v2(self):
        geography = random.choice(GEOGRAPHIES)

        self.client.get(
            url=f'/api/v2/{geography}/geometries?start_date=2019-01-01&end_date=2024-01-01',
            name=f'/api/v2/{geography}/geometries',
        )

    @tag('v2')
    @task(1)
    def api_details_route_v2(self):
        self.client.post(
            url='/api/v2/details',
            name='/api/v2/details',
            json={
                'outcome': 'soc',
                'mids': [],
                'metrics': ['any_soc_rate'],
                'aggregate': False,
            },
        )

    @tag('v2')
    @task(1)
    def api_overview_route_v2(self):
        outcome = 'soc'
        metric = 'any_soc_rate'
        start_date = '2023-01-01'
        end_date = '2024-01-01'

        self.client.get(
            url=f'/api/v2/overview?outcome={outcome}&metric={metric}&start_date={start_date}&end_date={end_date}',
            name='/api/v2/overview',
        )

    @tag('v2')
    @task(1)
    def api_bins_route_v2(self):
        outcome = random.choice(OUTCOMES)
        self.client.get(url=f'/api/v2/bins?outcome={outcome}', name='/api/v2/bins')

    @tag('v2')
    @task(1)
    def api_trendline_route_v2(self):
        outcome = random.choice(OUTCOMES)
        self.client.post(
            url='/api/v2/trendlines/national',
            json={'outcome': outcome},
            name='/api/v2/trendlines/national',
        )
