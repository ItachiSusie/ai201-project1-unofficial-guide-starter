# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

I chose ratings and student reviews of Northeastern University's Computer Science professors.

This knowledge is valuable because students want honest feedback on a professor's teaching style, workload, grading, and attendance policy before they register for a course. It is hard to find through official channels because the university's course catalog and faculty pages only show neutral or promotional descriptions. They do not publish the critical or negative student feedback that students rely on most when choosing a section, so this candid, crowd sourced perspective only exists on third party review sites.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| #   | Source                     | Description     | URL or location                                    |
| --- | -------------------------- | --------------- | -------------------------------------------------- |
| 1   | Rate My Professors website | Lucia Nunez     | https://www.ratemyprofessors.com/professor/2668761 |
| 2   | Rate My Professors website | Kaan Onarlioglu | https://www.ratemyprofessors.com/professor/2338287 |
| 3   | Rate My Professors website | Zhengzhong Jin  | https://www.ratemyprofessors.com/professor/3143867 |
| 4   | Rate My Professors website | Jonathan Bell   | https://www.ratemyprofessors.com/professor/2861725 |
| 5   | Rate My Professors website | Gregory Aloupis | https://www.ratemyprofessors.com/professor/2903924 |
| 6   | Rate My Professors website | Mark Fontenot   | https://www.ratemyprofessors.com/professor/2868024 |
| 7   | Rate My Professors website | Rose Sloan      | https://www.ratemyprofessors.com/professor/3053867 |
| 8   | Rate My Professors website | Alvaro Monge    | https://www.ratemyprofessors.com/professor/2757769 |
| 9   | Rate My Professors website | Eric Gerber     | https://www.ratemyprofessors.com/professor/2837478 |
| 10  | Rate My Professors website | Alden Jackson   | https://www.ratemyprofessors.com/professor/2443125 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** One review per chunk. Reviews are short (roughly 100 to 400 characters, about 1 to 3 sentences), so each chunk holds exactly one complete review.

**Overlap:** 0 characters.

**Reasoning:** Each document is already split into individual review comments, so the corpus has a clear structure. A fixed character window would cut a review in half or merge two students' opinions into one chunk, which hurts retrieval. Splitting on the review boundaries keeps each opinion intact and easy to attribute. Overlap is 0 because reviews are independent and no single fact spans two reviews, so overlap would only duplicate text and add noise.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 (via sentence-transformers).

**Top-k:** 5. Each professor has roughly 5 to 15 reviews, so a top-k of 5 is small enough to stay focused on a single professor's reviews, and when a question spans several professors it still leaves room for each one to contribute a relevant chunk. I also discard any retrieved chunk whose distance score is above 0.7 so that only sufficiently relevant reviews are passed to the LLM. If top-k is too large, retrieval is slower and pulls in less relevant reviews that distract the LLM; if it is too small, relevant reviews may be missed.

**Production tradeoff reflection:** all-MiniLM-L6-v2 is small, fast, and free to run locally, but it has a short context window and is trained mainly on English. If cost were not a constraint and I deployed this for real users, I would weigh: multilingual support (international students ask questions in different languages while the reviews are in English, so a multilingual model such as multilingual-e5 or OpenAI text-embedding-3 would handle cross language queries far better); accuracy on domain specific, opinionated review text (a larger model captures nuance more reliably); context length (less important here because reviews are short); and latency and cost (a larger or hosted model is slower and costs money per query, which is the price for the better accuracy and multilingual coverage).

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| #   | Question                                                             | Expected answer                                                                            | Case type                                       |
| --- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------------- |
| 1   | Who teaches CS3650?                                                  | Alden Jackson teaches CS3650.                                                              | Factual lookup (accurate)                       |
| 2   | Who are the three highest rated CS professors at Northeastern?       | Eric Gerber, Zhengzhong Jin, and Kaan Onarlioglu.                                          | Cross document ranking (harder, may be partial) |
| 3   | How is Professor Alvaro Monge rated?                                 | Very low, about 1.1 out of 5.                                                              | Factual lookup (accurate)                       |
| 4   | What is the average rating across Kaan Onarlioglu's review comments? | About 4.4 / 5 (the average of his 10 sampled review scores: 5, 3, 5, 4, 5, 5, 4, 3, 5, 5). | Aggregation (deliberate failure)                |
| 5   | Which courses has Jonathan Bell taught?                              | CS3100 and CS4530.                                                                         | Factual lookup (accurate)                       |

Coverage: Questions 1, 3, and 5 are factual single source lookups that should be accurate. Question 2 is a cross document ranking that is harder and may come back partial, because with top-k = 5 the retriever may not pull a rating for every professor. Question 4 is a deliberate failure case: computing a true average needs all 10 reviews, but top-k = 5 can retrieve at most 5, so the system is expected to fall short. This spread gives accurate cases, one partial case, and one clean failure, instead of all 5 coming back perfect.

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Aggregation questions run into the top-k tradeoff.** As explained in the Retrieval Approach, I chose top-k = 5 on purpose to keep retrieval focused on the most relevant reviews and avoid pulling in noisy, off-topic chunks. The cost of that choice is that questions which need every review for a professor, like averaging all 10 of Kaan Onarlioglu's review scores (true answer 4.4 / 5), cannot be answered in full, because at most 5 of the 10 reviews are retrieved. Raising top-k to 10 would cover one professor who has about 10 reviews, but it brings back the downsides I noted (slower retrieval and more off-topic, distracting chunks), and it still would not cover a professor with up to 15 reviews or a question that aggregates across several professors. So this is an accepted tradeoff of a small, fixed top-k rather than a value I can simply turn up.

2. **Generation not grounded in the documents.** In the generation step, the LLM might pull related information from its own training knowledge or the web instead of relying only on the retrieved review text, which would produce answers that are not grounded in my sources.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
+----------------------------------------+
|           Document Ingestion           |
|           Source: ./documents          |
|        Professor review text files     |
+----------------------------------------+
                   |
                   v
+----------------------------------------+
|               Chunking                 |
|       Custom review-based splitter     |
|       Split by "[Review N]" sections   |
+----------------------------------------+
                   |
                   v
+----------------------------------------+
|               Embedding                |
|            all-MiniLM-L6-v2             |
|          Sentence Transformers         |
+----------------------------------------+
                   |
                   v
+----------------------------------------+
|              Vector Store              |
|                ChromaDB                |
|     Collection: professor_reviews      |
|            Path: ./chroma_db           |
+----------------------------------------+
                   |
                   v
+----------------------------------------+
|               Retrieval                |
|            Chroma Retriever            |
|               Top-K: 5                  |
+----------------------------------------+
                   |
                   v
+----------------------------------------+
|              Generation                |
|               Groq API                 |
|         llama-3.3-70b-versatile        |
+----------------------------------------+
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I will use Claude (in Claude Code). As input I will give it my Domain, Documents, and Chunking Strategy sections plus the Document Ingestion and Chunking boxes of the Architecture, and tell it the source files live in ./documents as .txt files where each file starts with a header and SUMMARY block followed by "[Review N]" markers. Following the rulesbot ingest.py pattern, I expect it to produce a loader that reads every .txt file in ./documents and a chunk function that returns simple dicts with text, professor (just the professor's name), and chunk_id, where chunk_0 is the header and summary block (professor, department, school, source, and the site-wide rating) and chunk_1 to chunk_n are the individual student reviews, one review per chunk. I will verify by running it on kaan_onarlioglu.txt and checking that it produces one summary chunk plus 10 review chunks (chunk_0 through chunk_10), that no review is split or merged, and that each chunk carries the correct professor name and chunk_id.

**Milestone 4 — Embedding and retrieval:**
I will use Claude. As input I will give it my Retrieval Approach section plus the Embedding, Vector Store, and Retrieval boxes of the Architecture, with the requirements: embed chunks with all-MiniLM-L6-v2 via sentence-transformers, store them in a ChromaDB collection named professor_reviews at ./chroma_db, and retrieve with top-k = 5 while dropping any chunk whose distance is above 0.7. I expect it to produce an indexing script that writes all chunks into ChromaDB and a retrieve(query, k=5) function that returns the top 5 chunks with the distance filter applied. I will verify by running my 5 evaluation questions and inspecting the retrieved chunks: for the factual questions (1, 3, 5) the right professor's reviews should rank on top, the filter should drop off-topic chunks, and Question 4 should confirm that at most 5 of Onarlioglu's reviews ever come back (the expected limitation).

**Milestone 5 — Generation and interface:**
I will use Claude. As input I will give it my Domain, Retrieval Approach, Evaluation Plan, and Anticipated Challenges sections plus the Generation box, with the requirement to call the Groq API with llama-3.3-70b-versatile using a system prompt that answers only from the retrieved review text, cites the professor and source for every answer, says it does not have enough information when the reviews do not cover the question, and reflects disagreement when reviews conflict. This system prompt is how I address grounding (Challenge 2) and source attribution. I expect it to produce a generate_answer(query) function that retrieves and then prompts Groq with those grounded instructions and returns an answer with citations, plus a simple command line interface for asking questions. I will verify by running all 5 evaluation questions against their expected answers, confirming the answers stay grounded in my documents, that Questions 2 and 4 expose the expected limitations (incomplete ranking and an average it cannot fully compute), and that sources are cited.
