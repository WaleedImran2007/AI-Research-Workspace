from agent.tools.retrieval import retrieval
from agent.tools.calculator import calculator
from agent.tools.page_loader import page_loader
from agent.tools.web_search import web_search
from agent.tools.python_tool import python_tool

TOOLS = {
    "retrieval": retrieval,
    "page_loader": page_loader,
    "calculator": calculator,
    "web_search": web_search,
    "python_tool": python_tool,
}