import OpenAI from 'openai';
import * as readline from 'node:readline/promises'

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Without parameters, the API key will be retrieved for environment variable OPENAI_API_KEY.
// It can also be provided directly using the apiKey parameter, as in the commented line below.
// const client = new OpenAI({ apiKey: 'api-key' });
const client = new OpenAI();
const model = 'gpt-4-1106-preview' // GPT 4-Turbo

// Start with the system role message, which dictates the behavior of the model for the whole interaction.
let messages = [{ 'role': 'system', 'content': 'You\'re an old grumpy and cantankerous person. You respond to everything with complaints and apathy, although you end up helping with what you\'re asked.' }];
let text_user;

// The conversation will continue until we leave an empty message
while (text_user = (await rl.question('What do you want to say to the grumpy chatbot?\n> ')).trim()) {
    // Add the new entry to the list of messages, with role "user".
    messages.push({ 'role': 'user', 'content': text_user });

    // Call chat completions service to get the response from the model. Send the complete list of messages so the conversation context is not lost.
    const response = await client.chat.completions.create({
        model: model,
        messages: messages
    });

    // Display response and add it to the list of messages as role "assistant".
    console.log(response.choices[0].message.content);
    messages.push({ 'role': 'assistant', 'content': response.choices[0].message.content });
}

rl.close();
