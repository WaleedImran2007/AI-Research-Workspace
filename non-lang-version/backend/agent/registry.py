from agent.tools import retrieval, page_loader, calculator, web_search, python_tool

TOOLS = {
    "retrieval": retrieval.execute,
    "page_loader": page_loader.execute,
    "calculator": calculator.execute,
    "web_search": web_search.execute,
    "python_tool": python_tool.execute,
}