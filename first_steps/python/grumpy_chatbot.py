from openai import OpenAI

# Without parameters, the API key will be retrieved for environment variable OPENAI_API_KEY.
# It can also be provided directly using the apiKey parameter, as in the commented line below.
#client = OpenAI(api_key='clave-de-api',)
client = OpenAI()
modelo = 'gpt-4-1106-preview' # GPT 4-Turbo

# Start with the system role message, which dictates the behavior of the model for the whole interaction.
messages = [{'role': 'system', 'content': 'You\'re an old grumpy and cantankerous person. You respond to everything with complaints and apathy, although you end up helping with what you\'re asked.'}]
while True:
    # The conversation will continue until we leave an empty message/
    text_user = input('What do you want to say to the grumpy chatbot?\n> ').strip()
    if len(text_user)==0: 
        break

    # Add the new entry to the list of messages, with role "user".
    messages.append({'role': 'user', 'content': text_user})

    # Call chat completions service to get the response from the model. Send the complete list of messages so the conversation context is not lost.
    response = client.chat.completions.create(
        model=modelo,
        messages=messages
    )

    # Display response and add it to the list of messages as role "assistant".
    print(response.choices[0].message.content)
    messages.append({'role': 'assistant', 'content': response.choices[0].message.content})

