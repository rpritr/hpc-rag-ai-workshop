# Job directory

This is the directory you use on the cluster. The labs assume `pwd` ends in `RAG/`.

```bash
bash check_layout.sh
```

| Step | Lab | Command that matters |
|------|-----|----------------------|
| Read the pipeline | [Lab 01](../lab01/README.md) | `nano rag.py` |
| Build the image | [Lab 02](../lab02/README.md) | `apptainer build --fakeroot rag_environment.sif rag_environment.def` |
| Submit the job | [Lab 03](../lab03/README.md) | `sbatch run_rag.sh` |

The job uses 64 CPU cores. When a GPU is free, uncomment `#SBATCH --gres=gpu:1` in `run_rag.sh` and add `--nv` after `apptainer exec`. The model cache is `$HOME/ollama_models`.

`rag_environment.sif` and `*.log` are created here. They are not part of the git repository.

How to lead the session: [INSTRUCTOR.md](../INSTRUCTOR.md).
