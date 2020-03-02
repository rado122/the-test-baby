import logging
import json
from datetime import date

import clearbit
from faust.web import Request, Response, View

from tide_test.app import app
from tide_test.company_view.models import Company


companies_topic = app.topic('companies', partitions=8, value_type=Company)

domain_information_topic = app.topic('domain_information', partitions=8) # TODO: read what partition is

messages = [] # use as in-memory data-base will be wiped on restart

companies_stats = {} # use as in-memory data-base will be wiped on restart

async def collect_domain_information(domain):
    domain_info = clearbit.Enrichment.find(domain=domain)
    if domain_info:
        print(f"found info for {domain} domain")
        await domain_information_topic.send(value=domain_info)
    else:
        print(f"No info found for {domain} domain")


@app.agent(domain_information_topic)
async def store_company_stats(domain_infos):
    async for domain_info in domain_infos: # BS naming sorry
        employees_count = domain_info.get('metrics', {}).get('employees', None) # I prefer to add expecit None value
        age = None
        company_name = domain_info['name'].lower()
        
        founded_year = domain_info.get('foundedYear', None)
        if founded_year:
            current_year = date.today().year
            age = current_year - founded_year

        companies_stats[company_name] = {
            "employees_count": employees_count,
            "age": age
        }


@app.agent(companies_topic, sink=[collect_domain_information])
async def store_company_views(companies):
    async for company in companies:
        # TODO: Validate company format
        print(f"received message for company {company.name}")
        messages.append(company)
        yield company.domain


@app.page('/companies/')
class counter(View):
    async def get(self, request):
        return self.json({'messages': messages})

    async def post(self, request):
        body = await request.json()
        await companies_topic.send(value=body)
        return self.json({'processed': True})


@app.page('/companies/{name}')
class CompaniesStatsView(View):
    async def get(self, request, name):
        company_info = companies_stats.get(name.lower(), None)
        if company_info:
            return self.json(company_info)
        else:
            return self.notfound()


logger = logging.getLogger(__name__) # use that instead of print



