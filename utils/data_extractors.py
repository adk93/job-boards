# Standard library imports
from datetime import datetime

# Local application imports
from data import JobOffer, Skill, EmploymentType, JobOffers

NO_DATA_STRING = "N/A"

def just_join_it_data_extractor(parse_results, job_offers: JobOffers, company) -> None:
    for offer in parse_results:
        skills = []
        for skill_set in offer.get("skills", []):
            skill = Skill(skill_set.get("name"))
            skills.append(skill)

        employment_types = []
        for e_type in offer.get("employment_types", [{}]):
            salary_type = e_type.get("type").upper()
            salary = e_type.get("salary")
            salary_from = NO_DATA_STRING if salary is None else salary.get("from")
            salary_to = NO_DATA_STRING if salary is None else salary.get("to")
            salary_currency = NO_DATA_STRING if salary is None else salary.get("currency")

            employment_type = EmploymentType(salary_type,
                                             salary_from,
                                             salary_to,
                                             salary_currency)
            employment_types.append(employment_type)

        job_offer = JobOffer("justjoin.it",
                             offer.get("company_name"),
                             offer.get("city"),
                             offer.get("published_at"),
                             offer.get("title"),
                             offer.get("experience_level"),
                             offer.get("workplace_type"),
                             "https://justjoin.it/offers" + str(offer.get("id")),
                             skills,
                             employment_types)
        job_offers.offers.append(job_offer)


def jobs_for_geek_extractor(parse_results, job_offers: JobOffers, company: str) -> None:
    company_offers = filter(lambda x: True if company in x.get('companyName') else False, parse_results)
    for offer in company_offers:
        skills = []
        for skill_set in offer.get("skills", []):
            skill = Skill(skill_set)
            skills.append(skill)

        employment_types = [EmploymentType("B2B", offer.get("b2bSalaryFrom"),
                                           offer.get("b2bSalaryTo"), "PLN"),
                            EmploymentType("UOP", offer.get("employmentSalaryFrom"),
                                           offer.get("employmentSalaryTo"), "PLN")]

        job_offer = JobOffer("jobsforgeek.com",
                             offer.get("companyName"),
                             offer.get("city"),
                             offer.get("publishedTime"),
                             offer.get("jobTitle"),
                             NO_DATA_STRING,
                             offer.get("remoteType"),
                             "https://jobsforgeek.com/job-offers/details" + str(offer.get("id")),
                             skills,
                             employment_types)
        job_offers.offers.append(job_offer)


def no_fluff_jobs_extractor(parse_results, job_offers: JobOffers, company: str) -> None:
    for offer in parse_results.get("postings"):

        job_offer = JobOffer("nofluffjobs.com",
                             offer.get("name"),
                             NO_DATA_STRING,
                             datetime.utcfromtimestamp(int(offer.get("posted"))/1000).strftime("%Y-%m-%d"),
                             offer.get("title"),
                             offer.get("seniority")[0],
                             "Remote",
                             "https://nofluffjobs.com/pl/job/" + str(offer.get('url')),
                             [Skill("no skill")],
                             [EmploymentType(offer.get("salary").get("type").upper(),
                                             offer.get("salary").get("from"),
                                             offer.get("salary").get("to"),
                                             offer.get("salary").get("currency"))]
                             )
        job_offers.offers.append(job_offer)

def the_protocol_extractor(parse_results, job_offers: JobOffers, company: str) -> None:
    for offer in parse_results.get("offers"):

        s = offer.get("salary", {"type": "B2B",
                                 "from": NO_DATA_STRING,
                                 "to": NO_DATA_STRING,
                                 "currency": NO_DATA_STRING})

        e_type = EmploymentType("B2B",
                                0,
                                s.get("to", NO_DATA_STRING),
                                s.get("currency", NO_DATA_STRING))

        job_offer = JobOffer(
            "theprotocol.it",
            offer.get("employer"),
            offer.get("workplace", [{'location':NO_DATA_STRING}])[0].get("location", NO_DATA_STRING),
            offer.get("publicationDateUtc"),
            offer.get("title"),
            offer.get("positionLevels", [{'value': NO_DATA_STRING}])[0].get("value", NO_DATA_STRING),
            ",".join(offer.get("workModes", [NO_DATA_STRING])),
            "https://theprotocol.it/szczegoly/praca/" + offer.get("offerUrlName"),
            [Skill(s) for s in offer.get("technologies", [NO_DATA_STRING])],
            [e_type]
        )

        job_offers.offers.append(job_offer)

