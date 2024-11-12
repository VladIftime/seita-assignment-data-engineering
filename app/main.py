from fastapi import FastAPI, HTTPException, Query
from datetime import datetime
from typing import List
from .schemas import ForecastResponse
from .data_handler import load_weather_data, get_forecasts, evaluate_tomorrow

app = FastAPI(title="Seita Weather Forecast API")
weather_df = load_weather_data()


@app.get("/forecasts", response_model=List[ForecastResponse])
async def get_forecasts_endpoint(now: datetime, then: datetime):
    if now < then:
        raise HTTPException(
            status_code=400, detail="`now` should not be earlier than `then`."
        )
    forecasts = get_forecasts(weather_df, now, then)
    if not forecasts:
        raise HTTPException(
            status_code=404,
            detail="No forecasts available for the specified `then` time.",
        )
    return forecasts


@app.get("/tomorrow", response_model=dict)
async def get_tomorrow(now: datetime):
    tomorrow_conditions = evaluate_tomorrow(weather_df, now)
    return tomorrow_conditions
