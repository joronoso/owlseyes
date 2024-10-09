from transformers import pipeline

# Gemma 2 doesn't support system prompts
messages = [{"role": "user", "content": "You're an old grumpy and cantankerous person. You respond to everything with complaints and apathy, although you end up helping with what you're asked."},
            {"role": "assistant", "content": "OK."}]

pipe = pipeline(
    task="text-generation",
    model="google/gemma-2-2b-it",
    device="cuda",  # "mps" for Mac, "cpu" if no GPU
    token="HF_TOKEN", 
)

# The conversation will continue until we leave an empty message
while len(text_user := input("What do you want to say to the grumpy chatbot?\n> ").strip())>0:
    # Add the new entry to the list of messages, with role "user".
    messages.append({"role": "user", "content": text_user})

    # Generate the model's response using pipe. Send the complete list of messages so the conversation context is not lost.
    response_message = pipe(messages, max_new_tokens=256)[0]["generated_text"][-1]["content"]

    # Display response and add it to the list of messages as role "assistant".
    print(response_message)
    messages.append({"role": "assistant", "content": response_message})