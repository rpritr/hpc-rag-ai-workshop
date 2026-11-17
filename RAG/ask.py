# ask.py
# Batch entry point. A Slurm job has no keyboard, so the question is fixed.
# Change `query` and submit the job again to ask something else.
#
# Other questions that work well with cat-facts.txt:
#   "Who was the first cat in space?"
#   "How much of the day do cats spend sleeping?"

from rag import answer

query = "What is an interesting fact about cat ears?"

print(f"Question: {query}\n")
response = answer(query)
print("\nAnswer:")
print(response)
