import ollama

prompt = "인공지능의 미래를 한 문장으로"
 
for temp in [0.0, 0.7, 1.5]:
    for i in range(3):
        response = ollama.generate(
            model="gemma3:4b",
            prompt=prompt,
            options={"temperature": temp}
            )
