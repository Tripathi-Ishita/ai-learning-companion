from rag.rag_chain import ask

# In-context question — should answer correctly
print("Q1: how do I say thank you in Korean?")
print("A1:", ask("how do I say thank you in Korean?"))

# Out-of-context question — should REFUSE, not hallucinate
print("\nQ2: what is the capital of France?")
print("A2:", ask("what is the capital of France?"))