# CUE-Mem 详细运行说明

返回 [项目首页](../README.md)。完整数据见 [Hugging Face](https://huggingface.co/datasets/Kkryptonite/CUE-Mem)，仓库中的 `docs/` 已包含精选 Demo 媒体。下文“数据不随仓库提供”指完整实验数据。


`CUE-Mem-public` 是 CUE-Mem 实验代码的公开、代码优先版本，面向希望复现实验流程、替换自己的数据或接入自己的模型服务的使用者。

仓库只提供整理后的脚本、共用工具和少量 prompt 模板，不提供实验数据、个人媒体、模型权重、embedding、缓存或实验结果。运行完整流程前，需要准备自己的数据和相应的模型/服务依赖。

## 1. 仓库结构

```text
scripts/
├── common/                 JSON、路径和 LLM 配置共用函数
├── profile/                profile 构建、实体锚点、肖像和音频相关脚本
├── event/                  分组、事件、对话、图片和音频相关脚本
├── qa/                     QA 生成、转换、检查和 benchmark 输入构建
├── RQ1_RQ2/                RQ1/RQ2 benchmark、记忆方法和评测脚本
├── RQ3/                    embedding、检索、Omni QA 实验和结果评测
└── human_baseline_demo/    人工基线浏览和答题页面
```

推荐把流程理解为：

```text
profile → event → qa → RQ1_RQ2 / RQ3 → human_baseline_demo
```

各阶段也可以单独使用，只要准备了对应格式的输入文件。

## 2. 安装

建议使用 Python 3.10 或更高版本，并从仓库根目录执行命令。

```bash
git clone https://github.com/yulinlp/CUE-MEM.git CUE-Mem-public
cd CUE-Mem-public

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-public.txt
```

`requirements-public.txt` 只覆盖通用依赖。RQ1/RQ2 的部分记忆后端、RQ3 的 GPU embedding、ImageBind、绘图、TTS 和云端服务依赖需要按实际使用的脚本另行安装；模型权重也需要用户自行准备。

先确认代码包可以被找到：

```bash
python -m scripts.RQ1_RQ2.benchmark.run.run_bench --help
python -m scripts.RQ3.step1_encode_embeddings --help
python -m scripts.human_baseline_demo --help
```

这些 `--help` 命令不会调用真实 API，也不会运行实验。

## 3. 配置路径和服务

### 3.1 配置环境变量

仓库提供了变量模板：

```bash
cp .env.example .env
```

`.env` 不会被 Python 自动加载。可以在当前 shell 中显式导出：

```bash
set -a
source .env
set +a
```

也可以只导出当前任务所需的变量，例如：

```bash
export CUE_MEM_PROJECT_ROOT="$(pwd)"
export CUE_MEM_LLM_API_KEY="your-key"
export CUE_MEM_LLM_BASE_URL="your-openai-compatible-endpoint"
export CUE_MEM_LLM_MODEL="your-model"
```

不要把真实密钥写入 README、脚本、命令提交记录或 Git 仓库。优先使用环境变量，不要在命令行中直接传 `--api-key`，以免密钥进入 shell history。`.env` 已被 `.gitignore` 排除，但提交前仍应检查 Git 状态。

### 3.2 路径约定

默认路径相对于项目根目录解析。通常需要准备如下外部目录：

```text
<project-root>/
├── profile/                  profile 输入和生成文件
├── event/                    event 输入和生成文件
├── qa/                       QA 输入和生成文件
├── RQ1_RQ2/benchmark/        RQ1/RQ2 数据、结果和缓存
│   ├── data/
│   ├── result_*/
│   └── ...
├── RQ3/                      RQ3 数据、embedding 和结果
│   ├── data/
│   │   ├── history_dialogue/
│   │   ├── event_image/
│   │   ├── voice_mixed_000_002/
│   │   └── qa_image/
│   ├── embeddings/
│   ├── prompts/
│   └── results/
└── human_baseline_demo/results/
```

数据和结果不随仓库提供，也不应直接提交到公开仓库。若 benchmark 数据不在项目根目录的默认位置，可以显式指定：

```bash
export CUE_MEM_PROJECT_ROOT="/path/to/your/checkout"
export CUE_MEM_BENCHMARK_ROOT="/path/to/your/benchmark"
```

RQ1/RQ2 和人工基线会优先查找顶层 `RQ1_RQ2/benchmark`，并兼容旧目录名 `Mem-Gallery-main/benchmark`。显式设置 `CUE_MEM_BENCHMARK_ROOT` 后，以该变量为准。RQ3 的根目录由 `CUE_MEM_RQ3_ROOT` 指定，默认是项目根目录下的 `RQ3/`。

### 3.3 服务变量概览

完整变量列表和空值模板见 [`.env.example`](../.env.example)。常用变量如下：

| 用途 | 主要变量 |
| --- | --- |
| 通用 OpenAI-compatible LLM | `CUE_MEM_LLM_API_KEY`、`CUE_MEM_LLM_BASE_URL`、`CUE_MEM_LLM_MODEL` |
| QA 图片/音频服务 | `CUE_MEM_QA_IMAGE_*`、`CUE_MEM_QA_AUDIO_*` |
| RQ1/RQ2 vLLM | `CUE_MEM_VLLM_MODEL_PATH`、`CUE_MEM_VLLM_HEALTH_URL`、`CUE_MEM_VLLM_BASE_URL`、`CUE_MEM_VLLM_API_KEY` |
| RQ1/RQ2 外部记忆后端 | `AMEM_API_KEY`、`AMEM_API_BASE`、`MEMORYOS_API_KEY`、`MEMORYOS_API_BASE` |
| RQ3 Omni 服务 | `RQ3_OMNI_API_BASE`、`RQ3_OMNI_API_KEY`、`RQ3_OMNI_MODEL` |
| RQ3 Gemini embedding | `RQ3_GEMINI_EMBEDDING_API_BASE`、`RQ3_GEMINI_EMBEDDING_API_KEY`、`RQ3_GEMINI_EMBEDDING_MODEL` |

变量为空时，很多脚本只能执行 `--help`、纯本地处理或结果汇总；真正调用模型前必须完成对应配置。

## 4. profile 流程

profile 脚本处理人物档案、实体锚点以及可选的肖像和音频素材。输入通常是 JSON/JSONL 文件，具体字段以脚本的数据格式为准。

先查看参数：

```bash
python -m scripts.profile.build_profile_artifacts --help
python -m scripts.profile.gen_entity_anchors --help
python -m scripts.profile.gen_nano_banana_portraits --help
python -m scripts.profile.gen_voice_design --help
python -m scripts.profile.gen_voice_message --help
```

构建 profile 派生文件的示例：

```bash
python -m scripts.profile.build_profile_artifacts \
  --profiles profile/profiles_with_anchors.jsonl \
  --events event/events_with_anchors.jsonl \
  --output profile/profiles_with_items.jsonl
```

`build_profile_artifacts.py` 会集中完成原来多个派生步骤，并默认写入新的输出文件，不覆盖输入文件。实体锚点生成会调用 LLM，建议先用小样本调试：

```bash
python -m scripts.profile.gen_entity_anchors \
  --input profile/profiles_implicit_first.jsonl \
  --output profile/profiles_with_anchors.jsonl \
  --sample 1 \
  --workers 1
```

肖像、音色和语音消息脚本需要额外的图像/TTS/GPU 依赖，并会生成较大的本地文件；运行前先阅读对应的 `--help`。

## 5. event 流程

event 脚本负责从 profile 生成事件分组、修改事件、对话以及可选的图片和音频资产。

```bash
python -m scripts.event.generate_groups_via_llm --help
python -m scripts.event.gen_event_modified --help
python -m scripts.event.gen_dialog --help
python -m scripts.event.gen_formatted_data --help
python -m scripts.event.attach_assets_to_dialogue --help
```

第一次使用 LLM 分组时可以只打印 prompt，不发起请求：

```bash
python -m scripts.event.generate_groups_via_llm \
  --input profile/profiles_with_anchors.jsonl \
  --dry_run
```

确认输入和配置后，再指定输出路径运行真实任务。事件图片、Kling 音频、语音混合等脚本都支持命令行路径覆盖；运行这些脚本前需要配置相应的服务变量，并注意生成文件的磁盘空间。

## 6. QA 流程

QA 目录包含实体、偏好、推荐、拒答等 QA 生成脚本，以及转换、检查和 benchmark 输入构建工具。常用入口：

```bash
python -m scripts.qa.gen_qa_entity --help
python -m scripts.qa.gen_qa_preference --help
python -m scripts.qa.gen_qa_recommendation --help
python -m scripts.qa.gen_qa_adversarial_llm --help
python -m scripts.qa.convert --help
python -m scripts.qa.build_bench_input --help
```

推荐顺序是先阅读 `--help`，为输入和输出显式指定路径，再从 `--sample` 或单个 profile 开始。QA 生成和媒体描述可能调用多个外部服务，所需变量见 `.env.example`。

`convert.py` 通过 `--mode single` 处理单个输入文件，或通过 `--mode category` 批量转换 caption category 数据；`build_bench_input.py` 通过 `--mode base`、`--mode category` 和 `--mode audio-caption` 分别构建普通、category 和 audio-caption benchmark 输入。

音频 caption 研究数据准备使用以下两个入口：

```bash
python -m scripts.qa.generate_background_audio_captions --help
python -m scripts.qa.build_audio_caption_study_inputs --help
```

其中 `generate_background_audio_captions.py` 负责生成背景音描述缓存，实际调用服务时才需要通过环境变量或命令行参数提供 API 配置；`build_audio_caption_study_inputs.py` 根据 `asr`、`hint` 和 `asr_bg_split` 模式构造对应的 benchmark 输入。

本公开版本按要求不包含 `scripts/qa/view`，也没有提供生成 HTML 页面查看图片的脚本。

## 7. RQ1/RQ2 benchmark

RQ1/RQ2 代码位于 `scripts/RQ1_RQ2/`，其中 `benchmark/` 下保留记忆方法、评测逻辑、prompt 和运行脚本；数据、模型、结果和缓存需要单独准备。

先设置 benchmark 根目录并查看入口参数：

```bash
export CUE_MEM_BENCHMARK_ROOT="/path/to/RQ1_RQ2/benchmark"

python -m scripts.RQ1_RQ2.benchmark.run.run_bench --help
python -m scripts.RQ1_RQ2.benchmark.run.run_bench_question_only --help
python -m scripts.RQ1_RQ2.benchmark.run.run_bench_oracle_evidence --help
```

小样本运行示例（仍会调用模型，请先完成 API/模型配置）：

```bash
python -m scripts.RQ1_RQ2.benchmark.run.run_bench \
  --llm_name qwen3.6-35b-a3b \
  --memory_name FUMemory \
  --all_datasets \
  --sample 1 \
  --save_results
```

只运行 question-only 基线：

```bash
python -m scripts.RQ1_RQ2.benchmark.run.run_bench_question_only \
  --llm_name qwen3.6-35b-a3b \
  --all_datasets \
  --sample 1 \
  --save_results
```

question-only 多次运行完成后，可以用统一入口生成逐题交叉比较结果，或继续分析 retention 集合：

```bash
python -m scripts.RQ1_RQ2.benchmark.run.cross_compare_question_only \
  --mode cross-compare \
  --result_dir "$CUE_MEM_BENCHMARK_ROOT/result_question_only/base"

python -m scripts.RQ1_RQ2.benchmark.run.cross_compare_question_only \
  --mode retention \
  --cross_compare_dir "$CUE_MEM_BENCHMARK_ROOT/result_question_only/base/cross_compare"
```

### 7.1 统一结果统计入口

RQ1/RQ2 的五类 JSON 统计任务已经合并到一个脚本中，通过 `--mode` 选择统计类型：

```bash
# 普通 benchmark 汇总
python -m scripts.RQ1_RQ2.benchmark.run.aggregate_results \
  --mode overall \
  --result-dir "$CUE_MEM_BENCHMARK_ROOT/result_debug_trimmed/base"

# question-only：准确率、A/B/C/D 作答分布和选项偏置检验
python -m scripts.RQ1_RQ2.benchmark.run.aggregate_results \
  --mode question-only \
  --result-dir "$CUE_MEM_BENCHMARK_ROOT/result_question_only/base"

# question-only adversarial 结果
python -m scripts.RQ1_RQ2.benchmark.run.aggregate_results \
  --mode adversarial \
  --result-dir "$CUE_MEM_BENCHMARK_ROOT/result_question_only/base/qwen3.6-35b-a3b/final"

# 比较 brief / medium / detailed caption
python -m scripts.RQ1_RQ2.benchmark.run.aggregate_results \
  --mode caption \
  --result-dir "$CUE_MEM_BENCHMARK_ROOT/result_debug" \
  --captions brief,medium,detailed

# 比较 audio-caption 模型
python -m scripts.RQ1_RQ2.benchmark.run.aggregate_results \
  --mode audio-caption \
  --result-dir "$CUE_MEM_BENCHMARK_ROOT/result_debug" \
  --audio-models qwen3_asr_1.7b,qwen_audio,qwen2_audio_7b,moss_audio_8b,gemini-3.1-pro,voice_bgm_split
```

常用选项包括 `--category pref_text`、`--model <模型名>`、`--per-category` 和 `--output <JSON路径>`；完整参数请运行 `--help`。横向比较模式默认展示所有可找到的 QA category filter，caption 模式如需加入无 caption 基线，可在 `--captions` 中追加 `base`。统计脚本只读取已有结果，不会调用模型服务；生成的汇总 JSON 会写入结果目录，通常由 `.gitignore` 排除。

如果使用 Slurm 和本地 vLLM，公开版本仅保留一个基础包装脚本：

```bash
bash scripts/RQ1_RQ2/benchmark/run_bench_base.sh
```

该脚本不是通用的本地单机启动器；提交前需要准备 Slurm 环境、模型权重，并设置 `CUE_MEM_VLLM_MODEL_PATH`、`CUE_MEM_VLLM_HEALTH_URL`、端口和相关 API 变量。也可以跳过包装脚本，直接运行上面的 Python 入口。

实验生成的 `result_*`、日志、缓存和运行时 JSON/CSV 文件会被 `.gitignore` 忽略。部分记忆后端依赖外部项目或额外 Python 包，公开仓库没有将它们复制进来。

## 8. RQ3 实验

RQ3 的主流程分为 embedding、实验、评测和可视化四步。默认读取顶层 `RQ3/`，也可以通过 `CUE_MEM_RQ3_ROOT`、各个 `RQ3_*_DIR` 变量或命令行参数覆盖。

### 8.1 生成 embedding

ImageBind 需要外部 ImageBind 安装和 checkpoint：

```bash
python -m scripts.RQ3.step1_encode_embeddings \
  --embedding-provider imagebind \
  --profiles 0 \
  --modes unified_multimodal \
  --sample 10 \
  --skip-existing
```

如果使用兼容 Gemini embedding API：

```bash
export RQ3_EMBEDDING_PROVIDER=gemini
export RQ3_GEMINI_EMBEDDING_API_BASE="your-embedding-endpoint"
export RQ3_GEMINI_EMBEDDING_API_KEY="your-key"

python -m scripts.RQ3.step1_encode_embeddings \
  --embedding-provider gemini \
  --profiles 0 \
  --modes text \
  --sample 10 \
  --skip-existing
```

### 8.2 运行主实验

embedding 准备好后，可以先只跑一个 profile 和少量 QA：

```bash
python -m scripts.RQ3.step2_run_experiment \
  --variants TT \
  --profiles 0 \
  --sample 10 \
  --max-workers 1
```

完整实验可将 `--variants` 改为 `TT TM MT MM`，并根据机器资源调整 `--profiles`、`--max-workers` 和 `--checkpoint-every`。主实验需要 embedding 数据以及 Omni 评测服务；服务配置通过 `RQ3_OMNI_*` 或兼容的 `CUE_MEM_LLM_*` 变量提供。

### 8.3 汇总和可视化

```bash
python -m scripts.RQ3.step3_evaluate \
  --result-root RQ3/results

python -m scripts.RQ3.step4_visualize \
  --metrics-file RQ3/results/summary/full_metrics.json \
  --output-dir RQ3/results/plots
```

`step3_evaluate.py` 只读取已有结果，不需要重新调用 LLM；`step4_visualize.py` 会生成图表和可选报告，这些产物应保留在本地结果目录，不提交到公开仓库。

RQ3 还提供 `run_bench_oracle_evidence.py` 以及若干数据/结果修补脚本。它们主要用于已有实验数据的特殊复现，运行前请先使用 `--help` 确认输入文件和 `--apply` 等写入选项。

## 9. human baseline demo

人工基线页面默认寻找：

```text
RQ1_RQ2/benchmark/data/dialog/base/history_with_qa_p0.json
```

也可以显式指定数据、媒体根目录和提交结果目录：

```bash
python -m scripts.human_baseline_demo \
  --data RQ1_RQ2/benchmark/data/dialog/base/history_with_qa_p0.json \
  --media-root . \
  --output-dir human_baseline_demo/results \
  --host 127.0.0.1 \
  --port 8765
```

浏览器打开 `http://127.0.0.1:8765/`。若要查看其他 profile，可以使用例如 `http://127.0.0.1:8765/?profile=p1`。提交结果会写入 `--output-dir`，该目录默认被忽略，不会进入 Git。

该 demo 只提供人工阅读、选择答案和准确率计算，不调用 LLM；但页面展示的图片和音频仍需要数据文件及正确的媒体路径。

## 10. 常见问题

### 找不到数据文件

确认命令是在仓库根目录执行，并检查 `CUE_MEM_PROJECT_ROOT`、`CUE_MEM_BENCHMARK_ROOT` 或相应的 `--data-dir`/`--data` 参数。仓库仅包含 Demo 样例，不包含完整实验数据；请按项目首页下载并准备数据。

### 提示缺少 API key 或 endpoint

`.env.example` 只是模板，不会自动生效。执行 `source .env` 或在当前 shell 中 `export` 对应变量。不同模块可能使用不同的变量名前缀，优先查看本 README 和模板中的模块专用变量。

### `ModuleNotFoundError`

先安装 `requirements-public.txt`。如果错误来自 ImageBind、torch、TTS、特定记忆后端或绘图库，需要按照所选流程安装对应的可选依赖和模型，不要把这些大型依赖或权重复制进公开仓库。

### 想先确认命令是否正确

先运行入口的 `--help`，再使用 `--sample 1`、`--profiles 0` 或 event/QA 脚本提供的 `--dry_run`。任何真实 API 调用前，都应先确认输出目录和费用/并发设置。

## 11. 开发和自检

从仓库根目录可以执行基础静态检查：

```bash
ruff check --no-cache --select E9,F63,F7,F82 scripts

while IFS= read -r file; do
  bash -n "$file"
done < <(find scripts/RQ1_RQ2 -name '*.sh' -type f)
```

完整实验依赖外部数据、模型和服务，不能仅凭静态检查证明实验结果可复现。运行过程中生成的媒体、结果、缓存和日志请保存在本地或外部存储中。
