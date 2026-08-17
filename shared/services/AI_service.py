import chromadb
from google import genai
from shared.config import API_key

client = genai.Client(
    api_key=API_key
)

db = chromadb.PersistentClient(
    path="./data_db"
)

collection = db.get_collection(
    "student_data"
)


def ask_ai(question:str) -> str:

    result = collection.query(
        query_texts=[question],
        n_results=30
    )

    documents = result.get("documents", [[]])[0]

    if not documents:
        return "No matching records were found."

    context = "\n".join(documents)

    prompt = f"""
Use only the information below.

Context:
{context}

Question:
{question}

If the answer isn't present in the context, say so.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text

