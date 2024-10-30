import json

def convert_to_sharegpt_format(conversations):
    sharegpt_format = []
    for conversation in conversations:
        dialogue = []
        for message in conversation['messages']:
            if message['role'] == 'user':
                dialogue.append({'from': 'human', 'value': message['content']})
            elif message['role'] == 'assistant':
                dialogue.append({'from': 'gpt', 'value': message['content']})
        sharegpt_format.append({'dialogue': dialogue})
    return sharegpt_format

def main():
    conversations = []
    with open('messages.jsonl', 'r') as f:
        for line in f:
            conversations.append(json.loads(line))

    sharegpt_format = convert_to_sharegpt_format(conversations)

    with open('data.json', 'w') as f:
        json.dump(sharegpt_format, f, indent=4)

if __name__ == '__main__':
    main()