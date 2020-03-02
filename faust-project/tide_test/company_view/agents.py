import logging

from tide_test.app import app
from tide_test.company_view.models import Company
from faust.web import Request, Response, View

companies_topic = app.topic('companies', partitions=8, value_type=Company)

messages = [] # use as in-memory data-base will be wiped on restart

@app.agent(companies_topic)
async def store_company_views(companies):
    async for company in companies:
        print(f"received message for company {company.name}")
        messages.append(company)


@app.page('/companies/')
class counter(View):
    async def get(self, request):
        return self.json({'messages': messages})

    async def post(self, request):
        body = await request.json()
        await companies_topic.send(value=body)
        return self.json({'processed': True})


logger = logging.getLogger(__name__)



