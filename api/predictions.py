"""
Air quality prediction module using Prophet for time series forecasting.
"""

import logging
from typing import List, Optional

import pandas as pd
from openaq import OpenAQ
from prophet import Prophet

from api.models import ParameterPrediction, PredictionPoint

# Suppress Prophet's verbose logging
logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)


class AirQualityPredictor:
    """Air quality predictor using Facebook Prophet."""

    def __init__(self, client: OpenAQ):
        self.client = client
        self.min_data_points = 10  # Minimum historical data points needed

    def predict_parameter_from_data(
        self,
        historical_data: pd.DataFrame,
        parameter_name: str,
        parameter_unit: str,
        forecast_hours: int = 24,
        confidence_interval: float = 0.8,
    ) -> Optional[ParameterPrediction]:
        """
        Generate predictions from pre-fetched historical data.

        Args:
            historical_data: DataFrame with timestamp and value columns
            parameter_name: Name of the parameter (e.g., 'pm25', 'no2')
            parameter_unit: Unit of the parameter (e.g., 'µg/m³', 'ppm')
            forecast_hours: Hours to forecast ahead
            confidence_interval: Confidence interval for predictions (0.8 = 80%)

        Returns:
            ParameterPrediction object or None if prediction fails
        """
        try:
            if historical_data.empty or len(historical_data) < self.min_data_points:
                print(
                    f"Insufficient data for parameter {parameter_name}: {len(historical_data)} points"
                )
                return None

            # Remove outliers from the provided data
            cleaned_data = self._remove_outliers(historical_data)

            # Prepare data for Prophet
            df = self._prepare_prophet_data(cleaned_data)

            if df.empty:
                return None

            # Create and fit Prophet model
            model = self._create_prophet_model()
            model.fit(df)

            # Generate future dates
            future = model.make_future_dataframe(periods=forecast_hours, freq="h")

            # Make predictions
            forecast = model.predict(future)

            # Extract predictions for the forecast period
            prediction_points = self._extract_predictions(
                forecast, forecast_hours, confidence_interval
            )

            return ParameterPrediction(
                parameter_name=parameter_name,
                unit=parameter_unit,
                model_type="Prophet",
                forecast_hours=forecast_hours,
                predictions=prediction_points,
                confidence_interval=confidence_interval,
                training_data_points=len(df),
            )

        except Exception as e:
            print(f"Error predicting for parameter {parameter_name}: {e}")
            return None

    def _prepare_prophet_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data in Prophet's required format (ds, y)."""
        if df.empty:
            return pd.DataFrame()

        prophet_df = pd.DataFrame({"ds": df["timestamp"], "y": df["value"]})

        # Remove timezone information (Prophet requires timezone-naive timestamps)
        prophet_df["ds"] = pd.to_datetime(prophet_df["ds"]).dt.tz_localize(None)

        # Remove any NaN values
        prophet_df = prophet_df.dropna()

        return prophet_df

    def _create_prophet_model(self) -> Prophet:
        """Create a Prophet model with appropriate settings for air quality data."""
        return Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False,  # Not enough data for yearly patterns
            seasonality_mode="additive",
            interval_width=0.8,  # 80% confidence interval
            changepoint_prior_scale=0.05,  # Conservative approach to trend changes
            seasonality_prior_scale=10.0,  # Allow for seasonal patterns
            holidays_prior_scale=10.0,
            mcmc_samples=0,  # Use MAP estimation for speed
            uncertainty_samples=1000,
        )

    def _extract_predictions(
        self, forecast: pd.DataFrame, forecast_hours: int, confidence_interval: float
    ) -> List[PredictionPoint]:
        """Extract prediction points from Prophet forecast."""
        # Get the last N predictions (forecast period)
        predictions = forecast.tail(forecast_hours)

        prediction_points = []
        for _, row in predictions.iterrows():
            # Ensure non-negative predictions for air quality parameters
            predicted_value = max(0, row["yhat"])
            lower_bound = max(0, row["yhat_lower"]) if "yhat_lower" in row else None
            upper_bound = max(0, row["yhat_upper"]) if "yhat_upper" in row else None

            prediction_points.append(
                PredictionPoint(
                    timestamp=row["ds"].isoformat(),
                    predicted_value=round(predicted_value, 3),
                    lower_bound=round(lower_bound, 3)
                    if lower_bound is not None
                    else None,
                    upper_bound=round(upper_bound, 3)
                    if upper_bound is not None
                    else None,
                )
            )

        return prediction_points

    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove statistical outliers from the data."""
        if df.empty or len(df) < 3:
            return df

        # Calculate IQR-based outlier bounds
        Q1 = df["value"].quantile(0.25)
        Q3 = df["value"].quantile(0.75)
        IQR = Q3 - Q1

        # Define outlier bounds (1.5 * IQR is standard)
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # For air quality, lower bound should be at least 0
        lower_bound = max(0, lower_bound)

        # Filter out outliers
        filtered_df = df[
            (df["value"] >= lower_bound) & (df["value"] <= upper_bound)
        ].copy()

        return filtered_df

    @staticmethod
    def measurements_to_dataframe(measurements_response) -> pd.DataFrame:
        """
        Convert OpenAQ measurements response to pandas DataFrame.

        Args:
            measurements_response: OpenAQ measurements response object

        Returns:
            DataFrame with timestamp and value columns
        """
        data = []
        for measurement in measurements_response.results:
            data.append(
                {
                    "timestamp": measurement.period.datetime_to.utc,
                    "value": measurement.value,
                }
            )

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)
        df = df.sort_values("timestamp").reset_index(drop=True)

        return df
