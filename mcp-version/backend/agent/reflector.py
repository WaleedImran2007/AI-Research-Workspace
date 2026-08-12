import os
import json

from chains.reflector_chain import reflector_chain

def reflect(user_query: str, plan, context):

    return reflector_chain.invoke(
        {
            "user_query": user_query,
            "plan": plan,
            "context": context
        }
    )