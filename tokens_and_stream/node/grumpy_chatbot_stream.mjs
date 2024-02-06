import OpenAI from 'openai';
import * as readline from 'node:readline/promises'
import { encoding_for_model } from 'tiktoken';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Without parameters, the API key will be retrieved for environment variable OPENAI_API_KEY.
// It can also be provided directly using the apiKey parameter, as in the commented line below.
// const client = new OpenAI({ apiKey: 'api-key' });
const client = new OpenAI();
const model = 'gpt-3.5-turbo'; // 'gpt-4-1106-preview' // For GPT 4-Turbo

// This value depends on the model.
const fixed_per_message = 3;

// Window size we shouldn't exceed (max varies by model). 
const window = 4096;

// Get tiktoken encoding object for the model.
const enc = encoding_for_model(model);

// Start with the system role message, which dictates the behavior of the model for the whole interaction.
let messages = [{ 'role': 'system', 'content': 'You\'re an old grumpy and cantankerous person. You respond to everything with complaints and apathy, although you end up helping with what you\'re asked.' }];

// Array paralelo, donde guardaremos el número de tokens de cada mensaje
let tokens_message = [enc.encode(messages[0].role).length + enc.encode(messages[0].content).length + fixed_per_message];

// Track size of the longest response we've received.
let max_response = 0;

// The conversation will continue until we leave an empty message
let text_user;
while (text_user = (await rl.question('What do you want to say to the grumpy chatbot?\n> ')).trim()) {
    // Add the new entry to the list of messages, with role "user", and its size to tokens_message.
    messages.push({ 'role': 'user', 'content': text_user });
    tokens_message.push(enc.encode('user').length + enc.encode(text_user).length + fixed_per_message);

    // Leave enough space to be able to receive a response as long as the longest received.
    // If there's not enough space, delete as many messages as needed, oldest first.
    const sum_tokens = tokens_message.reduce(((a, b) => a + b));
    if (sum_tokens + max_response + 3 > window) {
        let i = 1;
        for (let sum = 0; sum_tokens + max_response + 3 - sum > window; i++)
            sum += tokens_message[i];
        messages.splice(1, i);
        tokens_message.splice(1, i);
    }

    // Call chat completions service to get the response from the model. Send the complete list of messages so the conversation context is not lost.
    const response = await client.chat.completions.create({
        model: model,
        messages: messages,
        stream: true
    });

    // Display and store the pieces of the message as they are received.
    let piece_list = [];
    for await (const piece of response) {
        const piece_txt = piece.choices[0]?.delta?.content || '\n';
        process.stdout.write(piece_txt);
        piece_list.push(piece_txt);
    }

    // Put all pieces together to store the complete message
    const text_response = piece_list.join('');

    // Add response to the list of messages as role 'assistant', and its size to tokens_message.
    messages.push({ 'role': 'assistant', 'content': text_response });
    const tokens_response = enc.encode('assistant').length + enc.encode(text_response).length + fixed_per_message
    tokens_message.push(tokens_response);

    // Update max response if needed.
    max_response = Math.max(max_response, tokens_response);
}

// Free encoding object when no longer needed.
enc.free();

rl.close();