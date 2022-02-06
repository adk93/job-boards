# Standard library imports
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

# Third-party imports

# Local application imports

@dataclass
class EmploymentType:
    type: str
    salary_min: float
    salary_max: float
    currency: str


@dataclass
class Skill:
    skill_name: str

@dataclass
class JobOffer:
    job_board: str
    company: str
    city: str
    published_at: datetime.date
    job_title: str
    experience_level: str
    workplace_type: str
    link : str
    skills: List[Skill]
    employment_types: List[EmploymentType]

@dataclass
class JobOffers:
    offers: List[JobOffer] = field(default_factory=lambda: [])
