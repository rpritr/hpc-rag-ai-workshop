# Job directory

This is the directory you use on the cluster. The labs assume `pwd` ends in `RAG/`.

```bash
bash check_layout.sh
```

| Step | Lab | Command that matters |
|------|-----|----------------------|
| Read the pipeline | [Lab 01](../lab01/README.md) | `nano rag.py` |
| Build the image | [Lab 02](../lab02/README.md) | `apptainer build --fakeroot rag_environment.sif rag_environment.def` |
| Submit the GPU job | [Lab 03](../lab03/README.md) | `sbatch run_rag.sh` |

`rag_environment.sif`, `*.log`, and the model cache are created here or on scratch. They are not part of the git repository.

How to lead the session: [INSTRUCTOR.md](../INSTRUCTOR.md).
