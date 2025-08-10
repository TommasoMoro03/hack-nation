import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from openai import OpenAI
import time

from core.config import settings
from services.answering.rag_service import RAGService
from services.finance.yahoo_finance_service import YahooFinanceService
from services.finance.finance_router import SmartFinanceRouter  # Import the SmartFinanceRouter


@dataclass
class QueryAnalysis:
    """Result of query analysis"""
    query_type: str  # 'rag', 'finance', 'mixed'
    confidence: float
    symbols: List[str]
    is_prediction: bool
    is_quantitative: bool
    reasoning: str


@dataclass
class RouterResult:
    """Result of query routing"""
    source: str  # 'rag', 'finance', 'mixed'
    answer: str
    sent_analysis: Optional[str]
    data: Optional[Dict[str, Any]] = None
    processing_time: float = 0.0
    charts: Optional[List[Dict[str, Any]]] = None  # Add charts field for visualization


class QueryRouter:
    """
    Intelligent router that analyzes queries and routes them to appropriate data sources:
    - RAG (PDFs) for qualitative analysis
    - Yahoo Finance for quantitative data and predictions
    - Mixed for queries requiring both sources
    """

    def __init__(self):
        self.rag_service = RAGService()
        self.finance_service = YahooFinanceService()
        self.logger = logging.getLogger(__name__)

        # Initialize OpenAI client for query analysis
        try:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            # Initialize SmartFinanceRouter with the required services
            self.smart_finance_router = SmartFinanceRouter(
                finance_service=self.finance_service,
                rag_service=self.rag_service,
                llm=self.openai_client
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            self.openai_client = None
            self.smart_finance_router = None

    def route_query(self, question: str, selected_documents: Optional[List[str]] = None) -> RouterResult:
        """
        Route a query to the appropriate data source
        """
        import time
        start_time = time.time()

        try:
            # Step 1: Analyze the query
            analysis = self._analyze_query(question)

            self.logger.info(f"Query analysis: {analysis.query_type} (confidence: {analysis.confidence:.2f})")

            # Step 2: Route based on analysis
            if analysis.query_type == 'rag':
                return self._handle_rag_query(question, selected_documents, start_time)

            elif analysis.query_type == 'finance':
                return self._handle_finance_query(question, analysis, start_time)

            elif analysis.query_type == 'mixed':
                return self._handle_mixed_query(question, selected_documents, analysis, start_time)

            else:
                # Default to RAG
                return self._handle_rag_query(question, selected_documents, start_time)

        except Exception as e:
            self.logger.error(f"Query routing failed: {str(e)}")
            processing_time = time.time() - start_time
            return RouterResult(
                source='error',
                answer="I encountered an error while processing your query. Please try again.",
                sent_analysis=None,
                processing_time=processing_time
            )

    def _analyze_query(self, question: str) -> QueryAnalysis:
        """Analyze query to determine the best data source"""

        # Simple keyword-based analysis as fallback
        if not self.openai_client:
            return self._simple_analysis(question)

        try:
            # Use LLM for sophisticated analysis
            prompt = f"""
Analyze this financial query and determine the best data source to answer it.

Query: "{question}"

Consider:
- RAG (PDFs): For qualitative analysis, company strategies, reports, qualitative insights
- Finance API: For current prices, quantitative data, predictions, market data, stock prices, charts, trends
- Mixed: For queries requiring both qualitative and quantitative information

Also consider if the query is asking for:
- Visual representation (charts, graphs)
- Market summaries
- Multi-company comparisons
- Historical trends

Respond with JSON only:
{{
    "query_type": "rag|finance|mixed",
    "confidence": 0.0-1.0,
    "symbols": ["AAPL", "GOOGL"],
    "is_prediction": true/false,
    "is_quantitative": true/false,
    "reasoning": "explanation"
}}
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            import json
            result = json.loads(response.choices[0].message.content.strip())

            return QueryAnalysis(
                query_type=result.get('query_type', 'rag'),
                confidence=result.get('confidence', 0.5),
                symbols=result.get('symbols', []),
                is_prediction=result.get('is_prediction', False),
                is_quantitative=result.get('is_quantitative', False),
                reasoning=result.get('reasoning', '')
            )

        except Exception as e:
            self.logger.error(f"LLM analysis failed: {str(e)}")
            return self._simple_analysis(question)

    def _simple_analysis(self, question: str) -> QueryAnalysis:
        """Simple keyword-based query analysis"""
        question_lower = question.lower()

        # Keywords for finance API (expanded to include chart/visualization keywords)
        finance_keywords = [
            'price', 'stock', 'market', 'trading', 'prediction', 'forecast',
            'current', 'real-time', 'live', 'quote', 'chart', 'trend',
            'volume', 'market cap', 'pe ratio', 'dividend', 'earnings',
            'technical', 'fundamental', 'analyst', 'target price',
            'compare', 'comparison', 'performance', 'historical', 'graph',
            'visualization', 'pie chart', 'line chart', 'summary'
        ]

        # Keywords for RAG
        rag_keywords = [
            'strategy', 'business model', 'competitive', 'risk', 'opportunity',
            'management', 'leadership', 'product', 'service', 'customer',
            'revenue', 'growth', 'expansion', 'acquisition', 'merger',
            'report', 'filing', 'annual', 'quarterly', '10-k', '10-q'
        ]

        # Extract stock symbols
        symbols = re.findall(r'\b[A-Z]{1,5}\b', question.upper())

        # Count matches
        finance_score = sum(1 for keyword in finance_keywords if keyword in question_lower)
        rag_score = sum(1 for keyword in rag_keywords if keyword in question_lower)

        # Determine query type
        if finance_score > rag_score and finance_score > 0:
            query_type = 'finance'
            confidence = min(0.9, finance_score / 5)
        elif rag_score > finance_score and rag_score > 0:
            query_type = 'rag'
            confidence = min(0.9, rag_score / 5)
        elif symbols:
            query_type = 'finance'
            confidence = 0.7
        else:
            query_type = 'rag'
            confidence = 0.5

        return QueryAnalysis(
            query_type=query_type,
            confidence=confidence,
            symbols=symbols,
            is_prediction='prediction' in question_lower or 'forecast' in question_lower,
            is_quantitative=finance_score > 0,
            reasoning=f"Keyword analysis: finance={finance_score}, rag={rag_score}, symbols={symbols}"
        )

    def _handle_rag_query(self, question: str, selected_documents: Optional[List[str]],
                          start_time: float) -> RouterResult:
        """Handle RAG-based query"""
        try:
            result = self.rag_service.process_query(question, selected_documents)
            processing_time = time.time() - start_time

            return RouterResult(
                source='rag',
                answer=result.answer,
                sent_analysis=result.sent_analysis,
                data={
                    'chunks_used': result.chunks_used,
                    'filter_applied': result.filter_applied
                },
                processing_time=processing_time
            )
        except Exception as e:
            self.logger.error(f"RAG query failed: {str(e)}")
            processing_time = time.time() - start_time
            return RouterResult(
                source='rag',
                answer="I couldn't find relevant information in the documents for your question.",
                sent_analysis=None,
                processing_time=processing_time
            )

    def _handle_finance_query(self, question: str, analysis: QueryAnalysis, start_time: float) -> RouterResult:
        """Handle finance API query with SmartFinanceRouter integration"""
        try:
            # Use SmartFinanceRouter if available for enhanced finance handling
            if self.smart_finance_router:
                smart_result = self.smart_finance_router.route_query(question)
                print("SmartFinanceRouter result:", smart_result)
                processing_time = time.time() - start_time

                return RouterResult(
                    source='finance',
                    answer=smart_result.get('content', 'No content available'),
                    sent_analysis=None,
                    charts=smart_result.get('charts', []),
                    data={
                        'symbols': analysis.symbols,
                        'query_analysis': {
                            'is_prediction': analysis.is_prediction,
                            'is_quantitative': analysis.is_quantitative,
                            'confidence': analysis.confidence
                        }
                    },
                    processing_time=processing_time
                )

            # Fallback to original finance handling if SmartFinanceRouter not available
            return self._fallback_finance_query(question, analysis, start_time)

        except Exception as e:
            self.logger.error(f"Finance query failed: {str(e)}")
            return self._fallback_finance_query(question, analysis, start_time)

    def _fallback_finance_query(self, question: str, analysis: QueryAnalysis, start_time: float) -> RouterResult:
        """Fallback finance query handling (original implementation)"""
        try:
            if analysis.symbols:
                # Get data for specific symbols
                stock_data = self.finance_service.get_multiple_stocks(analysis.symbols)

                if stock_data:
                    # Generate answer using LLM
                    answer = self._generate_finance_answer(question, stock_data, analysis)

                    processing_time = time.time() - start_time
                    return RouterResult(
                        source='finance',
                        answer=answer,
                        sent_analysis=None,
                        data={
                            'symbols': list(stock_data.keys()),
                            'stock_data': {k: {
                                'price': v.current_price,
                                'change': v.change,
                                'change_percent': v.change_percent
                            } for k, v in stock_data.items()}
                        },
                        processing_time=processing_time
                    )

            # Fallback to market summary
            market_summary = self.finance_service.get_market_summary()
            answer = self._generate_market_answer(question, market_summary)

            processing_time = time.time() - start_time
            return RouterResult(
                source='finance',
                answer=answer,
                sent_analysis=None,
                data={'market_summary': market_summary},
                processing_time=processing_time
            )

        except Exception as e:
            self.logger.error(f"Fallback finance query failed: {str(e)}")
            processing_time = time.time() - start_time
            return RouterResult(
                source='finance',
                answer="I couldn't retrieve the financial data you requested. Please try again.",
                sent_analysis=None,
                processing_time=processing_time
            )

    def _handle_mixed_query(self, question: str, selected_documents: Optional[List[str]], analysis: QueryAnalysis,
                            start_time: float) -> RouterResult:
        """Handle mixed query requiring both sources"""
        try:
            # Get RAG answer
            rag_result = self.rag_service.process_query(question, selected_documents)

            # Get finance data/charts if available
            charts = []
            finance_content = ""

            if self.smart_finance_router:
                try:
                    smart_result = self.smart_finance_router.route_query(question)
                    charts = smart_result.get('charts', [])
                    finance_content = smart_result.get('content', '')
                except Exception as e:
                    self.logger.warning(f"SmartFinanceRouter failed in mixed query: {str(e)}")

            # Get basic finance data if symbols are mentioned and no charts were generated
            finance_data = {}
            if analysis.symbols and not charts:
                finance_data = self.finance_service.get_multiple_stocks(analysis.symbols)

            # Combine answers
            combined_answer = self._combine_answers(
                rag_result.answer,
                finance_data,
                question,
                finance_content
            )

            processing_time = time.time() - start_time
            return RouterResult(
                source='mixed',
                answer=combined_answer,
                sent_analysis=rag_result.sent_analysis,
                charts=charts,
                data={
                    'rag_chunks': rag_result.chunks_used,
                    'finance_symbols': list(finance_data.keys()) if finance_data else analysis.symbols
                },
                processing_time=processing_time
            )

        except Exception as e:
            self.logger.error(f"Mixed query failed: {str(e)}")
            processing_time = time.time() - start_time
            return RouterResult(
                source='mixed',
                answer="I encountered an error while processing your query. Please try again.",
                sent_analysis=None,
                processing_time=processing_time
            )

    def _generate_finance_answer(self, question: str, stock_data: Dict, analysis: QueryAnalysis) -> str:
        """Generate answer for finance queries using LLM"""
        try:
            if not self.openai_client:
                return self._simple_finance_answer(stock_data)

            # Prepare stock data for LLM
            stock_info = []
            for symbol, data in stock_data.items():
                stock_info.append(
                    f"{symbol}: ${data.current_price:.2f} ({data.change:+.2f}, {data.change_percent:+.2f}%)")

            prompt = f"""
Based on the following stock data, answer the user's question.

Stock Data:
{chr(10).join(stock_info)}

Question: {question}

Provide a clear, accurate answer based on the current market data.
"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful financial analyst. Provide accurate information based on the stock data provided."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            self.logger.error(f"LLM finance answer generation failed: {str(e)}")
            return self._simple_finance_answer(stock_data)

    def _simple_finance_answer(self, stock_data: Dict) -> str:
        """Simple finance answer without LLM"""
        if not stock_data:
            return "I couldn't retrieve the requested stock data."

        answer_parts = []
        for symbol, data in stock_data.items():
            answer_parts.append(
                f"{symbol} is currently trading at ${data.current_price:.2f} "
                f"({data.change:+.2f}, {data.change_percent:+.2f}%)"
            )

        return " | ".join(answer_parts)

    def _generate_market_answer(self, question: str, market_summary: Dict) -> str:
        """Generate answer for market summary queries"""
        if not market_summary:
            return "I couldn't retrieve current market data."

        answer_parts = []
        for index, data in market_summary.items():
            index_name = {
                '^GSPC': 'S&P 500',
                '^DJI': 'Dow Jones',
                '^IXIC': 'NASDAQ',
                '^VIX': 'VIX'
            }.get(index, index)

            answer_parts.append(
                f"{index_name}: {data['current_price']:.2f} "
                f"({data['change']:+.2f}, {data['change_percent']:+.2f}%)"
            )

        return " | ".join(answer_parts)

    def _combine_answers(self, rag_answer: str, finance_data: Dict, question: str, finance_content: str = "") -> str:
        """Combine RAG and finance answers"""
        combined_parts = [rag_answer]

        # Add SmartFinanceRouter content if available
        if finance_content:
            combined_parts.append(f"\n\nFinancial Analysis: {finance_content}")

        # Add basic finance data if no smart content was generated
        if finance_data and not finance_content:
            finance_answer = self._simple_finance_answer(finance_data)
            combined_parts.append(f"\n\nCurrent Market Data: {finance_answer}")

        return "".join(combined_parts)