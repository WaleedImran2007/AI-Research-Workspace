def user_serializer(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],

        "aiRequestsRemaining": user.get("aiRequestsRemaining", 0),
        "aiResetDate": user.get("aiResetDate"),

        "createdAt": user["createdAt"].isoformat() if "createdAt" in user else None,
        "updatedAt": user["updatedAt"].isoformat() if "updatedAt" in user else None,
    }

def collection_serializer(collection: dict) -> dict:
    return {
        "id": str(collection["_id"]),
        "name": collection["name"],
        "description": collection.get("description"),
        "ownerId": str(collection["ownerId"]),
        "createdAt": collection["createdAt"] if "createdAt" in collection else None,
        "updatedAt": collection["updatedAt"] if "updatedAt" in collection else None,
    }

def collections_serializer(collections: list) -> list:
    return [collection_serializer(collection) for collection in collections]


def document_serializer(document: dict) -> dict:
    return {
        "id": str(document["_id"]),
        "ownerId": str(document["ownerId"]),
        "collectionId": str(document["collectionId"]),
        "originalName": document["originalName"],
        "fileName": document["fileName"],
        "mimeType": document["mimeType"],
        "filesize": document["filesize"],
        "status": document["status"],
        "createdAt": document["createdAt"] if "createdAt" in document else None,
        "updatedAt": document["updatedAt"] if "updatedAt" in document else None,
    }

def documents_serializer(documents: list) -> list:
    return [document_serializer(document) for document in documents]

def knowledge_chunk_serializer(chunk: dict) -> dict:
    return {
        "id": str(chunk["_id"]),
        "ownerId": str(chunk["ownerId"]),
        "collectionId": str(chunk["collectionId"]),
        "documentId": str(chunk["documentId"]),
        "chunkIndex": chunk["chunkIndex"],
        "text": chunk["text"],
        "embedding": chunk["embedding"],
    }

def knowledge_chunks_serializer(chunks: list) -> list:
    return [knowledge_chunk_serializer(chunk) for chunk in chunks]

def conversation_serializer(conversation: dict) -> dict:
    return {
        "id": str(conversation["_id"]),
        "title": conversation["title"],
        "createdAt": conversation["createdAt"] if "createdAt" in conversation else None,
        "updatedAt": conversation["updatedAt"] if "updatedAt" in conversation else None,
    }

def conversations_serializer(conversations: list) -> list:
    return [conversation_serializer(conversation) for conversation in conversations]

def message_serializer(message: dict) -> dict:
    return {
        "id": str(message["_id"]),
        "conversation_id": str(message["conversation_id"]),
        "role": message["role"],
        "content": message["content"],
        "sources": message.get("sources", []),
        "image": message.get("image"),
        "file": message.get("file"),
        "createdAt": message["createdAt"] if "createdAt" in message else None,
    }

def messages_serializer(messages: list) -> list:
    return [message_serializer(message) for message in messages]