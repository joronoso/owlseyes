import OpenAI from 'openai';
import * as readline from 'node:readline/promises';
import { GoogleGenerativeAI } from '@google/generative-ai';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});


// Without parameters, the API key will be retrieved from the environment variable OPENAI_API_KEY.
// It can also be provided directly using the apiKey parameter, as in the commented line below.

// const client = new OpenAI({ apiKey: 'api-key' });
const client = new OpenAI();
const model = 'gpt-3.5-turbo'; // 'gpt-4-1106-preview' // Para GPT 4-Turbo

// Retrieve API key from GOOGLE_API_KEY environment variable.
const genai = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);

const gemini = genai.getGenerativeModel(
    {
        model: 'gemini-pro',
        safetySettings: [
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
        ],
        generationConfig: {
            //candidateCount: 1,
            //maxOutputTokens: 1700,
            stopSequences: [],
            temperature: 1,
            topK: 1,
            topP: 1
        }

    });

// Set initial message for GPT as system role, which will dictate the model's behavior during the entire interaction.
let messages_openai = [{
    'role': 'system', 'content': 'You are the Democratic presidential candidate. \
        You are in a debate with the Republican candidate. You are discussing the issue of healthcare. \
        Respond with persuasive arguments, presenting the Democratic viewpoint on the subject. \
        It is especially important that you try to put your opponent in a bad light whenever possible. \
        You are first to talk in the debate, stating your initial stance on the issue and attacking the opponent.'
}];

// Set initial messages for Gemini
let messages_gemini = [{
    'role': 'user', 'parts': [{
        'text': 'You are the Democratic presidential candidate. \
            You are in a debate with the Democratic candidate.You are discussing the issue of healthcare. \
            Respond with persuasive arguments, presenting the Republican viewpoint on the subject. \
            It is especially important that you try to put your opponent in a bad light whenever possible.'
    }]
}, { 'role': 'model', 'parts': [{ 'text': 'OK' }] }];

// Limit conversation to 5 messages from each model. 10 in total.
for (let i = 0; i < 5; i++) {
    // Call chat completions service to get GPT's response. Send the complete list of messages so the conversation context is not lost.
    const response_openai = await client.chat.completions.create({
        model: model,
        messages: messages_openai,
        stream: true
    });

    console.log('Democrat:');
    let text_response = '';
    for await (const chunk of response_openai) {
        const trozo_txt = chunk.choices[0]?.delta?.content || '\n';
        process.stdout.write(trozo_txt);
        text_response += trozo_txt;
    }

    messages_openai.push({ 'role': 'assistant', 'content': text_response });
    messages_gemini.push({ 'role': 'user', 'parts': [{ 'text': text_response }] });

    // Call generateContentStream service to get Gemini's response. Send the complete list of messages so the conversation context is not lost.
    const response_gemini = await gemini.generateContentStream({ 'contents': messages_gemini });

    console.log('\nRepublican:');
    text_response = '';
    for await (const chunk of response_gemini.stream) {
        const chunk_txt = chunk.text();
        text_response += chunk_txt;
        process.stdout.write(chunk_txt);
    }
    console.log('\n');

    messages_openai.push({ 'role': 'user', 'content': text_response });
    messages_gemini.push({ 'role': 'model', 'parts': [{ 'text': text_response }] });
}

rl.close();
