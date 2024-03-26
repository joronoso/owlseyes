from openai import OpenAI
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

# Without parameters, the API key will be retrieved from the environment variable OPENAI_API_KEY.
# It can also be provided directly using the apiKey parameter, as in the commented line below.
#client = OpenAI(api_key='api-key',)
client = OpenAI()
model = 'gpt-3.5-turbo' # 'gpt-4-turbo-preview' # For GPT 4-Turbo

# By default, the library will take the API key from the GOOGLE_API_KEY environment variable.
# You may also pass it directly through the api_key parameter, using the commented line below
# genai.configure(api_key=API-KEY)

gemini = genai.GenerativeModel(model_name="gemini-pro",
            generation_config=generation_config,
            safety_settings=safety_settings)

# Set initial message for GPT as system role, which will dictate the model's behavior during the entire interaction.
messages_openai = [{'role': 'system', 'content': '''You are the Democratic presidential candidate. 
                    You are in a debate with the Republican candidate. You are discussing the issue of healthcare. 
                    Respond with persuasive arguments, presenting the Democratic viewpoint on the subject. 
                    It is especially important that you try to put your opponent in a bad light whenever possible. 
                    You are first to talk in the debate, stating your initial stance on the issue and attacking the opponent.'''}]

# Set initial messages for Gemini
messages_gemini = [{'role':'user', 'parts': ['''You are the Democratic presidential candidate. 
                    You are in a debate with the Democratic candidate. You are discussing the issue of healthcare. 
                    Respond with persuasive arguments, presenting the Republican viewpoint on the subject. 
                    It is especially important that you try to put your opponent in a bad light whenever possible.''']},
                {'role':'model', 'parts': ['OK']}]

# Limit conversation to 5 messages from each model. 10 in total.
for i in range(5):
    # Call chat completions service to get GPT's response. Send the complete list of messages so the conversation context is not lost.
    response = client.chat.completions.create(
        model=model,
        messages=messages_openai,
        stream=True
    )

    print('Democrat:')
    text_response = ''
    for chunk in response:
        chunk_txt = chunk.choices[0].delta.content or '\n'
        text_response += chunk_txt 
        print(chunk_txt, end='', flush=True)
    
    messages_openai.append({'role': 'assistant', 'content': text_response})
    messages_gemini.append({'role':'user', 'parts': [text_response]})

    # Call generate_content service to get Gemini's response. Send the complete list of messages so the conversation context is not lost.
    response = gemini.generate_content(messages_gemini, stream=True)

    print('Republican:')
    text_response = ''
    for chunk in response:
        chunk_txt = chunk.text
        text_response += chunk_txt 
        print(chunk_txt, end='', flush=True)
    print()
    messages_openai.append({'role': 'user', 'content': text_response})
    messages_gemini.append({'role':'model', 'parts': [text_response]})



