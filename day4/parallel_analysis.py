# parallel_analysis.py — no LLM calls here, just the orchestration pattern
import asyncio
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class MultiAnalysisState(TypedDict):
    url: str
    seo_analysis: str
    perf_analysis: str
    security_analysis: str
    global_report: str

# --- Parallel nodes — they all read the same initial state ---
# In real life, each would call an LLM or a specialized API.
# Here we simulate with asyncio.sleep to make the gain visible.

async def analyze_seo(state: MultiAnalysisState) -> dict:
    await asyncio.sleep(1.5)  # simulates "LLM call for SEO audit"
    return {"seo_analysis": "SEO score: 72/100. Missing titles on 3 pages."}

async def analyze_perf(state: MultiAnalysisState) -> dict:
    await asyncio.sleep(1.5)  # simulates "perf audit via Lighthouse"
    return {"perf_analysis": "LCP: 2.3s. CLS: 0.05. FCP: 1.1s."}

async def analyze_security(state: MultiAnalysisState) -> dict:
    await asyncio.sleep(1.5)  # simulates "security headers check"
    return {"security_analysis": "Missing headers: X-Frame-Options, CSP."}

def consolidate(state: MultiAnalysisState) -> dict:
    report = f"""## Analysis Report for {state['url']}

**SEO:** {state['seo_analysis']}
**Performance:** {state['perf_analysis']}
**Security:** {state['security_analysis']}
"""
    return {"global_report": report}

# --- Build the graph: 3 parallel branches, then consolidation ---
graph = StateGraph(MultiAnalysisState)
graph.add_node("seo", analyze_seo)
graph.add_node("perf", analyze_perf)
graph.add_node("security", analyze_security)
graph.add_node("consolidate", consolidate)

# Fan-out: START branches to the three nodes in parallel
graph.add_edge(START, "seo")
graph.add_edge(START, "perf")
graph.add_edge(START, "security")

# Fan-in: the three nodes feed the consolidator — LangGraph waits for all of them to finish
graph.add_edge("seo", "consolidate")
graph.add_edge("perf", "consolidate")
graph.add_edge("security", "consolidate")
graph.add_edge("consolidate", END)

workflow = graph.compile()

# --- Execution ---
async def main():
    import time
    start = time.time()
    result = await workflow.ainvoke({
        "url": "https://example.com",
        "seo_analysis": "", "perf_analysis": "", "security_analysis": "",
        "global_report": "",
    })
    elapsed = time.time() - start
    print(result["global_report"])
    print(f"[Elapsed: {elapsed:.2f}s — note: ~1.5s in parallel vs ~4.5s in sequence]")

if __name__ == "__main__":
    asyncio.run(main())
