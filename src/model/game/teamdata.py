from pydantic import BaseModel


class TeamData(BaseModel):
    conference: str
    division: str
    city: str
    name: str
    full_name: str
    abbreviation: str
