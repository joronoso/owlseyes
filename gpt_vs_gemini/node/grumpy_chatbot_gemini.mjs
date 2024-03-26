import * as readline from 'node:readline/promises';
import { GoogleGenerativeAI } from '@google/generative-ai';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Retrieve API key from GOOGLE_API_KEY environment variable.
const genai = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);

// Window size we shouldn't exceed (max varies by model).
const window = 4096

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

// Set initial messages, which will dictate the model's behavior during the entire interaction.
let messages = [{ 'role': 'user', 'parts': [{ 'text': 'You\'re an old grumpy and cantankerous person. You respond to everything with complaints and apathy, although you end up helping with what you\'re asked.' }] },
{ 'role': 'model', 'parts': [{ 'text': 'OK' }] }];

// Array to store number of tokens for each exchange (question-answer).
let tokens_exchange = [];

// Size of the longest question-answer we have received.
let max_exchange = 0

// The conversation will continue until we leave an empty message.
let text_user;
while (text_user = (await rl.question('What do you want to say to the grumpy chatbot?\n> ')).trim()) {
    // Calculate tokens for the last exchange, store in the list, an update max_exchange
    const last_exchange = (await gemini.countTokens({ 'contents': messages.slice(messages.length - 2, messages.length) })).totalTokens;
    tokens_exchange.push(last_exchange);
    max_exchange = max_exchange > last_exchange ? max_exchange : last_exchange;

    // We want to leave enough space to accommodate the maximum exchange previously received.
    // If there's not enough space, we delete as many exchanges as necessary from the beginning (except for the first two).
    const sum_tokens = tokens_exchange.reduce((sum, elem) => sum + elem, 0);
    if (sum_tokens + max_exchange > window) {
        let i = 2;
        let suma = tokens_exchange[1];
        while (sum_tokens + max_exchange - suma > window) {
            suma += tokens_exchange[i];
            i++;
        }
        messages.splice(2, 2 * (i - 1));
        tokens_exchange.splice(1, i - 1);
    }

    // Add the new entry to the list of messages, with role "user"
    messages.push({ 'role': 'user', 'parts': [{ 'text': text_user }] });

    // Call generateContentStream to get the model's response. Send the complete list of messages so the conversation context is not lost.
    const response = await gemini.generateContentStream({ 'contents': messages });

    let text_response = '';
    for await (const chunk of response.stream) {
        const chunk_txt = chunk.text();
        text_response += chunk_txt;
        process.stdout.write(chunk_txt);
    }

    // Add response to the list of messages as role "model"
    messages.push({ 'role': 'model', 'parts': [{ 'text': text_response }] });

    console.log('\n');
}

rl.close();
