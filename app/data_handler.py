import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import List, Dict
from .config import (
    WARM_THRESHOLD,
    SUNNY_THRESHOLD,
    WINDY_THRESHOLD,
    WEATHER_DATA_FILEPATH,
)


def load_weather_data(filepath: str = WEATHER_DATA_FILEPATH) -> pd.DataFrame:
    """
    Load weather data from a CSV file into a pandas DataFrame.

    This function reads a CSV file specified by the `filepath` parameter,
    parses the 'event_start' column as datetime. The 'event_start'
    column is then converted to UTC timezone.

    Args:
        filepath (str): The path to the CSV file containing the weather data.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the loaded weather data.
    """
    # Load CSV into a DataFrame with parsed datetime for 'event_start'
    df = pd.read_csv(
        filepath,
    )
    df["event_start"] = pd.to_datetime(df["event_start"], errors="coerce")

    return df


def get_forecasts(df: pd.DataFrame, now: datetime, then: datetime) -> List[Dict]:
    """
    Get the three most recent forecasts for temperature, irradiance, and wind speed.

    Parameters:
        df (pd.DataFrame): DataFrame containing weather data.
        now (datetime): The current datetime (must be UTC).
        then (datetime): The datetime up to which forecasts are considered.

    Returns:
        List[Dict[str, float]]: A list containing a dictionary with the most recent forecasts for each sensor.

    Notes:
        - If no data is available for a sensor, its value is set to -1.0.
    """
    # Ensure 'now' and 'then' are timezone-aware
    now = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
    then = then if then.tzinfo else then.replace(tzinfo=timezone.utc)

    # Define sensors of interest and default forecast values
    sensors = {"temperature", "irradiance", "wind speed"}
    default_forecast = {"temperature": -1.0, "irradiance": -1.0, "wind_speed": -1.0}

    # Filter the data for the time range up to 'then' and relevant sensors
    filtered_data = df[(df["event_start"] <= then) & (df["sensor"].isin(sensors))]

    # Filter forecasts that were made available by 'now'
    filtered_data = filtered_data[
        (
            filtered_data["event_start"]
            - pd.to_timedelta(filtered_data["belief_horizon_in_sec"], unit="s")
        )
        <= now
    ]

    # For each sensor, select the forecast with the smallest belief horizon for 'then'
    most_recent_forecasts = (
        filtered_data.sort_values(
            by=["sensor", "event_start", "belief_horizon_in_sec"],
            ascending=[True, False, True],
        )
        .groupby("sensor")
        .first()
    )

    # Convert to dictionary and rename sensors
    forecast_values = {
        key.replace(" ", "_"): value
        for key, value in most_recent_forecasts["event_value"].to_dict().items()
    }

    # Update default forecast with available values
    forecasts = {**default_forecast, **forecast_values}

    return [forecasts]


def evaluate_tomorrow(df: pd.DataFrame, now: datetime) -> dict:
    """
    Determine if tomorrow's forecast meets conditions for 'warm', 'sunny', and 'windy'.

    Parameters:
        df (pd.DataFrame): DataFrame containing forecast data.
        now (datetime): The current datetime (must be UTC).

    Returns:
        dict: A dictionary with keys "warm", "sunny", and "windy" indicating whether
              the conditions are met for tomorrow based on predefined thresholds.

    Notes:
        - Thresholds are defined for each condition.
        - Returns False if no data is available.
    """
    # Ensure 'now' is timezone-aware
    now = now if now.tzinfo else now.replace(tzinfo=timezone.utc)

    # If the DataFrame is empty, return default conditions
    if df.empty:
        return {"warm": False, "sunny": False, "windy": False}

    # Determine tomorrow's date and filter forecasts for that date
    tomorrow_date = (now + timedelta(days=1)).date()
    tomorrow_forecasts = df[df["event_start"].dt.date == tomorrow_date]

    # Debugging information to confirm filtering
    print("Evaluating for tomorrow's date:", tomorrow_date)
    print("Filtered forecasts for tomorrow:", tomorrow_forecasts)

    # Separate forecasts by sensor type for tomorrow
    temperature_forecasts = tomorrow_forecasts[
        tomorrow_forecasts["sensor"] == "temperature"
    ]
    irradiance_forecasts = tomorrow_forecasts[
        tomorrow_forecasts["sensor"] == "irradiance"
    ]
    wind_speed_forecasts = tomorrow_forecasts[
        tomorrow_forecasts["sensor"] == "wind speed"
    ]

    # Evaluate conditions based on thresholds
    warm = (
        any(temperature_forecasts["event_value"] >= WARM_THRESHOLD)
        if not temperature_forecasts.empty
        else False
    )
    sunny = (
        any(irradiance_forecasts["event_value"] >= SUNNY_THRESHOLD)
        if not irradiance_forecasts.empty
        else False
    )
    windy = (
        any(wind_speed_forecasts["event_value"] >= WINDY_THRESHOLD)
        if not wind_speed_forecasts.empty
        else False
    )

    # Debugging outputs to check conditions
    print("Temperature forecasts for tomorrow:", temperature_forecasts)
    print("Irradiance forecasts for tomorrow:", irradiance_forecasts)
    print("Wind speed forecasts for tomorrow:", wind_speed_forecasts)
    print("Result - Warm:", warm, "Sunny:", sunny, "Windy:", windy)

    return {"warm": warm, "sunny": sunny, "windy": windy}
