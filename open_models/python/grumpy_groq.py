from groq import Groq

messages = [{"role": "system", "content": "You're an old grumpy and cantankerous person. You respond to everything with complaints and apathy, although you end up helping with what you're asked."}]
client = Groq()
# The conversation will continue until we leave an empty message
while len(text_user := input("What do you want to say to the grumpy chatbot?\n> ").strip())>0:

    # Add the new entry to the list of messages, with role "user".
    messages.append({"role": "user", "content": text_user})

    # Call chat completions service to get the response from the model. Send the complete list of messages so the conversation context is not lost.
    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        stream=True)

    response_message = ""
    for chunk in stream:
        chunk_txt = chunk.choices[0].delta.content or ""
        response_message += chunk_txt
        print(chunk_txt, end="", flush=True)
    print("")

    # Display response and add it to the list of messages as role "assistant".
    messages.append({"role": "assistant", "content": response_message})
