<!-- Write the README -->

## Setup

1. **Clone the repository:**
    ```sh
    git clone https://github.com/VladIftime/seita-assignment-data-engineering.git
    cd seita-assignment-data-engineering
    ```

2. **Create a virtual environment:**
    ```sh
    python -m venv seita_assignment_env
    source seita_assignment_env/bin/activate  # On Windows use `seita_assignment_env\Scripts\activate`
    ```

3. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

## Running the API

1. **Start the FastAPI server:**
    ```sh
    uvicorn app.main:app --reload
    ```

2. **Access the API documentation:**
    Open your browser and go to `http://127.0.0.1:8000/docs` to see the interactive API documentation.

## Endpoints

### Get Forecasts

- **Endpoint:** `/forecasts`
- **Method:** `GET`
- **Parameters:**
  - `now` (datetime): The current datetime.
  - `then` (datetime): The datetime up to which forecasts are considered.
- **Response:** A list of dictionaries containing the most recent forecasts for each sensor.

### Evaluate Tomorrow

- **Endpoint:** `/tomorrow`
- **Method:** `GET`
- **Parameters:**
  - `now` (datetime): The current datetime.
- **Response:** A dictionary with keys "warm", "sunny", and "windy" indicating whether the conditions are met for tomorrow based on predefined thresholds.

## Configuration

- **Thresholds:** The thresholds for warm, sunny, and windy conditions are defined in `app/config.py`.
- **Weather Data File:** The path to the weather data CSV file is specified in `app/config.py`.

## TODO

Test for scalability. Use tools like `timeit` or `Locust` to make sure functions perform well under expected loads.

## License

This project is licensed under the MIT License.
