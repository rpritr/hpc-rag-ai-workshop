# SLAIF Lab 02: Package the RAG environment
## One definition file, one image, the same stack on every node

---

## Learning objectives

By the end of this lab you can:

- read an Apptainer definition file section by section
- build `rag_environment.sif` with `--fakeroot`
- check that Python inside the image can import `ollama` and `numpy`

The image contains the software. It does not contain `cat-facts.txt`, `ask.py`, or the model weights. Those stay outside, in your directory and on scratch, so you can change the question without rebuilding.

---

## Prerequisites

- Lab 01 finished, you are still in `RAG/`
- Apptainer on the login node
- permission to build with `--fakeroot`
- a network path to Ubuntu package mirrors and to `https://ollama.com`

```bash
apptainer --version
pwd
bash check_layout.sh
```

---

## Exercise 1: Read the definition file

```bash
nano rag_environment.def
```

Section headers start at the beginning of the line.

| Section | What it does here |
|---------|-------------------|
| `Bootstrap` / `From` | Start from the Ubuntu 22.04 Docker image |
| `%post` | Install Python, curl, zstd, the Ollama server, and the Python packages |
| `%environment` | `PATH` includes `/usr/local/bin`, and Python prints straight away |
| `%runscript` | `apptainer run` forwards arguments to the command you give it |
| `%labels`, `%help` | Text you can inspect later |

`%post` installs:

- `python3` and `pip`, because the pipeline is Python
- `curl`, `ca-certificates`, and `zstd`, because the Ollama install script needs them
- the `ollama` binary, via the upstream install script
- the Python packages `ollama` and `numpy`

The GPU driver stays on the host. Lab 03 passes it in with `--nv` at run time. It is not installed into the image.

PyTorch and Transformers are not in this recipe. The module handout lists them, and this pipeline never imports them. Ollama runs the models. Leaving the extra packages out keeps the build inside the session.

---

## Exercise 2: Build the image

This is the long command of the workshop. Start it, then keep reading. A few minutes to tens of minutes is normal, depending on the mirror and the disk.

```bash
apptainer build --fakeroot rag_environment.sif rag_environment.def
```

`--fakeroot` lets an unprivileged user run the install steps that expect root inside the build. You do not get root on the cluster.

When the command returns, list the image:

```bash
ls -lh rag_environment.sif
```

The `.sif` file is large and stays out of git. It has to sit next to `ask.py` when you submit the job.

---

## Exercise 3: Smoke test

This checks the image without a GPU and without downloading models.

```bash
apptainer exec rag_environment.sif python3 -c "import ollama, numpy; print('ok')"
apptainer exec rag_environment.sif ollama --version
apptainer exec rag_environment.sif cat /etc/os-release
```

You want `ok`, an Ollama version line, and Ubuntu 22.04.

Your files are visible inside the container because Apptainer exposes the current directory:

```bash
apptainer exec rag_environment.sif python3 -c "import rag; print(len(rag.load_facts()))"
```

That prints the number of facts. It does not call Ollama. Calling the models comes in Lab 03, where the server is running on a GPU node.

---

## Exercise 4: Inspect

```bash
apptainer inspect rag_environment.sif
apptainer inspect --helpfile rag_environment.sif
```

Use the labels and the help text to confirm you built the image from this lab, not an older file in the same directory.

---

## Bonus

A check that uses the image and does not rebuild it:

```bash
apptainer exec rag_environment.sif python3 -c "import numpy as np; print(float(np.array([1, 2, 3]).mean()))"
```

Expected output: `2.0`.

Rebuilding to add another package waits until after Lab 03. The GPU job matters more than a second image build during the session.

---

## Checkpoint

Everyone needs these before `sbatch`:

```bash
bash check_layout.sh
apptainer exec rag_environment.sif python3 -c "import ollama, numpy; print('ok')"
```

`check_layout.sh` now prints `ok` for `rag_environment.sif` as well.

---

## Reflection

1. Which steps run once at build time, and which steps run on every job?
2. Why do the fact file and the model weights stay outside the image?
3. What does `--fakeroot` let you do on a shared cluster?

---

## Expected outcome

`rag_environment.sif` is in `RAG/`, and Python inside it imports `ollama` and `numpy`.

---

## Next lab

Submit the GPU job: [Lab 03](../lab03/README.md).

---

## SLAIF

Part of the SLAIF labs on portable research environments.
