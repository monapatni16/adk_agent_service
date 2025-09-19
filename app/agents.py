import logging
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import settings
from app.utils import logger

class TransientError(Exception):
    """Raised when an agent run had a transient error that should be retried."""
    pass

def retry_decorator():
    return retry(
        reraise=True,
        stop=stop_after_attempt(settings.AGENT_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=settings.AGENT_RETRY_BACKOFF, min=1, max=10),
        retry=retry_if_exception_type(TransientError)
    )

class ADKAgentWrapper:
    def __init__(self, name: str, model_identifier: str, instruction: str):
        self.name = name
        try:
            self.agent = Agent(
                name=self.name,
                model=LiteLlm(model=model_identifier),
                description=f"{self.name} agent",
                instruction=instruction
            )
        except Exception as e:
            logger.error("Failed to initialize ADK Agent", agent=self.name, error=str(e))
            raise

    @retry_decorator()
    async def run(self, input_text: str) -> str:
        try:
            # The actual interface might be different depending on ADK version
          #  result = await self.agent.run_async({"input": input_text})
            result = self.agent.run_async({"input": input_text})
            print("Result ------------------>", dir(result))
            # Try to extract output_text or fallback
            if hasattr(result, "output_text"):
                return result.output_text
            if isinstance(result, dict):
                return result.get("output", str(result))
            return str(result)
        except Exception as e:
            logger.error("Agent run failed", agent=self.name, error=str(e))
            # For some errors, you might wrap as TransientError or not
            # For now, treat all as transient for retry decorator
            raise TransientError(str(e))

def create_agents():
    # Three different agents with different models / instructions
    agent1 = ADKAgentWrapper(
        name="ResearchAgent",
        model_identifier=settings.MODEL_1,
        instruction="You are the research agent; gather data and summarize."
    )
    agent2 = ADKAgentWrapper(
        name="AnalysisAgent",
        model_identifier=settings.MODEL_2,
        instruction="You are the analysis agent; analyze the research output."
    )
    agent3 = ADKAgentWrapper(
        name="SummaryAgent",
        model_identifier=settings.MODEL_3,
        instruction="You are the summary agent; produce a concise summary."
    )
    return [agent1, agent2, agent3]