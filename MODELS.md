# 1min.ai model identifiers

Full list of API model identifiers accepted by `POST /api/chat-with-ai`'s `model` field, as published at
[docs.1min.ai/docs/api/chat-with-ai-api](https://docs.1min.ai/docs/api/chat-with-ai-api). Kept here so the
exact strings are on hand without needing to load that page's dynamic model list again.

> 1min.ai updates this list as new models release - re-check the link above from time to time and update
> this file if identifiers change.


## Alibaba Cloud

- `qwen3.7-plus` - Qwen 3.7 Plus
- `qwen3.7-max` - Qwen 3.7 Max
- `qwen3.7-flash` - Qwen 3.7 Flash
- `qwen3.6-plus` - Qwen 3.6 Plus
- `qwen3.6-max-preview` - Qwen 3.6 Max Preview
- `qwen3.6-flash` - Qwen 3.6 Flash
- `qwen3-vl-plus` - Qwen3 VL Plus
- `qwen3-vl-flash` - Qwen3 VL Flash
- `qwen3-vl-8b-thinking` - Qwen3 VL 8B Thinking
- `qwen3-max` - Qwen3 Max
- `qwen3-8b` - Qwen3 8B
- `qwen-vl-plus` - Qwen VL Plus
- `qwen-vl-max` - Qwen VL Max
- `qwen-plus` - Qwen Plus
- `qwen-max` - Qwen Max
- `qwen-flash` - Qwen Flash

## Anthropic

- `claude-sonnet-5` - Claude 5 Sonnet
- `claude-sonnet-4-6` - Claude 4.6 Sonnet
- `claude-sonnet-4-5-20250929` - Claude 4.5 Sonnet
- `claude-opus-4-8` - Claude 4.8 Opus
- `claude-opus-4-7` - Claude 4.7 Opus
- `claude-opus-4-6` - Claude 4.6 Opus
- `claude-opus-4-5-20251101` - Claude 4.5 Opus
- `claude-haiku-4-5-20251001` - Claude 4.5 Haiku
- `claude-fable-5` - Claude 5 Fable

## Cohere

- `command-r-08-2024` - Command R

## DeepSeek

- `deepseek-reasoner` - DeepSeek V3.2 Reasoner
- `deepseek-chat` - DeepSeek V3.2 Chat

## GoogleAI

- `gemini-3.5-flash` - Gemini 3.5 Flash
- `gemini-3.1-pro-preview` - Gemini 3.1 Pro
- `gemini-3.1-flash-lite-preview` - Gemini 3.1 Flash Lite
- `gemini-3-flash-preview` - Gemini 3 Flash
- `gemini-2.5-pro` - Gemini 2.5 Pro
- `gemini-2.5-flash` - Gemini 2.5 Flash

## MistralAI

- `magistral-small-latest` - Magistral Small 1.2
- `magistral-medium-latest` - Magistral Medium 1.2
- `ministral-14b-latest` - Ministral 14B Latest
- `open-mistral-nemo` - Mistral Open Nemo
- `mistral-small-latest` - Mistral Small
- `mistral-medium-latest` - Mistral Medium 3.1
- `mistral-large-latest` - Mistral Large 2

## OpenAI

- `gpt-5.3-codex` - GPT-5.3 Codex
- `o3-mini` - GPT-o3 Mini
- `gpt-5.6-terra` - GPT-5.6 Terra
- `gpt-5.6-sol` - GPT-5.6 Sol
- `gpt-5.6-luna` - GPT-5.6 Luna
- `gpt-5.5-pro` - GPT-5.5 Pro
- `gpt-5.5` - GPT-5.5
- `gpt-5.4-pro` - GPT-5.4 Pro
- `gpt-5.4-nano` - GPT-5.4 Nano
- `gpt-5.4-mini` - GPT-5.4 Mini
- `gpt-5.4` - GPT-5.4
- `gpt-5.2-pro` - GPT-5.2 Pro
- `gpt-5.2` - GPT-5.2
- `gpt-5.1` - GPT-5.1
- `gpt-5-nano` - GPT-5 Nano
- `gpt-5-mini` - GPT-5 Mini
- `gpt-5` - GPT-5
- `gpt-4o-mini` - GPT-4o Mini **(used as `MODEL_CLASSIFIER`)**
- `gpt-4o` - GPT-4o
- `gpt-4.1-nano` - GPT-4.1 nano
- `gpt-4.1-mini` - GPT-4.1 mini
- `gpt-4.1` - GPT-4.1
- `gpt-4-turbo` - GPT-4 Turbo
- `gpt-3.5-turbo` - GPT-3.5
- `o3-pro` - o3 Pro
- `o3` - o3

## Perplexity

- `sonar-reasoning-pro` - Perplexity [reasoning pro]
- `sonar-pro` - Perplexity [pro]
- `sonar-deep-research` - Perplexity [deep research]
- `sonar` - Perplexity

## xAI

- `grok-4.5` - Grok 4.5 **(used as `MODEL_HARD`)**
- `grok-4.3` - Grok 4.3
- `grok-4-fast-reasoning` - Grok 4 Fast Reasoning **(used as `MODEL_MEDIUM`)**
- `grok-4-fast-non-reasoning` - Grok 4 Fast Non-Reasoning **(used as `MODEL_EASY`)**
- `grok-4-0709` - Grok 4
- `grok-3-mini` - Grok 3 Mini
- `grok-3` - Grok 3

## Z.AI

- `glm-5.2` - GLM-5.2
- `glm-5.1` - GLM-5.1
- `glm-5` - GLM-5

## Extra (Meta / OpenAI OSS)

- `meta/meta-llama-3-70b-instruct` - LLaMA 3 70b
- `meta/llama-4-scout-instruct` - LLaMA 4 Scout Instruct
- `meta/llama-4-maverick-instruct` - LLaMA 4 Maverick Instruct
- `meta/llama-2-70b-chat` - LLaMA 2 70b
- `openai/gpt-oss-20b` - GPT OSS 20b
- `openai/gpt-oss-120b` - GPT OSS 120b

## Why these four were picked for this project

Users tend to want fast, snappy answers over long "thinking" delays, so easy/medium tiers favor speed - and
xAI's Grok models tend to read a bit more conversational/human than other providers' equivalents, which is a
nice fit for a chat bot.

| Tier | Model | Reasoning |
|---|---|---|
| `MODEL_CLASSIFIER` | `gpt-4o-mini` | Cheap, fast, only needs to output one word (easy/medium/hard) - doesn't need to sound human, so provider doesn't matter here |
| `MODEL_EASY` | `grok-4-fast-non-reasoning` | xAI's fastest model, no reasoning step, for quick/simple questions |
| `MODEL_MEDIUM` | `grok-4-fast-reasoning` | Same speed tier but with a light reasoning pass - middle ground between instant replies and the flagship |
| `MODEL_HARD` | `grok-4.5` | xAI's flagship, full reasoning, for questions that actually need it |

Source of truth for prices/context windows: check the 1min.ai dashboard directly, since it can change
independently of this file.