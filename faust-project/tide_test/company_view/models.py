import faust


class Company(faust.Record):
    name: str
    domain: str
