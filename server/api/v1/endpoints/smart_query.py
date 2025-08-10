import logging
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from services.query_router import QueryRouter

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global router instance
_query_router: Optional[QueryRouter] = None


class SmartQueryRequest(BaseModel):
    """Request model for smart queries"""
    question: str = Field(..., min_length=1, max_length=1000, description="The user's question")
    selected_documents: Optional[List[str]] = Field(None, description="Optional list of selected document IDs")


class SmartQueryResponse(BaseModel):
    """Response model for smart queries"""
    answer: str = Field(..., description="The generated answer")
    source: str = Field(..., description="Data source used: 'rag', 'finance', 'mixed'")
    processing_time: float = Field(..., description="Processing time in seconds")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data from the source")


def get_query_router() -> QueryRouter:
    """Dependency to get query router instance"""
    global _query_router
    if _query_router is None:
        _query_router = QueryRouter()
    return _query_router


@router.post("/smart-query", response_model=SmartQueryResponse)
async def smart_query(
    request: SmartQueryRequest,
    router: QueryRouter = Depends(get_query_router)
):
    """
    Smart query endpoint that automatically routes to the best data source:
    - RAG (PDFs) for qualitative analysis
    - Yahoo Finance for quantitative data and predictions
    - Mixed for queries requiring both sources
    """
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        logger.info(f"Processing smart query: {request.question[:100]}...")
        
        # Route query to appropriate source
        result = router.route_query(
            question=request.question.strip(),
            selected_documents=request.selected_documents
        )
        
        response = SmartQueryResponse(
            answer=result.answer,
            source=result.source,
            processing_time=result.processing_time,
            data=result.data
        )
        
        logger.info(f"Smart query processed: {result.source} source, {result.processing_time:.2f}s")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Smart query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Smart query failed: {str(e)}")


@router.get("/finance/stock/{symbol}")
async def get_stock_info(
    symbol: str,
    router: QueryRouter = Depends(get_query_router)
):
    """Get current stock information"""
    try:
        from services.finance.yahoo_finance_service import YahooFinanceService
        finance_service = YahooFinanceService()
        
        stock_data = finance_service.get_stock_info(symbol)
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"Stock data not found for {symbol}")
        
        return {
            "symbol": stock_data.symbol,
            "current_price": stock_data.current_price,
            "change": stock_data.change,
            "change_percent": stock_data.change_percent,
            "volume": stock_data.volume,
            "market_cap": stock_data.market_cap,
            "pe_ratio": stock_data.pe_ratio,
            "dividend_yield": stock_data.dividend_yield,
            "timestamp": stock_data.timestamp.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stock info failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stock info: {str(e)}")


@router.get("/finance/market-summary")
async def get_market_summary(
    router: QueryRouter = Depends(get_query_router)
):
    """Get market summary for major indices"""
    try:
        from services.finance.yahoo_finance_service import YahooFinanceService
        finance_service = YahooFinanceService()
        
        summary = finance_service.get_market_summary()
        return summary
        
    except Exception as e:
        logger.error(f"Market summary failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get market summary: {str(e)}")


@router.get("/finance/search")
async def search_stocks(
    query: str,
    router: QueryRouter = Depends(get_query_router)
):
    """Search for stocks by name or symbol"""
    try:
        from services.finance.yahoo_finance_service import YahooFinanceService
        finance_service = YahooFinanceService()
        
        results = finance_service.search_stocks(query)
        return {"results": results}
        
    except Exception as e:
        logger.error(f"Stock search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search stocks: {str(e)}") 