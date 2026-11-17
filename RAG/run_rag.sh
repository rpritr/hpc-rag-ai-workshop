#!/bin/bash
#SBATCH --job-name=rag_ollama_gpu
#SBATCH --output=rag_output_%j.log
#SBATCH --error=rag_error_%j.log
#SBATCH --partition=compute
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:45:00

# Confirm the partition name with `sinfo` before the session.
# The first run is long because it downloads the models.
# Later runs reuse /scratch/$USER/ollama_models and finish faster.

set -euo pipefail

cd "${SLURM_SUBMIT_DIR:-$PWD}"

export OLLAMA_MODELS="/scratch/${USER}/ollama_models"
mkdir -p "$OLLAMA_MODELS"

# One port per job, so two students on the same node do not collide.
PORT=$((11434 + SLURM_JOB_ID % 1000))
export OLLAMA_HOST="127.0.0.1:${PORT}"
export PYTHONUNBUFFERED=1

SIF="rag_environment.sif"

cleanup() {
    status=$?
    if [[ -n "${SERVER_PID:-}" ]]; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    exit "$status"
}
trap cleanup EXIT

run_in_container() {
    apptainer exec --nv \
        --env OLLAMA_MODELS="$OLLAMA_MODELS" \
        --env OLLAMA_HOST="$OLLAMA_HOST" \
        --env PYTHONUNBUFFERED=1 \
        "$SIF" "$@"
}

echo "Job ${SLURM_JOB_ID} on $(hostname)"
echo "Ollama host: ${OLLAMA_HOST}"
echo "Model cache: ${OLLAMA_MODELS}"

echo "Starting Ollama server on GPU..."
run_in_container ollama serve > ollama_server.log 2>&1 &
SERVER_PID=$!

echo "Waiting for Ollama..."
ready=0
for _ in $(seq 1 30); do
    if run_in_container ollama list >/dev/null 2>&1; then
        ready=1
        break
    fi
    sleep 2
done
if [[ "$ready" -ne 1 ]]; then
    echo "Ollama did not start. See ollama_server.log" >&2
    exit 1
fi

echo "Pulling models..."
run_in_container ollama pull mxbai-embed-large
run_in_container ollama pull llama3

echo "Running RAG script..."
run_in_container python3 ask.py

echo "Done."
