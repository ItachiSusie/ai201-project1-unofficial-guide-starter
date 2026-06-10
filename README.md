# The Unofficial Guide — Project 1

---

## Domain

ProfessorBot covers student reviews and ratings of Northeastern University Computer Science professors.

This knowledge is valuable because students want honest feedback about teaching style, workload, grading difficulty, attendance requirements, and overall course experience before registering for classes.

This information is difficult to find through official university channels. Course catalogs and faculty pages provide only official descriptions and do not include student opinions, criticism, or experiences. As a result, students often rely on third-party review platforms such as Rate My Professors.

## Document Sources

All documents were collected from Rate My Professors and manually converted into structured `.txt` files for ingestion.

| #   | Source                | Type                                   | URL or file path                                   |
| --- | --------------------- | -------------------------------------- | -------------------------------------------------- |
| 1   | Alden Jackson Reviews | Rate My Professors Page → TXT Document | https://www.ratemyprofessors.com/professor/2443125 |
| 2   | Eric Gerber Reviews   | Rate My Professors Page → TXT Document | https://www.ratemyprofessors.com/professor/2837478 |
| 3   | Jonathan Bell Reviews | Rate My Professors Page → TXT Document | https://www.ratemyprofessors.com/professor/2861725 |
| 4   | Lucia Nunez Reviews   | Rate My Professors Page → TXT Document | https://www.ratemyprofessors.com/professor/2668761 |
| 5   | Mark Fontenot Reviews | Rate My Professors Page → TXT Document | https://www.ratemyprofessors.com/professor/2868024 |
| 6   | Rose Sloan Reviews    | Rate My Profess                        |                                                    |

---

## Chunking Strategy

**Chunk size:** 300 characters

**Overlap:** 50 characters

**Why these choices fit your documents:**

My original plan was to use review-level chunking because each professor document already contained separate review blocks.

However, during retrieval testing I discovered that review-level chunking did not consistently return the most relevant chunks.

For example, queries about professor ratings often failed because rating information occupied only a small portion of a review chunk.

After testing, I switched to fixed-size chunking with overlap.

The overlap helps preserve context near chunk boundaries and improved retrieval quality for ranking and course-related questions.

**Final chunk count:** 177 chunks

---

## Embedding Model

**Model used:**

```text
all-MiniLM-L6-v2
```

via Sentence Transformers.

This model was recommended in the starter project and is free to run locally.
It is lightweight, fast, and easy to integrate with ChromaDB.
For a small corpus of professor reviews, it provides reasonable semantic retrieval quality without requiring external APIs.

**Production tradeoff reflection:**

If cost were not a concern, I would consider:

- Better multilingual support for cross-language queries
- Higher retrieval accuracy on opinion-based review text
- Better handling of ranking and aggregation tasks
- Larger embedding models that capture semantic nuance more effectively

The tradeoff would be higher latency and API costs.

---

## Grounded Generation

**System prompt grounding instruction:**

```text
Answer the user's question using ONLY the raw text provided in the context below.

Do not use outside knowledge.

If the answer is not contained in the provided text, say so explicitly.

State which source document your answer comes from.
```

**How source attribution is surfaced in the response:**

The generation model only receives retrieved chunks from ChromaDB.

It is instructed to refuse questions that cannot be answered from the provided context.

This prevents hallucination and ensures answers remain tied to retrieved documents.

---

## Evaluation Report

Three of the five test questions were answered accurately (#1, #3, and #4). These were straightforward factual lookup questions where the required information appeared directly in the retrieved chunks.

Question #5 behaved as expected for a retrieval-augmented system. The requested average would require access to all review ratings, but only a representative sample of reviews was stored in the document collection. Rather than hallucinating a value, the model explained why it could not compute the requested statistic and referenced the available aggregate rating instead.

Question #2 was the clearest failure case. The retriever did not return the documents containing all of the highest-rated professors. Because professor ratings occupy only a small portion of each chunk compared to the surrounding review text, semantic retrieval prioritized other professors whose chunks appeared more similar to the query. As a result, the generator could only rank the professors present in the retrieved context, producing an incorrect answer.

| #   | Question                                                             | Expected answer                                                                                                | System response (summarized)                                                                                                                                                                                    | Retrieval quality  | Response accuracy  |
| --- | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | ------------------ |
| 1   | Who teaches CS3650?                                                  | Alden Jackson teaches CS3650.                                                                                  | Correctly identified Alden Jackson as the instructor for CS3650.                                                                                                                                                | Relevant           | Accurate           |
| 2   | Who are the three highest rated CS professors at Northeastern?       | Eric Gerber, Zhengzhong Jin, and Kaan Onarlioglu.                                                              | Returned Eric Gerber, Lucia Nunez, and Jonathan Bell instead of the actual top three professors.                                                                                                                | Partially relevant | Inaccurate         |
| 3   | How is Professor Alvaro Monge rated?                                 | Very poorly rated (Overall Quality 1.1 / 5).                                                                   | Correctly reported Alvaro Monge's low rating, low "Would Take Again" percentage, and high difficulty score.                                                                                                     | Relevant           | Accurate           |
| 4   | Which courses has Jonathan Bell taught?                              | CS3100 and CS4530.                                                                                             | Correctly identified CS3100 and CS4530 from the retrieved review documents.                                                                                                                                     | Relevant           | Accurate           |
| 5   | What is the average rating across Kaan Onarlioglu's review comments? | The system should not be able to accurately compute the average because only a sample of reviews is retrieved. | Explained that only the site-wide Overall Quality score (4.9/5 based on 107 ratings) is available and that the average across all individual review comments cannot be calculated from the retrieved documents. | Relevant           | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target

**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:**

```text
Who are the three highest rated CS professors at Northeastern?
```

**What the Expected returned:**

```text
Eric Gerber
Zhengzhong Jin
Kaan Onarlioglu
```

**What the system returned:**

```text
Eric Gerber
Lucia Nunez
Jonathan Bell
```

**Root cause (tied to a specific pipeline stage):**

The failure occurred during retrieval.

Professor ratings appear as a small portion of each summary chunk. Most chunk content consists of review text and metadata.

Because embeddings are generated from the entire chunk, rating information received relatively little weight.

As a result, the retriever failed to return chunks for Zhengzhong Jin and Kaan Onarlioglu.

The generator could only rank the professors present in the retrieved context.

**What you would change to fix it:**

Use hybrid retrieval combining vector similarity with metadata or keyword-based filtering.

Store overall ratings separately as structured metadata and perform ranking directly on metadata instead of relying entirely on semantic retrieval.

---

## Spec Reflection

**One way the spec helped you during implementation:**
The planning document forced me to think through my retrieval strategy, chunking design, evaluation questions, and anticipated failure cases before writing code.

This made implementation significantly faster because the architecture and testing criteria were already defined.

**One way your implementation diverged from the spec, and why:**
My original plan used review-level chunking because reviews naturally formed separate units.

After retrieval testing, I discovered that fixed-size chunking with overlap produced better retrieval results.

As a result, I changed the chunking strategy from the original design and updated the implementation accordingly.

---

## AI Usage

**Instance 1**

- What I gave the AI:
  My planning document, architecture diagram, chunking strategy, and retrieval requirements.

- What it produced:
  Ingestion scripts, chunking logic, ChromaDB indexing code, retrieval functions, and generation pipeline code.

- What I changed or overrode:
  I replaced the original review-level chunking implementation with fixed-size chunking (300 character chunks with 50 character overlap) after retrieval testing showed better performance.

**Instance 2**

- What I gave the AI:
  UI requirements and the existing chatbot interface code.
- What it produced:
  HTML, CSS, and JavaScript updates for the chatbot interface.
- What I changed or overrode:
  I also modified parts of the generated interface to better match the retrieval and generation workflow used by my system.
