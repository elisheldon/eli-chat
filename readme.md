This repo is a learning playground for fine-tuning LLMs (currently Llama 3.2 1B Instruct) and running them locally (currently with Transformers.js v3).

# Development process
1. Downloaded full Google Chat transcript between my wife and me using Google Takeout
2. Processed conversation data and created train.yaml pointing to that data
3. Used torchtune with train.yaml config and full finetune to finetune on my data
`tune run full_finetune_single_device --config train.yaml`
4. Renamed hf_model_0001_2.pt file to pytorch_model.bin so Optimum can find it
5. Used transformer.js v3's convert.py script (after copying in the quantize.py script and removing duplicate enum to avoid an import issue) to quantize into onnx files
`python transformers/scripts/convert.py --model_id "Meta-Llama3.2-1B-Instruct-FT" --task "text-generation"`
6. Used transformer.js v3's quantize.py script for all modes (could also do, for example, `--modes "q4fp16" "int8"`)
`python transformers/scripts/quantize.py --input_folder "models/elisheldon/Meta-Llama3.2-1B-Instruct-FT" --output_folder "models/elisheldon/Meta-Llama3.2-1B-Instruct-FT/onnx"`
7. Published model to https://huggingface.co/elisheldon/Meta-Llama3.2-1B-Instruct-FT which is consumed by this web code

# Next steps
1. Resolve WebGPU issues. Current WebGPU implementation is mostly broken Only the q4fp16 quantized model can be run on WebGPU without a memory error or garbage output (at least on my M2 Pro), but the quality of the response is poor as compared with running the exact same model on WASM.
2. Improve WASM speed. Current WASM implementation runs very slowly, although it does successfully respond with reasonable responses.
3. Improve base model. Llama 3.2 1B Instruct was chosen to avoid 2GB protobuf limits in the onnx stack, but fine-tuning results are much better with fine-tuned Llama 3.2 3B Instruct run as GGUF outside of the browser context.