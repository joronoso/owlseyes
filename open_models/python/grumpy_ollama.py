import ollama

messages = [{"role": "system", "content": "You're an old grumpy and cantankerous person. You respond to everything with complaints and apathy, although you end up helping with what you're asked."}]

# The conversation will continue until we leave an empty message
while len(text_user := input("What do you want to say to the grumpy chatbot?\n> ").strip())>0:

    # Add the new entry to the list of messages, with role "user".
    messages.append({"role": "user", "content": text_user})

    # Call chat completions service to get the response from the model. Send the complete list of messages so the conversation context is not lost.
    stream = ollama.chat(
        model="phi3.5:latest",
        messages=messages,
        stream=True)

    response_message = ""
    for chunk in stream:
        response_message += chunk["message"]["content"]
        print(chunk["message"]["content"], end="", flush=True)
    print("")

    # Display response and add it to the list of messages as role "assistant".
    messages.append({"role": "assistant", "content": response_message})
