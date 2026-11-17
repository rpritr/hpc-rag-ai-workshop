# Source handout

`MODULE_5_APPTAINER_AND_SLURM.txt` is the original module this workshop was written from.

The labs in the repository root are the version to teach. They keep the same pipeline and add a job port, a wait loop for the Ollama server, unbuffered logs, and a container recipe without PyTorch. The pipeline calls Ollama over HTTP and does not import PyTorch or Transformers.
