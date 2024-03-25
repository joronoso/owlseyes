from openai import OpenAI
import tiktoken

# Without parameters, the API key will be retrieved from the environment variable OPENAI_API_KEY.
# It can also be provided directly using the apiKey parameter, as in the commented line below.
#client = OpenAI(api_key='api-key',)
client = OpenAI()
model = 'gpt-3.5-turbo' # 'gpt-4-turbo-preview' # For GPT 4-Turbo

# This value depends on the model.
fixed_per_message = 3

# Window size we shouldn't exceed (max varies by model). 
window = 4096

# Get tiktoken encoding object for the model.
enc = tiktoken.encoding_for_model(model)

# Start with the system role message, which dictates the behavior of the model for the whole interaction.
messages = [{'role': 'system', 'content': 'You\'re an old grumpy and cantankerous person. You respond to everything with complaints and apathy, although you end up helping with what you\'re asked.'}]

# List to store number of tokens for each message.
tokens_message = [len(enc.encode(messages[0]['role'])) + len(enc.encode(messages[0]['content'])) + fixed_per_message]

# Track size of the longest response we've received.
max_response = 0

while True:
    # The conversation will continue until we leave an empty message
    text_user = input('What do you want to say to the grumpy chatbot?\n> ').strip()
    if len(text_user)==0: 
        break

    # Add the new entry to the list of messages, with role "user", and its size to tokens_message.
    messages.append({'role': 'user', 'content': text_user})
    tokens_message.append(len(enc.encode('user')) + len(enc.encode(text_user)) + fixed_per_message)

    # Leave enough space to be able to receive a response as long as the longest received.
    # If there's not enough space, delete as many messages as needed, oldest first.
    sum_tokens = sum(tokens_message)
    if sum_tokens + 3 + max_response > window:
        i = 2
        suma = tokens_message[1]
        while sum_tokens + max_response + 3 - suma > window:
            suma += tokens_message[i]
            i += 1
        del messages[1:i]
        del tokens_message[1:i]

    # Call chat completions service to get the response from the model. Send the complete list of messages so the conversation context is not lost.
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )

    # Display and store the pieces of the message as they are received.
    text_response = ''
    for piece in response:
        piece_txt = piece.choices[0].delta.content or '\n'
        text_response += piece_txt 
        print(piece_txt, end='', flush=True)

    # Add response to the list of messages as role 'assistant', and its size to tokens_message.
    messages.append({'role': 'assistant', 'content': text_response})
    tokens_response = len(enc.encode('assistant')) + len(enc.encode(text_response)) + fixed_per_message
    tokens_message.append(tokens_response)

    # Update max response if needed.
    if tokens_response > max_response:
        max_response = tokens_response
