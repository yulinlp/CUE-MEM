<div align="center">

# CUE-Mem
### Benchmarking Long-Term User Memory via Implicit Cues in Multimodal Conversations

[**Online Demo**](https://reichenbach1854-hash.github.io/CUE-Mem/) · [**Dataset**](https://huggingface.co/datasets/Kkryptonite/CUE-Mem) · [**Getting Started**](#getting-started) · [**中文运行指南**](guides/usage_zh.md)

Yulin Hu, **Yanyan Zhao***, Zimo Long, Xing Fu, Mengtong Ji, Weixiang Zhao, Yutai Hou, Qianchao Wang, Dandan Tu

Harbin Institute of Technology · Huawei Technologies Co., Ltd.<br>
*Corresponding author: Yanyan Zhao*

</div>

**Can a conversational agent remember what a user never explicitly says?**

A pet bowl in the background of a photograph, repeated cycling equipment, or ambient sounds in a voice message can reveal information that matters for future interactions. CUE-Mem evaluates whether memory systems retain, retrieve, and use these subtle cues across long-term multimodal conversations.

The benchmark contains **2,674 questions** spanning **text, images, and audio**, with explicit and implicit evidence settings across four tasks:

| Task | What it tests |
|---|---|
| **Entity Recall** | Remembering user-related entities and their attributes |
| **Long Pattern** | Inferring persistent preferences and habits across interactions |
| **Personalized Recommendation** | Applying remembered information to a new recommendation |
| **Answer Refusal** | Abstaining when the history does not support an answer |

<p align="center"><img src="assets/benchmark.png" alt="CUE-Mem benchmark construction and evaluation overview" width="100%"></p>

## Resources

- **[Online demo](https://reichenbach1854-hash.github.io/CUE-Mem/):** explore the construction pipeline, image/audio examples, QA tasks, and experimental findings in your browser.
- **[Hugging Face dataset](https://huggingface.co/datasets/Kkryptonite/CUE-Mem):** download the full benchmark separately from the code.
- **This repository:** data-construction scripts, RQ1/RQ2 memory evaluation, RQ3 multimodal retrieval and answering, and a human-evaluation interface.
- **Paper:** the arXiv link will be added when the preprint is available.

The `docs/` directory includes the selected media needed by the static demo. Full experiment data, model weights, embedding indices, and generated results are external to this repository.

## Getting started

### 1. Browse the demo

The [hosted demo](https://reichenbach1854-hash.github.io/CUE-Mem/) needs no installation. To serve the included copy locally:

```bash
git clone https://github.com/yulinlp/CUE-MEM.git
cd CUE-MEM
python -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Open **http://127.0.0.1:8000**. This route uses Python's standard library and needs no API keys or model downloads. Use an HTTP server rather than opening `index.html` directly, because the application fetches JSON files.

### 2. Install experiment dependencies

Use Python **3.10 or later**, and run commands from the repository root.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-eval.txt
python -m pip install torch
```

The final command installs the default PyTorch build. For GPU experiments, choose the PyTorch build appropriate to your CUDA environment. ImageBind, local model serving, TTS, and individual memory backends require their own packages and weights; the basic installation does not install all research backends. The smaller `requirements-public.txt` covers the shared construction utilities.

### 3. Download and prepare the dataset

```bash
python -m pip install huggingface_hub
hf download Kkryptonite/CUE-Mem --repo-type dataset --local-dir benchmark-data

python -m scripts.prepare_dataset \
  --dataset-root benchmark-data \
  --output-root workdir/benchmark
```

The preparation command copies dialogue/QA JSONs into the runners' expected layout and resolves published media paths to absolute local paths. It preserves questions, answers, annotations, and the original download. Media files are not duplicated. Keep `benchmark-data/` at the same location after preparation; use a new output directory if you prepare another copy.

Check `workdir/benchmark/dataset_preparation.json`: missing media are listed explicitly. A successful JSON preparation does not mean every media file has been downloaded. Complete those files before multimodal experiments.

### 4. Configure your model service

```bash
cp .env.example .env
# Edit .env with the endpoint and credentials for your selected services.
set -a
source .env
set +a

export CUE_MEM_BENCHMARK_ROOT="$PWD/workdir/benchmark"
```

`.env` is not loaded automatically. Configure `CUE_MEM_LLM_API_KEY` and `CUE_MEM_LLM_BASE_URL` for the RQ1/RQ2 OpenAI-compatible service. The runner accepts the model names listed by `--help`; the endpoint must serve the selected model. RQ3 additionally uses `RQ3_OMNI_*` and the selected embedding-provider settings. See [`.env.example`](.env.example) for the full list.

## Experiments

### RQ1: Memory from explicit and implicit evidence

Start with one profile and a small QA sample. This command makes real model-service requests once configured:

```bash
python -m scripts.RQ1_RQ2.benchmark.run.run_bench \
  --llm_name qwen3.6-35b-a3b \
  --memory_name FUMemory \
  --data_name history_with_qa_p0 \
  --caption_category base \
  --sample 1 \
  --save_results
```

`--sample` limits QA items per category; it does not necessarily limit the history ingested by a memory backend. With `--caption_category base`, `--data_name` is relative to `data/dialog/base/` and omits `.json`. The example model must be available on your configured endpoint; it is not downloaded by this command.

Question-only and oracle-evidence baselines have separate entry points:

```bash
python -m scripts.RQ1_RQ2.benchmark.run.run_bench_question_only --help
python -m scripts.RQ1_RQ2.benchmark.run.run_bench_oracle_evidence --help
```

### RQ2: What is preserved by textualization?

RQ2 varies image-caption detail and audio representations before memory evaluation. Caption variants must first be generated or supplied; the base dataset alone does not contain every intervention.

```bash
python -m scripts.RQ1_RQ2.benchmark.run.run_bench --help
python -m scripts.qa.build_bench_input --help
python -m scripts.qa.build_audio_caption_study_inputs --help
```

Use the runner's `--caption_category` and `--audio_caption` options for prepared variants. Summarize existing results with:

```bash
python -m scripts.RQ1_RQ2.benchmark.run.aggregate_results \
  --mode overall \
  --result-dir "$CUE_MEM_BENCHMARK_ROOT/result_debug/base"
```

The [detailed guide](guides/usage_zh.md#7-rq1rq2-benchmark) covers caption/audio comparisons, memory backends, and Slurm wrappers. Aggregation reads existing results; it does not reproduce model inference.

### RQ3: Multimodal indexing versus multimodal evidence use

RQ3 separates the retrieval index from the evidence supplied to the answering model:

| Variant | Index | Evidence use |
|---|---|---|
| `TT` | Text | Text |
| `TM` | Text | Multimodal |
| `MT` | Multimodal | Text |
| `MM` | Multimodal | Multimodal |

Point RQ3 to the prepared histories and the downloaded media:

```bash
export RQ3_HISTORY_DIR="$PWD/workdir/benchmark/data/dialog/base"
export RQ3_DATA_DIR="$PWD/benchmark-data"
export CUE_MEM_RQ3_ROOT="$PWD/workdir/RQ3"
```

After installing ImageBind and its checkpoint, generate the indices needed for the selected variants:

```bash
python -m scripts.RQ3.step1_encode_embeddings \
  --embedding-provider imagebind \
  --profiles 0 \
  --modes text unified_multimodal \
  --skip-existing

python -m scripts.RQ3.step2_run_experiment \
  --variants TT TM MT MM \
  --profiles 0 \
  --sample 10 \
  --max-workers 1

python -m scripts.RQ3.step3_evaluate \
  --result-root workdir/RQ3/results
```

The experiment stage requires an Omni answering service configured through `RQ3_OMNI_*`. A Gemini-compatible embedding backend is also supported; see the [detailed guide](guides/usage_zh.md#8-rq3-实验). Changing the model or embedding backend changes the experimental setting.

## Data construction and human evaluation

Construction scripts follow **profiles → events and conversations → QA → benchmark inputs**. You do not need to regenerate the benchmark to evaluate on its published data.

| Directory | Contents |
|---|---|
| `scripts/profile/` | Profiles, entity anchors, portraits, and voice design |
| `scripts/event/` | Event plans, conversations, images, and audio |
| `scripts/qa/` | Question construction, checks, and input conversion |
| `scripts/RQ1_RQ2/` | Textualized memory methods, baselines, and aggregation |
| `scripts/RQ3/` | Embedding, retrieval, Omni answering, and evaluation |
| `scripts/human_baseline_demo/` | Interactive annotation interface |
| `scripts/common/` | Shared configuration, paths, and I/O |
| `docs/` | Static website and selected demo media |

To collect human answers using a prepared profile:

```bash
python -m scripts.human_baseline_demo \
  --data workdir/benchmark/data/dialog/base/history_with_qa_p0.json \
  --media-root benchmark-data \
  --output-dir workdir/human-results \
  --host 127.0.0.1 --port 8765
```

Open http://127.0.0.1:8765. This is a separate application from the static project website and writes participant submissions to the specified output directory.

See [release validation](guides/validation.md) for the checks performed and their scope.

## Citation

```bibtex
@misc{hu2026cuemem,
  title = {CUE-Mem: Benchmarking Long-Term User Memory via Implicit Cues in Multimodal Conversations},
  author = {Hu, Yulin and Zhao, Yanyan and Long, Zimo and Fu, Xing and Ji, Mengtong and Zhao, Weixiang and Hou, Yutai and Wang, Qianchao and Tu, Dandan},
  year = {2026},
  url = {https://github.com/yulinlp/CUE-MEM}
}
```

The citation will be updated with the arXiv identifier once available.

## Acknowledgments and reuse

This release builds on the [collaborator-maintained CUE-Mem repository](https://github.com/reichenbach1854-hash/CUE-Mem); its Git history is retained. The online demo remains hosted by that collaborator. Thanks to the authors of the memory systems and model backends used in the experiments.

The imported code repository does not include a standalone code license. Dataset terms are provided with the [dataset release](https://huggingface.co/datasets/Kkryptonite/CUE-Mem). No new code license is assigned by this cleanup; upstream dependencies retain their own terms.
