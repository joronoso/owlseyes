import google.generativeai as genai

generation_config = {
    "candidate_count": 1,
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

# Window size we shouldn't exceed (max varies by model). 
window = 4096

# By default, the library will take the API key from the GOOGLE_API_KEY environment variable.
# You may also pass it directly through the api_key parameter, using the commented line below
# genai.configure(api_key=API-KEY)

gemini = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

# Set initial messages, which will dictate the model's behavior during the entire interaction.
messages = [{'role':'user', 'parts': ['You\'re an old grumpy and cantankerous person. You respond to everything with complaints and apathy, although you end up helping with what you\'re asked.']},
            {'role':'model', 'parts': ['OK']}]

# List to store number of tokens for each exchange (question-answer).
tokens_exchange = [ ]

# Size of the longest question-answer we have received.
max_exchange = 0

# The conversation will continue until we leave an empty message. As Google's API requires Python 3.9, we'll use the walrus operator.
while len(text_user := input('What do you want to say to the grumpy chatbot?\n> ').strip())>0:

    # Calculate tokens for the last exchange, store in the list, an update max_exchange
    last_exchange = int(gemini.count_tokens(messages[-2:]).total_tokens)
    tokens_exchange.append( last_exchange )
    max_exchange = max(max_exchange, last_exchange)

    # We want to leave enough space to accommodate the maximum exchange previously received.
    # If there's not enough space, we delete as many exchanges as necessary from the beginning (except for the first two).
    sum_tokens = sum(tokens_exchange)
    if sum_tokens + max_exchange > window:
        i = 2
        suma = tokens_exchange[1]
        while sum_tokens + max_exchange - suma > window:
            suma += tokens_exchange[i]
            i += 1
        del messages[2:2*i]
        del tokens_exchange[1:i]

    # Add the new entry to the list of messages, with role "user"
    messages.append({'role':'user', 'parts': [text_user]})

    # Call generate_content service to get the model's response. Send the complete list of messages so the conversation context is not lost.
    response = gemini.generate_content(messages, stream=True)

    text_response = ''
    for chunk in response:
        chunk_txt = chunk.text
        text_response += chunk_txt 
        print(chunk_txt, end='', flush=True)

    # Add response to the list of messages as role "model"
    messages.append({'role':'model', 'parts': [text_response]})
    print('\n')
