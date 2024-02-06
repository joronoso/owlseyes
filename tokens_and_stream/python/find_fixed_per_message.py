from openai import OpenAI
import tiktoken

# Test messages. Will use to compare token numbers returned by 'usage' with those calculated using tiktoken.
messages = [
    {
        "role": "system",
        "content": "Whatever you receive as input, always respond 'OK'."
    },
    {
        "role": "user",
        "content": "This late pivot means we don't have time to boil the ocean for the client deliverable."
    },
    {
        "role": "assistant",
        "content": "Many of the pets in the game are named after characters from popular culture or individuals."
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
    }]

client = OpenAI()

# Get latest model list, and iterate to calculate the parameter for each.
models = client.models.list()
for model in [m.id for m in models.data]:
    # Only looking for text models. Ignore the rest.
    if model[:4]!='gpt-' or 'vision' in model or 'instruct' in model:
        continue
    
    # Get tiktoken encoding object for the current model.
    encoding = None
    try:
        encoding = tiktoken.encoding_for_model(model)
    except:
        print('Can\'t find encoding for model ' + model)
        continue

    # Send messages to chat completions to get usage.prompt_tokens
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    # Use tiktoken to calculate tokens for each message, for both the text and the role.
    tiktokens = 0
    for message in messages:
        tiktokens += sum([len(encoding.encode(v)) for v in message.values()])
        
    # Using the difference between the usage number and the one from tiktoken, calculate the amount of fixed tokens per message for this model.
    if (response.usage.prompt_tokens - 3 - tiktokens) % len(messages) != 0:
        print('Can\'t find the magic number for '+model)
    else:
        print(model + ' -> Fixed tokens per message: ' + str((response.usage.prompt_tokens - 3 - tiktokens) // len(messages)))

