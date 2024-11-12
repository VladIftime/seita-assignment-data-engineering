from fastapi import FastAPI, HTTPException, Query
from datetime import datetime
from typing import List
from .schemas import ForecastResponse
from .data_handler import load_weather_data, get_forecasts, evaluate_tomorrow

app = FastAPI(title="Seita Weather Forecast API")
weather_df = load_weather_data()


@app.get("/forecasts", response_model=List[ForecastResponse])
async def get_forecasts_endpoint(now: datetime, then: datetime):
    """
    Get the three most recent forecasts for temperature, irradiance, and wind speed.

    Parameters:
        df (pd.DataFrame): A DataFrame containing weather data with columns:
                           - "event_start" (datetime): The datetime of the forecasted event.
                           - "belief_horizon_in_sec" (int): How long ago (in seconds) the forecast was made.
                           - "event_value" (float): The forecasted value.
                           - "sensor" (str): The type of sensor data ("temperature", "irradiance", "wind speed").
        now (datetime): The datetime when the forecast is requested (must be UTC).
        then (datetime): The datetime for which forecasts are considered.

    Returns:
        List[Dict[str, float]]: A dictionary with the most recent forecasted values for each sensor.

    Raises:
        HTTPException: If input data is missing or in an incorrect format.

    Notes:
        - If no data is available for a specific sensor, the function will return -1.0 for that sensor.
        - The function filters for only relevant sensor types ("temperature", "irradiance", "wind speed").
    """
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
    """
    Determines if tomorrow is expected to meet "warm", "sunny", and "windy" conditions.

    Parameters:
        df (pd.DataFrame): A DataFrame with forecast data, including columns:
                           - "event_start" (datetime): The datetime of the forecasted event.
                           - "event_value" (float): The forecasted value.
                           - "sensor" (str): The type of sensor data ("temperature", "irradiance", "wind speed").
        now (datetime): The datetime to calculate tomorrow's date (must be UTC).

    Returns:
        dict: A dictionary with Boolean keys indicating if conditions are met:
              - "warm": True if temperature meets the warm threshold.
              - "sunny": True if irradiance meets the sunny threshold.
              - "windy": True if wind speed meets the windy threshold.

    Raises:
        HTTPException: If input data is missing or in an incorrect format.

    Notes:
        - Thresholds for each condition can be adjusted based on requirements.
        - Function returns False for a condition if no relevant data is available.
    """
    tomorrow_conditions = evaluate_tomorrow(weather_df, now)
    return tomorrow_conditions
