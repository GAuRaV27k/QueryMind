# import requests

# async def generate_answer_llama(prompt: str):
#     try:
#         print("inside generate_answer_llama")

#         response = requests.post(
#             "http://localhost:11434/api/generate",
#             json={
#                 "model": "qwen3-coder:30b",
#                 "prompt": prompt,
#                 "stream": False,
#                 "options": {
#                     "temperature": 0.3,
#                     "num_predict": 1024
#                 }
#             },
#             timeout=120
#         )

#         response.raise_for_status()

#         result = response.json()

#         print("llama response received")

#         return result["response"]

#     except Exception as e:
#         print(f"Generation Error: {e}")
#         return None
import time 
start = time.time()

for i in range(1_000):
    print(i**2)

end = time.time()
print(f"{end-start:.2f}")