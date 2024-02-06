import OpenAI from 'openai';
import { encoding_for_model } from 'tiktoken';

// Test messages. Will use to compare token numbers returned by 'usage' with those calculated using tiktoken.
const messages = [
    {
        "role": "system",
        "content": "Whatever you receive as input, always respond 'OK'.",
    },
    {
        "role": "user",
        "content": "This late pivot means we don't have time to boil the ocean for the client deliverable.",
    },
    {
        "role": "assistant",
        "content": "Many of the pets in the game are named after characters from popular culture or individuals.",
    },
    {
        "role": "user",
        "content": "The standout aspect of this paper is its quality."
    },
    {
        "role": "assistant",
        "content": "Perfect for Business Orders and for My Dog's Prized Peanut Butter Dog Biscuit Recipe."
    },
    {
        "role": "user",
        "content": "I completely agree."
    }
]
const client = new OpenAI();

// Get latest model list, and iterate to calculate the parameter for each.
const models = await client.models.list();
for (const obj_model of models.data) {
    const model = obj_model.id;

    // Only looking for text models. Ignore the rest.
    if (model.substring(0, 4) !== 'gpt-' || model.includes('vision') || model.includes('instruct')) continue;

    // Get tiktoken encoding object for the current model.
    let encoding;
    try {
        encoding = encoding_for_model(model);
    } catch {
        console.log('Can\'t find encoding for model ' + model);
        continue;
    }

    // Send messages to chat completions to get usage.prompt_tokens
    const response = await client.chat.completions.create({
        model: model,
        messages: messages
    });

    // Use tiktoken to calculate tokens for each message, for both the text and the role.
    let tiktokens = 0;
    for (const message of messages) {
        for (const key in message) {
            tiktokens += encoding.encode(message[key]).length;
        }
    }

    // Using the difference between the usage number and the one from tiktoken, calculate the amount of fixed tokens per message for this model.
    if ((response.usage.prompt_tokens - 3 - tiktokens) % messages.length != 0)
        console.log(`Can't find the magic number for ${model}.`);
    else
        console.log(`${model} -> Fixed tokens per message: ${(response.usage.prompt_tokens - 3 - tiktokens) / messages.length}`);
}
