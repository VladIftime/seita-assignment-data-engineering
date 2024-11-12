import unittest
from datetime import datetime, timezone
import pandas as pd
from app.data_handler import get_forecasts, load_weather_data, evaluate_tomorrow

global WARM_THRESHOLD, SUNNY_THRESHOLD, WINDY_THRESHOLD


class TestWeatherAPI(unittest.TestCase):
    def setUp(self):
        # Sample data setup
        data = {
            "event_start": [
                datetime(2020, 11, 3, 18, 0, tzinfo=timezone.utc),
                datetime(2020, 11, 3, 18, 0, tzinfo=timezone.utc),
                datetime(2020, 11, 3, 18, 0, tzinfo=timezone.utc),
                datetime(2020, 11, 4, 7, 0, tzinfo=timezone.utc),
                datetime(2020, 11, 4, 8, 0, tzinfo=timezone.utc),
                datetime(2020, 11, 4, 9, 0, tzinfo=timezone.utc),
            ],
            "belief_horizon_in_sec": [3600, 7200, 3600, 7200, 10800, 3600],
            "event_value": [8.97, 0, 6.17, 4.55, 85.02, 6.94],
            "sensor": [
                "temperature",
                "irradiance",
                "wind speed",
                "irradiance",
                "irradiance",
                "wind speed",
            ],
        }
        self.df = pd.DataFrame(data)
        self.df["event_start"] = pd.to_datetime(self.df["event_start"])
        self.now = datetime(2020, 11, 3, 19, 0, tzinfo=timezone.utc)
        self.then = datetime(2020, 11, 3, 18, 0, tzinfo=timezone.utc)

    def test_get_forecasts(self):
        # Expected result dictionary
        expected_result = [{"temperature": 8.97, "irradiance": 0.0, "wind_speed": 6.17}]

        # Call the function
        result = get_forecasts(self.df, self.now, self.then)

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_get_forecasts_missing_data(self):
        # Modify df to exclude "wind speed" for then
        df_missing = self.df[self.df["sensor"] != "wind speed"]
        expected_result = [{"temperature": 8.97, "irradiance": 0.0, "wind_speed": -1.0}]

        # Call the function
        result = get_forecasts(df_missing, self.now, self.then)

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_get_forecasts_no_data(self):
        # Test when no data is available
        df_empty = pd.DataFrame(columns=self.df.columns)
        expected_result = [
            {"temperature": -1.0, "irradiance": -1.0, "wind_speed": -1.0}
        ]

        # Call the function
        result = get_forecasts(df_empty, self.now, self.then)

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_evaluate_tomorrow(self):
        WARM_THRESHOLD = 8.0
        SUNNY_THRESHOLD = 50.0
        WINDY_THRESHOLD = 6.0
        # Set tomorrow date relative to 'now'
        tomorrow_now = datetime(2020, 11, 2, 18, 0, tzinfo=timezone.utc)

        # Expected result: warm, sunny, windy based on thresholds
        expected_result = {"warm": False, "sunny": False, "windy": True}

        # Debug print to check thresholds and data
        print("Thresholds:", WARM_THRESHOLD, SUNNY_THRESHOLD, WINDY_THRESHOLD)
        print("Test data for tomorrow:", self.df)

        # Call the function
        result = evaluate_tomorrow(self.df, tomorrow_now)

        # Debug print to check result
        print("Function result:", result)

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_evaluate_tomorrow_not_sunny(self):
        # Modify data to ensure irradiance is below threshold
        self.df.loc[self.df["sensor"] == "irradiance", "event_value"] = 40.0

        # Expected result: not sunny, but warm and windy
        expected_result = {"warm": False, "sunny": False, "windy": True}

        # Call the function
        result = evaluate_tomorrow(self.df, self.now)

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_evaluate_tomorrow_no_data(self):
        # Test with empty DataFrame
        df_empty = pd.DataFrame(columns=self.df.columns)
        expected_result = {"warm": False, "sunny": False, "windy": False}

        # Call the function
        result = evaluate_tomorrow(df_empty, self.now)

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
