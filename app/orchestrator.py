import asyncio, time, json
from typing import List, AsyncGenerator
from app.schemas import AgentProgress, FinalResult
from app.metrics import REQUESTS_TOTAL, REQUEST_DURATION, AGENT_ERRORS
from app.utils import logger
from app.config import settings

class Orchestrator:
    def __init__(self, agents: List):
        if not agents or len(agents) < 2:
            raise ValueError("Need at least two agents for Agent-2-Agent orchestration")
        self.agents = agents
        self.total = len(agents)

    async def stream_workflow(self, query: str) -> AsyncGenerator[str, None]:
        start = time.time()
        REQUESTS_TOTAL.inc()
        steps = []
        current_input = query

        for idx, agent in enumerate(self.agents, start=1):
            # Start event
            progress = AgentProgress(
                status="started",
                current_agent=agent.name,
                step_index=idx,
                total_steps=self.total,
                message=f"{agent.name} started"
            )
            yield f"data: {json.dumps(progress.dict())}\n\n"

            # Run with timeout
            try:
                result = await asyncio.wait_for(agent.run(current_input), timeout=settings.AGENT_TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                REQUEST_ERRORS = AGENT_ERRORS
                REQUEST_ERRORS.inc()
                logger.error("Agent timeout", agent=agent.name)
                progress = AgentProgress(
                    status="failed",
                    current_agent=agent.name,
                    step_index=idx,
                    total_steps=self.total,
                    message=f"{agent.name} timed out after {settings.AGENT_TIMEOUT_SECONDS}s"
                )
                yield f"data: {json.dumps(progress.dict())}\n\n"
                return
            except Exception as e:
                AGENT_ERRORS.inc()
                logger.error("Agent execution error", agent=agent.name, error=str(e))
                progress = AgentProgress(
                    status="failed",
                    current_agent=agent.name,
                    step_index=idx,
                    total_steps=self.total,
                    message=str(e)
                )
                yield f"data: {json.dumps(progress.dict())}\n\n"
                return

            # Success
            steps.append({"name": agent.name, "output": result})
            progress = AgentProgress(
                status="completed",
                current_agent=agent.name,
                step_index=idx,
                total_steps=self.total,
                message=f"{agent.name} completed",
                data={"output_preview": result[:400] if isinstance(result, str) else str(result)}
            )
            yield f"data: {json.dumps(progress.dict())}\n\n"

            current_input = result

        # Final result
        final = FinalResult(
            workflow=" -> ".join([a.name for a in self.agents]),
            steps=[
                AgentProgress(
                    status="completed",
                    current_agent=s["name"],
                    step_index=i+1,
                    total_steps=self.total,
                    message="completed",
                    data={"output_preview": s["output"][:400] if isinstance(s["output"], str) else str(s["output"])}
                )
                for i, s in enumerate(steps)
            ],
            final_output=steps[-1]["output"] if steps else None
        )

        yield f"data: {json.dumps({'final': final.dict()})}\n\n"

        elapsed = time.time() - start
        REQUEST_DURATION.observe(elapsed)
        logger.info("Orchestration finished", duration=elapsed, workflow=final.workflow)