import { pipeline } from '@huggingface/transformers';

console.log('Loading model...')

const generator = await pipeline('text-generation', 'elisheldon/Meta-Llama3.2-1B-Instruct-FT', {dtype: 'q4f16', device: 'cpu'});

const messages = [
    { role: "system", content: "You are Eli Sheldon, husband of Chrissie. You are chatting with Chrissie in an online messaging platform. You live in Seattle. You have a 4 year old named Gabe and a 7 month old named Aya and a dog named Gus. Respond as Eli." },
    { role: "user", content: "There is a dog that looks just like Gus" },
]

console.log('Generating output...')

const output = await generator(messages, { max_new_tokens: 128 });
console.log(output[0].generated_text.at(-1).content)