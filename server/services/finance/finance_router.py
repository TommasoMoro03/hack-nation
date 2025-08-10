import json
from typing import List, Dict, Any
from datetime import datetime, timedelta

from services.finance.prediction_service import PredictionService
from services.finance.yahoo_finance_service import YahooFinanceService
from utils.prompts import FINANCE_INTENT_PROMPT


class SmartFinanceRouter:
    def __init__(self, finance_service: YahooFinanceService, rag_service, llm):
        self.finance_service = finance_service
        self.rag_service = rag_service
        self.llm = llm
        self.prediction_service = PredictionService(finance_service)

    def classify_intent(self, question: str) -> Dict[str, Any]:
        prompt = FINANCE_INTENT_PROMPT.format(question=question)
        try:
            resp = self.llm.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"}
            )
            response_content = resp.choices[0].message.content

            # Basic validation
            if not response_content.strip():
                raise ValueError("Empty response from LLM")

            parsed = json.loads(response_content)

            # Validate structure
            if not all(key in parsed for key in ["intent", "symbols", "time_period"]):
                raise ValueError("Missing required keys in response")

            return parsed

        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response: {e}\nResponse was: {response_content}")
            return {"intent": "fallback", "symbols": [], "time_period": ""}
        except Exception as e:
            print(f"Error in intent classification: {e}")
            return {"intent": "fallback", "symbols": [], "time_period": ""}

    def generate_market_summary_pie_chart(self) -> Dict[str, Any]:
        indices = ['^GSPC', '^DJI', '^IXIC', '^VIX']
        data = []
        total_market_cap = 0

        for idx in indices:
            stock = self.finance_service.get_stock_info(idx)
            print(f"Indice {idx} - Market Cap: {stock.market_cap if stock else 'N/A'}")
            if stock and stock.market_cap:
                data.append({
                    "company": stock.symbol,
                    "share": stock.market_cap,
                    "value": stock.market_cap
                })
                total_market_cap += stock.market_cap

        for d in data:
            d["share"] = round(100 * d["value"] / total_market_cap, 2)

        content = "Market summary pie chart of major indices based on market capitalization."

        chart = {
            "id": "market-share",
            "type": "pie",
            "title": "Market Share Distribution",
            "data": data,
            "dataKeys": ["share"],
            "colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"]
        }

        return {"content": content, "charts": [chart]}

    def generate_multi_line_chart(self, symbols: List[str], time_period: str = "3mo") -> Dict[str, Any]:

        all_series = []
        x_keys = None

        for symbol in symbols:
            hist = self.finance_service.get_historical_data(symbol, period=time_period)
            print(f"Historical data for {symbol}")
            print(f"Dates: {hist.dates if hist else 'N/A'}")
            if hist:
                # X keys per date
                if x_keys is None:
                    x_keys = hist.dates
                all_series.append({
                    "id": symbol,
                    "data": [{"date": d, "value": p} for d, p in zip(hist.dates, hist.prices)],
                    "color": None  # si può mappare a palette
                })

        if not all_series or not x_keys:
            return {"content": "No historical data found for the specified symbols.", "charts": []}

        # Costruisco dati per line chart: array di dict con una chiave per data e per simboli
        chart_data = []
        for i, date in enumerate(x_keys):
            point = {"date": date}
            for series in all_series:
                point[series["id"]] = series["data"][i]["value"]
            chart_data.append(point)

        content = f"Multi line chart showing performance of {', '.join(symbols)} over {time_period}."

        chart = {
            "id": "multi-company-trend",
            "type": "line",
            "title": "Performance Over Time",
            "data": chart_data,
            "xKey": "date",
            "yKey": None,
            "dataKeys": symbols,
            "colors": ["#8884d8", "#82ca9d", "#ffc658", "#d0ed57"][:len(symbols)],
            "timeRange": time_period
        }

        return {"content": content, "charts": [chart]}

    def generate_prediction_chart(self, symbol: str, horizon: str) -> Dict[str, Any]:
        """Generate prediction chart with historical and forecast data"""
        prediction = self.prediction_service.predict_with_arma(symbol, horizon)

        # Combine historical and prediction data for the chart
        chart_data = []
        for i, date in enumerate(prediction["historical"]["dates"]):
            chart_data.append({
                "date": date,
                "value": prediction["historical"]["prices"][i],
                "type": "historical"
            })

        for i, date in enumerate(prediction["prediction"]["dates"]):
            chart_data.append({
                "date": date,
                "value": prediction["prediction"]["values"][i],
                "type": "prediction",
                "confidence_lower": prediction["prediction"]["confidence_lower"][i],
                "confidence_upper": prediction["prediction"]["confidence_upper"][i]
            })

        content = (f"Prediction for {symbol}: Current price ${prediction['current_price']:.2f}, "
                   f"predicted price ${prediction['predicted_price']:.2f} by {horizon}.")

        chart = {
            "id": "price-prediction",
            "type": "line",
            "title": f"{symbol} Price Prediction",
            "data": chart_data,
            "xKey": "date",
            "yKey": "value",
            "dataKeys": ["value"],
            "colors": ["#8884d8"],
            "confidenceBand": True,
            "timeRange": "custom"
        }

        return {
            "content": content,
            "charts": [chart],
            "prediction_details": prediction
        }

    def route_query(self, question: str) -> Dict[str, Any]:
        print("Qui ci enttro?")
        intent_data = self.classify_intent(question)
        intent = intent_data.get("intent", "fallback")
        symbols = intent_data.get("symbols", [])
        time_period = intent_data.get("time_period", "3mo")

        if intent == "market_summary":
            return self.generate_market_summary_pie_chart()

        elif intent == "multi_company_trend" and symbols:
            return self.generate_multi_line_chart(symbols, time_period)

        elif intent == "prediction" and symbols:
            return self.generate_prediction_chart(symbols[0], time_period)

        else:
            # fallback testuale (usa RAG)
            explanation = self.rag_service.query(question)
            return {"content": explanation, "charts": []}
