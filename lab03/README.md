# SLAIF Lab 03: Run the pipeline with Slurm
## Ollama in the background, retrieval and the answer in the log

---

## Learning objectives

By the end of this lab you can:

- read a Slurm script that starts a server, pulls models, and runs Python
- submit that script and follow it in the queue
- find the retrieved facts and the answer in the output log
- change the question and submit a second, shorter job

---

## Prerequisites

- `rag_environment.sif` built in Lab 02
- you are in the `RAG/` directory on the login node
- a partition that matches `run_rag.sh`
- about 6 GB of home quota for the model cache, and a node that can give the job 64 CPU cores

```bash
cd RAG
bash check_layout.sh
sinfo
```

If your partition is not called `compute`, edit the `#SBATCH --partition=` line before you submit. The instructor will write the right name on the board.

### CPU by default, GPU when one is free

The script ships ready for a CPU node. On Trdina the idle machines in `sinfo` have `GRES` equal to `(null)`, so a GPU request waits with `Reason=Resources`. Ollama answers this small knowledge base on CPU.

Two cluster facts are already built into `run_rag.sh`:

- The model cache is `$HOME/ollama_models`. Compute nodes cannot create `/scratch/$USER`, and `$SCRATCH` is empty. Home is on shared Ceph, so the job sees the same files.
- The job asks for 64 CPU cores. Inside the container Ollama 0.40 sees all 128 host CPUs and starts 64 threads. `OLLAMA_NUM_THREADS` does not change that choice. If Slurm only grants 4 or 16 cores, each embed takes about a minute and 150 facts do not finish inside the 45 minute limit. With 64 cores one embed takes a fraction of a second.

When `sinfo` shows a free GPU, switch the same script before you submit:

1. Uncomment `#SBATCH --gres=gpu:1` near the top of `run_rag.sh`.
2. In `run_in_container`, change `apptainer exec` to `apptainer exec --nv`.

Both edits go together. `--nv` on a node without a GPU is the wrong half of the switch. A GPU request while every GPU is busy leaves the job pending.

---

## What the job does

`run_rag.sh` is the whole production path:

1. Put the Ollama model cache in `$HOME/ollama_models`.
2. Pick a port from the Slurm job id, so two jobs on one node can both run.
3. Start `ollama serve` inside the image, in the background. With a GPU request, this command also gets `--nv`.
4. Wait until the server answers `ollama list`.
5. Pull `mxbai-embed-large` and `llama3` into that cache.
6. Run `python3 ask.py` in the same image, pointed at that server.
7. Stop the server when the script exits.

Each `apptainer exec` is a new process. They share the server because Apptainer uses the host network, and every command receives the same `OLLAMA_HOST` and `OLLAMA_MODELS`.

---

## Exercise 1: Read the job script

```bash
nano run_rag.sh
```

Read the `#SBATCH` lines first.

| Line | Meaning |
|------|---------|
| `--job-name` | Name you will see in `squeue` |
| `--output` / `--error` | Log files. `%j` becomes the job id |
| `--partition` | Which queue |
| `--cpus-per-task=64` | Enough cores for the 64 threads Ollama starts on its own |
| `--mem` | Memory for both models |
| `--time` | Maximum runtime. The first run includes the model download |
| `#SBATCH --gres=gpu:1` | Present as a comment. Uncomment it only when a GPU is free |

Then read the shell below the headers: model cache, port, the `cleanup` trap, the pull commands, and `python3 ask.py`.

Make the script executable:

```bash
chmod +x run_rag.sh
```

---

## Exercise 2: Submit

```bash
sbatch run_rag.sh
```

The reply looks like:

```text
Submitted batch job 527916
```

Write your job id down. The log files use that number.

---

## Exercise 3: Watch the queue

```bash
squeue -u $USER
```

| State | Meaning |
|-------|---------|
| `PD` | Pending. With a GPU request, this usually means every GPU is busy. With 64 CPUs, the node may simply be full. |
| `R` | Running. The server, the downloads, or the Python script is active. |

Details for one job:

```bash
scontrol show job 527916
```

Replace `527916` with your id.

When the state is `R`, follow the output. The file appears after the job has written its first lines.

```bash
tail -f rag_output_527916.log
```

In another terminal, the server's own log:

```bash
tail -f ollama_server.log
```

Leave the first job running. Cancelling it to "see if it is stuck" throws away the model download.

The quiet stretches are expected:

- the server is starting
- `llama3` is downloading
- the facts are being embedded (`embedded 25/150` and so on)

---

## Exercise 4: Read the result

When `squeue` no longer lists the job:

```bash
cat rag_output_527916.log
cat rag_error_527916.log
```

A healthy output contains four blocks:

```text
Job ... on ...
Ollama host: 127.0.0.1:...
Model cache: /ceph/grid/home/.../ollama_models
Starting Ollama server...
Waiting for Ollama...
Pulling models...
Running RAG script...
Question: What is an interesting fact about cat ears?

Building the search index (150 facts)...
  embedded 25/150
  ...
Retrieved facts:
  [0.xxx] The little tufts of hair in a cat’s ear ...
Answer:
...
Done.
```

The score and the wording of the answer move a little between runs. The retrieved facts should include the ear-furnishings line you found in Lab 01. That line is how you know retrieval worked.

`rag_error_<id>.log` collects Ollama's download progress, because `ollama pull` writes that to standard error. Lines that end in `success` mean the model is on disk. A Python traceback in that file is the thing to read next. `ollama_server.log` is the place to look when the output stops at "Waiting for Ollama...".

A healthy embed line in `ollama_server.log` looks like `POST /api/embed` with a time under a second. A time of 30 to 60 seconds means the job has fewer cores than Ollama's 64 threads.

Accounting, once the job has left the queue:

```bash
sacct -j 527916 --format=JobID,JobName,State,Elapsed,ExitCode
```

---

## Exercise 5: Ask a second question

The models are already in the cache, so this job spends its time on retrieval and the answer.

Edit `ask.py` and replace the question. Keep the rest of the file.

```python
query = "Who was the first cat in space?"
```

Submit again:

```bash
sbatch run_rag.sh
squeue -u $USER
```

In the new log, the retrieved facts should mention Felicette. Then try one you choose yourself. A reliable third question:

```python
query = "How much of the day do cats spend sleeping?"
```

You are editing a text file and resubmitting. The image stays as it is.

---

## Bonus

Cancel a job you do not want anymore:

```bash
scancel 527916
```

See why a pending job is waiting:

```bash
squeue -u $USER -o "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %R"
```

The last column is the reason, such as `Resources` or a bad partition.

---

## Checkpoint

You have:

- a job id that reached a completed state
- an output log that shows retrieved facts and an answer
- a second job with a different question

---

## Reflection

1. Why does the Slurm script start `ollama serve` itself instead of assuming a system-wide server?
2. Why does this cluster keep `OLLAMA_MODELS` in `$HOME`, and why does the job ask for 64 CPU cores?
3. Why does the second job finish faster than the first?
4. What would you change to answer questions about a different text file?
5. Which part of the log tells you the search worked, separate from the quality of the prose?

---

## Expected outcome

You can submit a containerized RAG job, read the answer from the Slurm log, and ask a new question by editing `ask.py`.

---

## SLAIF

Part of the SLAIF labs on portable research environments. Previous labs in this workshop: [Lab 01](../lab01/README.md), [Lab 02](../lab02/README.md). The container introduction is the [Apptainer workshop](https://github.com/rpritr/hpc-apptainer-workshop).
