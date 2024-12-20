from pydantic import BaseModel


class Team(BaseModel):
    conference: str
    division: str
    city: str
    name: str
    full_name: str
    abbreviation: str
