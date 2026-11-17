---
marp: true
paginate: true
title: RAG on HPC
---

<!--
Speaker notes, about 20 minutes, then Lab 01.
One heading is one beat. Commands stay in the labs.
Marp: each --- is a slide. This comment is not shown.
-->

## RAG on HPC

SLAIF workshop

A local knowledge base, a container, a GPU job.

About 3 hours. Three labs.

---

## What you will do today

- Read a RAG program that fits on one screen
- Build an Apptainer image around it
- Submit it with Slurm
- Change the question and submit again

---

## One picture

```text
cat-facts.txt
      |
      v
embeddings  ---- top 4 lines ----> llama3 ----> answer
      ^
   your question
```

Search first. The model writes from the lines you found.

---

## Why a text file

One fact per line. About 150 lines.

You can `grep` the file and predict what the job should retrieve.

The domain is cats so the room can judge the answers.

---

## Two models, one server

| Piece | Role |
|-------|------|
| `mxbai-embed-large` | Vectors for search |
| `llama3` | The written answer |
| Ollama | Serves both, on the compute node, only while the job runs |

Python asks Ollama over HTTP. The weights are not pip packages.

---

## Five files

| File | You touch it when |
|------|-------------------|
| `cat-facts.txt` | You want a different knowledge base |
| `rag.py` | You want to see how search and the prompt work |
| `ask.py` | You want to ask a new question |
| `rag_environment.def` | You build the image |
| `run_rag.sh` | You submit the job |

---

## Where the work runs

Login node: edit files, build the image.

Compute node: Ollama, embeddings, the answer. You get there with `sbatch`, and you come back through the log file. A free GPU is optional. The script as shipped uses 64 CPU cores.

---

## Lab 01

Open `RAG/rag.py`.

Leave the lab able to say which function embeds, which function searches, and why `ask.py` has no `input()`.

---

## Lab 02

`apptainer build --fakeroot rag_environment.sif rag_environment.def`

The image is the software. The facts and the models stay outside it.

Checkpoint: `import ollama, numpy` prints `ok`.

---

## Lab 03

`sbatch run_rag.sh`

Then `squeue`, then the output log.

The first run downloads models. The second run asks a new question and is shorter.

---

## What "it worked" looks like

The log contains:

- the question
- `Retrieved facts:` with a line you can find in `cat-facts.txt`
- a short answer under that
- `Done.`

For the first question, look for ear furnishings.

---

## If the queue is quiet

`PD` means it is waiting for a GPU.

An empty log during `R` usually means a download. Look at `ollama_server.log`.

A Python traceback is in `rag_error_<jobid>.log`.

---

## Close

Edit one string. Submit again.

The container does not change.

That is the workflow: data and question outside, software in the image, GPU time through Slurm.

---

## Series

Previous workshop: Apptainer, then Apptainer on Slurm.

This workshop: the same tools, with a RAG pipeline inside.
