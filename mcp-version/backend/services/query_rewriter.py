from chains.query_rewriter_chain import query_rewriter_chain

def rewrite_query(query: str, history: str) -> str:
    return query_rewriter_chain.invoke({
        "query": query,
        "history": history
    })
