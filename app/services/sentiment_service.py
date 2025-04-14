import asyncio
import logging
import httpx
from typing import Dict, Any, List
from app.config import settings
from app.models import SentimentAnalysisResult

class SentimentService:
    def __init__(self):
        self.datura_api_key = settings.DATURA_API_KEY
        self.chutes_api_key = settings.CHUTES_API_KEY
        self.datura_base_url = "https://api.datura.ai"
        self.chutes_base_url = "https://api.chutes.ai"

    async def search_tweets(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for tweets using Datura.ai API
        """
        url = f"{self.datura_base_url}/twitter/search"
        headers = {
            "Authorization": f"Bearer {self.datura_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": query,
            "limit": limit
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, 
                    headers=headers, 
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json().get("data", [])
        except Exception as e:
            logging.error(f"Error searching tweets: {e}")
            return []
    
    async def analyze_sentiment(self, tweets: List[Dict[str, Any]]) -> SentimentAnalysisResult:
        """
        Analyze sentiment of tweets using Chutes.ai LLM API
        """
        if not tweets:
            return SentimentAnalysisResult(
                score=0, 
                tweets_analyzed=0,
                summary="No tweets found for analysis"
            )

        # Extract tweet text and create prompt
        tweet_texts = [tweet.get("text", "") for tweet in tweets if tweet.get("text")]
        tweets_text = "\n\n".join(tweet_texts)
        
        prompt = f"""
        Analyze the sentiment of the following tweets about Bittensor:
        
        {tweets_text}
        
        Provide a sentiment score from -100 (extremely negative) to 100 (extremely positive).
        Base your analysis on indicators like:
        - Positive/negative language
        - Opinions about the technology
        - Enthusiasm for the project
        - Criticisms or concerns
        - Overall sentiment
        Return ONLY the score value (a number between -100 and 100).
        """

        # Call Chutes API
        chutes_endpoint = f"{self.chutes_base_url}/v1/app/chute/20acffc0-0c5f-58e3-97af-21fc0b261ec4/run"
        headers = {
            "Authorization": f"Bearer {self.chutes_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "input": prompt
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    chutes_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()

                result = response.json()
                score = self._extract_sentiment_score(result.get("output", "0"))

                return SentimentAnalysisResult(
                    score=score,
                    tweets_analyzed=len(tweets),
                    summary=f"Analyzed {len(tweets)} tweets with sentiment score {score}"
                )
        except Exception as e:
            logging.error(f"Error analyzing sentiment: {e}")
            # Return neutral sentiment on error
            return SentimentAnalysisResult(
                score=0,
                tweets_analyzed=len(tweets),
                summary=f"Error analyzing sentiment: {str(e)}"
            )

    def _extract_sentiment_score(self, output: str) -> float:
        """Extract numerical sentiment score from LLM output"""
        try:
            # Try to extract just the number from the output
            number_str = ''.join(c for c in output if c.isdigit() or c == '-' or c == '.')
            if number_str:
                score = float(number_str)
                # Ensure the score is within bounds
                return max(min(score, 100), -100)
            return 0
        except Exception:
            return 0

    async def get_subnet_sentiment(self, netuid: int) -> SentimentAnalysisResult:
        """
        Get sentiment analysis for a specific subnet
        """
        # Search for tweets about the subnet
        query = f"Bittensor netuid {netuid}"
        tweets = await self.search_tweets(query, limit=20)

        # Analyze sentiment
        sentiment = await self.analyze_sentiment(tweets)
        return sentiment

# Create service instance
sentiment_service = SentimentService()


