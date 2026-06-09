from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are ProfessorBot, a northeastern professor review assistant.

  GROUNDING RULES:
  - Answer the user's question using ONLY the rule text provided in the context below.
  - Do not use any outside knowledge about professor reviews, even if you are confident it is correct.
  - If the answer is not contained in the provided text, say so explicitly. Do not guess,
    do not fill in gaps, and do not generalize from what you know about other games.

  CITATION RULES:
  - State which game your answer comes from, using the game label from the source blocks
    (e.g. "According to the Alden Jackson reviews, ...").
  - If your answer draws on more than one source, cite each source you used.
  """

def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer from retrieved rule chunks.

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
      - "text"     : the chunk text
      - "professor"     : the professor name
      - "distance" : similarity score (you can use this to filter weak matches)

    Return the response as a plain string.
    """
    if not retrieved_chunks:
        return (
            "I couldn't find anything relevant in the loaded review documents. "
            "Try rephrasing your question — or check that your ingestion pipeline is working."
        )

    # Your implementation here.

    context_blocks = []
    for i, chunk in enumerate(retrieved_chunks, start=1):
          context_blocks.append(
              f"[Source {i} — {chunk['professor']}]\n{chunk['text']}"
          )
    context = "\n\n".join(context_blocks)

    user_message = (
          f"Context:\n{context}\n\n"
          f"Question: {query}"
      )

    response = _client.chat.completions.create(
          model=LLM_MODEL,
          messages=[
              {"role": "system", "content": SYSTEM_PROMPT},
              {"role": "user", "content": user_message},
          ],
      )

    return response.choices[0].message.content
    # return "⚙️ Response generation not yet implemented. Complete Milestone 3 to activate answers."
