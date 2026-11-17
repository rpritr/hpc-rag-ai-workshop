#!/bin/bash
# Quick check before the container build and the Slurm submit.

missing=0
for f in cat-facts.txt rag.py ask.py rag_environment.def run_rag.sh; do
    if [[ -f "$f" ]]; then
        echo "ok       $f"
    else
        echo "MISSING  $f"
        missing=1
    fi
done

if [[ -f rag_environment.sif ]]; then
    echo "ok       rag_environment.sif"
else
    echo "pending  rag_environment.sif  (built in lab 02)"
fi

exit "$missing"
