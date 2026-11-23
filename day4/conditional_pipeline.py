# conditional_pipeline.py — no LLM calls here, a local simulation of the pattern
from typing import TypedDict
from langgraph.graph import StateGraph, END

class ValidationState(TypedDict):
    code: str
    errors: list[str]
    corrected_code: str
    report: str

def analyze_code(state: ValidationState) -> dict:
    """Analyzes the code and detects errors."""
    code = state["code"]
    # Static analysis — simplified for the demo
    errors = []
    if "except:" in code:
        errors.append("Overly generic exception (bare except)")
    if "eval(" in code:
        errors.append("Use of eval() — security risk")
    if len([line for line in code.split("\n") if line.strip()]) > 50:
        errors.append("Function too long (> 50 lines)")
    return {"errors": errors}

def fix_code(state: ValidationState) -> dict:
    """Automatically fixes simple errors."""
    code = state["code"]
    corrected_code = code.replace("except:", "except Exception as e:")
    return {"corrected_code": corrected_code}

def generate_report(state: ValidationState) -> dict:
    """Generates a report when no fix is needed."""
    return {"report": "Code validated. No errors detected."}

def generate_report_with_fixes(state: ValidationState) -> dict:
    """Generates a report with the applied fixes."""
    errors = "\n".join([f"- {e}" for e in state["errors"]])
    return {"report": f"Corrections applied:\n{errors}"}

def router(state: ValidationState) -> str:
    """Decides the path based on the detected errors."""
    if state["errors"]:
        return "fix"
    return "clean_report"

graph = StateGraph(ValidationState)
graph.add_node("analyze", analyze_code)
graph.add_node("fix", fix_code)
graph.add_node("clean_report", generate_report)
graph.add_node("fix_report", generate_report_with_fixes)

graph.set_entry_point("analyze")
graph.add_conditional_edges(
    "analyze",
    router,
    {
        "fix": "fix",
        "clean_report": "clean_report",
    }
)
graph.add_edge("fix", "fix_report")
graph.add_edge("clean_report", END)
graph.add_edge("fix_report", END)

workflow = graph.compile()

# --- Run the pipeline on two examples to see both branches ---
if __name__ == "__main__":
    bad_code = """
def parse_user_input(raw):
    try:
        return eval(raw)
    except:
        return None
"""
    print("--- Bad code ---")
    result = workflow.invoke({"code": bad_code, "errors": [], "corrected_code": "", "report": ""})
    print(result["report"])
    print("\nCorrected:\n" + result["corrected_code"])

    good_code = """
def add(a: int, b: int) -> int:
    return a + b
"""
    print("\n--- Good code ---")
    result = workflow.invoke({"code": good_code, "errors": [], "corrected_code": "", "report": ""})
    print(result["report"])
