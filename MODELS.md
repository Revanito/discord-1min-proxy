# 1min.ai model identifiers

Full list of API model identifiers accepted by `POST /api/chat-with-ai`'s `model` field (type
`UNIFY_CHAT_WITH_AI`), as listed at
[docs.1min.ai/docs/api/chat-with-ai-api](https://docs.1min.ai/docs/api/chat-with-ai-api). That page renders
the list client-side from a public JSON endpoint (no API key needed), which is the real source of truth:

```
https://api.1min.ai/models?feature=UNIFY_CHAT_WITH_AI
```

> Last synced: 2026-10-06. 1min.ai renames and removes models without notice
> (e.g. in 2026 every Claude ID moved to AWS Bedrock-style `us.anthropic.*` IDs and the `grok-4-fast-*`
> models were dropped). `scripts/check_models.py` checks the models this repo uses (and its sibling repos)
> against that endpoint every month. See the README.


## Alibaba Cloud

- `qwen3.7-plus` - Qwen 3.7 Plus
- `qwen3.7-max` - Qwen 3.7 Max
- `qwen3.7-flash` - Qwen 3.7 Flash
- `qwen3.6-plus` - Qwen 3.6 Plus
- `qwen3.6-max-preview` - Qwen 3.6 Max Preview
- `qwen3.6-flash` - Qwen 3.6 Flash
- `qwen3-vl-plus` - Qwen3 VL Plus _(deprecated on 2026-10-09)_
- `qwen3-vl-flash` - Qwen3 VL Flash
- `qwen3-vl-8b-thinking` - Qwen3 VL 8B Thinking
- `qwen3-max` - Qwen3 Max
- `qwen3-8b` - Qwen3 8B
- `qwen-vl-plus` - Qwen VL Plus
- `qwen-vl-max` - Qwen VL Max
- `qwen-plus` - Qwen Plus
- `qwen-max` - Qwen Max
- `qwen-flash` - Qwen Flash

## Anthropic (via AWS Bedrock)

- `us.anthropic.claude-sonnet-5` - Claude 5 Sonnet
- `us.anthropic.claude-sonnet-4-6` - Claude 4.6 Sonnet
- `us.anthropic.claude-sonnet-4-5-20250929-v1:0` - Claude 4.5 Sonnet
- `us.anthropic.claude-opus-5-5` - Claude 5.5 Opus
- `us.anthropic.claude-opus-5` - Claude 5 Opus
- `us.anthropic.claude-opus-4-8` - Claude 4.8 Opus
- `us.anthropic.claude-opus-4-7` - Claude 4.7 Opus
- `us.anthropic.claude-opus-4-6-v1` - Claude 4.6 Opus
- `us.anthropic.claude-opus-4-5-20251101-v1:0` - Claude 4.5 Opus
- `us.anthropic.claude-haiku-4-5-20251001-v1:0` - Claude 4.5 Haiku
- `us.anthropic.claude-fable-5-1` - Claude 5.1 Fable
- `us.anthropic.claude-fable-5` - Claude 5 Fable

## Cohere

- `command-r-08-2024` - Command R

## DeepSeek

- `deepseek-v4-pro` - DeepSeek V4 Pro
- `deepseek-flash` - DeepSeek V4.1 Flash

## GoogleAI

- `gemini-3.8-flash` - Gemini 3.8 Flash
- `gemini-3.7-flash` - Gemini 3.7 Flash
- `gemini-3.6-flash` - Gemini 3.6 Flash
- `gemini-3.5-flash` - Gemini 3.5 Flash
- `gemini-3.1-pro-preview` - Gemini 3.1 Pro
- `gemini-3.1-flash-lite-preview` - Gemini 3.1 Flash Lite
- `gemini-3-flash-preview` - Gemini 3 Flash
- `gemini-2.5-pro` - Gemini 2.5 Pro _(deprecated on 2026-10-09)_
- `gemini-2.5-flash` - Gemini 2.5 Flash _(deprecated on 2026-10-09)_

## MistralAI

- `magistral-small-latest` - Magistral Small 1.2
- `magistral-medium-latest` - Magistral Medium 1.2
- `ministral-14b-latest` - Ministral 14B Latest
- `open-mistral-nemo` - Mistral Open Nemo
- `mistral-small-latest` - Mistral Small
- `mistral-small-2603` - Mistral Small 4
- `mistral-medium-latest` - Mistral Medium 3.1
- `mistral-medium-3-5` - Mistral Medium 3.5
- `mistral-large-latest` - Mistral Large 2
- `mistral-large-2512` - Mistral Large 3

## OpenAI

- `gpt-5.3-codex` - GPT-5.3 Codex
- `o3-mini` - GPT-o3 Mini _(deprecated on 2026-10-21)_
- `gpt-6.1-sol` - GPT-6.1 Sol
- `gpt-6-sol` - GPT-6 Sol
- `gpt-6-luna` - GPT-6 Luna
- `gpt-6-astra` - GPT-6 Astra
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
- `gpt-5-nano` - GPT-5 Nano _(deprecated on 2026-12-09)_
- `gpt-5-mini` - GPT-5 Mini _(deprecated on 2026-12-09)_
- `gpt-5` - GPT-5 _(deprecated on 2026-12-09)_
- `gpt-4o-mini` - GPT-4o Mini
- `gpt-4o` - GPT-4o
- `gpt-4.1-nano` - GPT-4.1 nano _(deprecated on 2026-10-21)_
- `gpt-4.1-mini` - GPT-4.1 mini
- `gpt-4.1` - GPT-4.1
- `gpt-4-turbo` - GPT-4 Turbo _(deprecated on 2026-10-21)_
- `gpt-3.5-turbo` - GPT-3.5 _(deprecated on 2026-10-21)_
- `o3-pro` - o3 Pro _(deprecated on 2026-12-09)_
- `o3` - o3 _(deprecated on 2026-12-09)_

## Perplexity

- `sonar-reasoning-pro` - Perplexity [reasoning pro]
- `sonar-pro` - Perplexity [pro]
- `sonar-deep-research` - Perplexity [deep research]
- `sonar` - Perplexity

## xAI

- `grok-4.7` - xAI
- `grok-4.6` - xAI
- `grok-4.5` - xAI
- `grok-4.3` - xAI

## Z.AI

- `glm-5.3` - GLM-5.3
- `glm-5.2` - GLM-5.2
- `glm-5.1` - GLM-5.1
- `glm-5` - GLM-5

## Extra (OpenRouter: Kimi / Muse)

- `moonshotai/kimi-k3` - Kimi K3
- `moonshotai/kimi-k2.7-code` - Kimi K2.7 Code
- `moonshotai/kimi-k2.6` - Kimi K2.6
- `meta/muse-spark-1.3` - Muse Spark 1.3
- `meta/muse-spark-1.2` - Muse Spark 1.2
- `meta/muse-spark-1.1` - Muse Spark 1.1

## Extra (Meta / OpenAI OSS)

- `meta/meta-llama-3-70b-instruct` - LLaMA 3 70b
- `meta/llama-4-scout-instruct` - LLaMA 4 Scout Instruct
- `meta/llama-4-maverick-instruct` - LLaMA 4 Maverick Instruct
- `openai/gpt-oss-20b` - GPT OSS 20b
- `openai/gpt-oss-120b` - GPT OSS 120b

## Why these models were picked for this project

Each message is classified along two axes in a single classifier call: **category** (code / specific /
general) and **difficulty** (easy / medium / hard). Category picks the provider, difficulty picks the tier
within that provider. Chosen with cost in mind rather than always reaching for each provider's flagship.

| Category | Provider | Why |
|---|---|---|
| `code` (programming/IT/devops) | Anthropic | Claude tends to be the strongest at code and technical reasoning |
| `specific` (factual/knowledge questions) | OpenAI | Solid general knowledge accuracy |
| `general` (casual/creative/opinion) | xAI | Grok reads more conversational/human, a nice fit for chit-chat |

| Tier | code (Anthropic) | specific (OpenAI) | general (xAI) |
|---|---|---|---|
| `easy` | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | `gpt-5-mini` | `grok-4.3` |
| `medium` | `us.anthropic.claude-sonnet-4-6` | `gpt-5.4-mini` | `grok-4.5` |
| `hard` | `us.anthropic.claude-opus-4-6-v1` | `gpt-5.2` | `grok-4.7` |

`MODEL_CLASSIFIER` stays `gpt-4o-mini` - cheap, fast, only needs to output "category,difficulty", doesn't
need to sound human so provider doesn't matter here.

Deliberately avoided each provider's priciest flagship (e.g. `us.anthropic.claude-opus-5-5`, `gpt-5.5-pro`) to keep
per-message cost down on 1min.ai credits - bump individual cells up in `.env` if quality matters more than
cost for your use case.

Source of truth for prices/context windows: check the 1min.ai dashboard directly, since it can change
independently of this file.