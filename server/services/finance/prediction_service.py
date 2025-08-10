import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any
from services.finance.yahoo_finance_service import YahooFinanceService


class PredictionService:
    def __init__(self, finance_service: YahooFinanceService):
        self.finance_service = finance_service

    def _prepare_data(self, symbol: str, period: str = "5y") -> pd.DataFrame:
        """Fetch and prepare historical data"""
        hist = self.finance_service.get_historical_data(symbol, period=period)
        if not hist or not hist.dates or not hist.prices:
            raise ValueError(f"No historical data found for {symbol}")

        df = pd.DataFrame({
            'date': hist.dates,
            'price': hist.prices
        })
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    def _parse_horizon(self, horizon_str: str) -> Tuple[datetime, int]:
        """Parse prediction horizon like 'Q4 2025' into end date and periods"""
        today = datetime.now()

        if "Q" in horizon_str.upper():
            # Quarterly prediction
            quarter, year = horizon_str.upper().split()
            quarter_num = int(quarter[1:])
            year_num = int(year)

            # Calculate quarter end date
            quarter_end_month = quarter_num * 3
            quarter_end_date = datetime(year_num, quarter_end_month, 1) + timedelta(days=-1)

            # Calculate business days between today and target
            business_days = int(np.busday_count(
                today.date(),
                quarter_end_date.date()
            ))
            return quarter_end_date, max(10, business_days)  # Minimum 10 periods

        elif "month" in horizon_str.lower():
            # Monthly prediction
            months = int(horizon_str.split()[0])
            target_date = today + timedelta(days=30 * months)
            business_days = int(np.busday_count(
                today.date(),
                target_date.date()
            ))
            return target_date, max(10, business_days)

        else:
            # Default to 3 months if parsing fails
            target_date = today + timedelta(days=90)
            return target_date, 60  # ~3 months of business days

    def predict_with_arma(self, symbol: str, horizon: str = "Q4 2025") -> Dict[str, Any]:
        """Make ARMA prediction for given symbol and horizon"""
        try:
            # 1. Prepare data
            df = self._prepare_data(symbol)

            # 2. Parse prediction horizon
            target_date, periods = self._parse_horizon(horizon)

            # 3. Fit ARIMA model (Auto Regressive Integrated Moving Average)
            # I use here ARIMA(p,d,q) where d=1 for differencing
            model = ARIMA(df['price'], order=(2, 1, 2))  # (p,d,q) parameters
            fitted_model = model.fit()

            # 4. Make prediction
            forecast = fitted_model.get_forecast(steps=periods)
            pred_mean = forecast.predicted_mean
            conf_int = forecast.conf_int()

            # 5. Prepare results
            last_historical_date = df.index[-1]
            prediction_dates = pd.date_range(
                start=last_historical_date + timedelta(days=1),
                periods=periods,
                freq='B'  # Business days
            )

            return {
                "symbol": symbol,
                "historical": {
                    "dates": df.index.tolist(),
                    "prices": df['price'].tolist()
                },
                "prediction": {
                    "dates": prediction_dates.tolist(),
                    "values": pred_mean.tolist(),
                    "confidence_lower": conf_int.iloc[:, 0].tolist(),
                    "confidence_upper": conf_int.iloc[:, 1].tolist()
                },
                "target_date": target_date,
                "current_price": df['price'].iloc[-1],
                "predicted_price": pred_mean.iloc[-1],
                "model_params": str(fitted_model.params)
            }

        except Exception as e:
            print(f"Prediction failed for {symbol}: {e}")
            raise


# Example usage:
# prediction_service = PredictionService(YahooFinanceService())
# prediction = prediction_service.predict_with_arma("AAPL", "Q4 2025")
# print(prediction)