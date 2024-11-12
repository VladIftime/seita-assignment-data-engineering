from pydantic import BaseModel


class ForecastResponse(BaseModel):
    temperature: float
    irradiance: float
    wind_speed: float
