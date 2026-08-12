from chains.intent_chain import intent_chain

def detect_intent(user_query: str):
    return intent_chain.invoke(
        {
            "user_query": user_query
        }
    )
