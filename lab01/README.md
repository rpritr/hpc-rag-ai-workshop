# SLAIF Lab 01: A RAG pipeline you can read
## Facts in a text file, retrieval, then a local answer

---

## Learning objectives

By the end of this lab you can:

- describe retrieval-augmented generation as search first, answer second
- find the knowledge base, the retrieval code, and the question
- explain why a batch script cannot call `input()`

You will not start the models in this lab. That happens on a GPU node in Lab 03. The login node is for reading and editing.

---

## The pipeline

```text
cat-facts.txt  --->  embeddings  --->  top 4 lines  --->  llama3  --->  answer
                         ^
                         |
                       ask.py
```

Two models, both served by Ollama:

| Model | Job in this lab |
|-------|-----------------|
| `mxbai-embed-large` | Turns a line of text into a vector so we can search |
| `llama3` | Writes the answer from the lines we retrieved |

The Python program never loads the model weights itself. It talks to the Ollama server.

---

## Prerequisites

- the repository cloned on the cluster login node, or on your laptop for reading
- a terminal in the `RAG/` directory

```bash
cd RAG
bash check_layout.sh
```

Every required file should print `ok`. `rag_environment.sif` may print `pending`. That file appears in Lab 02.

---

## Exercise 1: The knowledge base

```bash
wc -l cat-facts.txt
head -n 5 cat-facts.txt
```

Each non-empty line is one fact. That is the whole index. There is no PDF parser and no database.

Search the file the way the program will, by eye:

```bash
grep -n -i "ear" cat-facts.txt
grep -n -i "space" cat-facts.txt
grep -n -i "sleep" cat-facts.txt
```

Remember one line from each search. You will look for it in the job log in Lab 03.

---

## Exercise 2: Walk through `rag.py`

Open the file and read it from top to bottom.

```bash
nano rag.py
```

Stop at each of these names:

1. `KB_PATH`, `EMBED_MODEL`, `LLM_MODEL`, `TOP_K` — the four settings that matter.
2. `load_facts` — skips blank lines.
3. `embed` — one Ollama call, one vector back.
4. `KnowledgeBase.search` — cosine similarity, highest scores first, keep `TOP_K`.
5. `answer` — prints the chosen facts, then asks `llama3` to answer from those facts only.

The prompt in `answer` tells the model to use the retrieved lines and to say when they are not enough. Temperature is `0` so a live demo stays stable.

`get_kb` builds the index on the first question and keeps it for the rest of the process. Building means one embedding call per fact, so the log prints progress every 25 lines.

---

## Exercise 3: The batch question

Open `ask.py`.

```bash
nano ask.py
```

The file is short on purpose. A Slurm job has no keyboard attached, so the question is a Python string. Lab 03 submits this file unchanged, then you edit that string and submit again.

The flow inside `ask.py`:

1. Print the question.
2. Call `answer(query)`.
3. Print whatever string comes back.

`answer` also prints the retrieved facts, so the log shows the search and the final paragraph as two separate blocks.

---

## Checkpoint

Before you leave this lab, you should be able to answer these without looking them up for long:

1. Which file is the knowledge base?
2. Which function turns a sentence into a vector?
3. How many facts does the model see when it writes the answer?
4. Why is the question written as a variable instead of `input()`?

---

## Reflection

1. What does the program retrieve, and what does it generate?
2. What would you edit to ask about a different domain, the text file or the model name?
3. Why is a plain text file a useful knowledge base for a first HPC run?

---

## Expected outcome

You can point at the five files in `RAG/` and say what each one contributes. The models have not run yet.

---

## Next lab

Build the Apptainer image that contains Python, NumPy, and Ollama: [Lab 02](../lab02/README.md).

---

## SLAIF

Part of the SLAIF labs on portable research environments.
