This repo is a learning playground for fine-tuning LLMs (currently Llama 3.2 1B Instruct) and running them locally (currently with Transformers.js v3).

# Development process
1. Downloaded full Google Chat transcript between my wife and me using Google Takeout
1. Processed conversation data and created train.yaml pointing to that data
2. Used torchtune with train.yaml config and full finetune to finetune on my data
tune run full_finetune_single_device --config train.yaml
3. Renamed hf_model_0001_2.pt file to pytorch_model.bin so Optimum can find it
4. Used transformer.js v3's convert.py script (after copying in the quantize.py script and removing duplicate enum to avoid an import issue) to quantize into onnx files. "-with-past" task variants allow inference with use_cache=True which speeds things up a lot. As of Oct 2024, question-answering is not a currently supported task for llama models (or any other LLMs).
python transformers/scripts/convert.py --model_id "Meta-Llama3.2-1B-Instruct-FT" --task "text-generation-with-past"
5. Used transformer.js v3's quantize.py script for all modes (could also do, for example, `--modes "q4fp16" "int8"`)
python transformers/scripts/quantize.py --input_folder "models/elisheldon/Meta-Llama3.2-1B-Instruct-FT" --output_folder "models/elisheldon/Meta-Llama3.2-1B-Instruct-FT/onnx" --per_channel False --reduce_range False --is_symmetric True --quant_type 1