<!-- 4cca736b-0db4-4480-832f-004c32d306a9 1b4320fa-c9c6-4f7e-8e61-dda452f2e570 -->
# DeepSeek & Qwen Integration Plan

## Scope

- Replace Anthropic-specific config and generator logic so DeepSeek `deepseek-chat` and Qwen OpenAI-compatible endpoints are selectable.
- Update docs to explain new provider setup and env vars.

## Approach

1. Audit current Anthropic wiring in `backend/ai_generator.py`, `backend/config.py`, `backend/rag_system.py` to outline provider touchpoints.
2. Refactor `AIGenerator` into a provider-agnostic client using OpenAI-compatible SDK: add dynamic base URL, API key, model selection, and keep tool-use flow intact.
3. Extend configuration (`Config` dataclass, `.env` guidance) to support provider choice (`MODEL_PROVIDER`, API keys, base URLs, model names) with sensible defaults for DeepSeek/Qwen.
4. Adjust `rag_system` initialization and any call sites to pass new config fields; ensure tool invocation remains functional.
5. Update documentation (`README.md`, `docs/system_overview.md`) detailing DeepSeek/Qwen setup, environment variables, and migration steps from Anthropic.

## Implementation Todos

- analyze-current: Review existing Anthropic integrations and identify required abstraction points.
- refactor-generator: Generalize `AIGenerator` to work with OpenAI-compatible endpoints and provider configs.
- update-config: Expand configuration and `.env` guidance for DeepSeek/Qwen providers.
- refresh-docs: Update documentation to reflect new provider options and setup steps.

### To-dos

- [ ] Review `backend/ai_generator.py`, `backend/config.py`, and related files to map Anthropic-specific logic.
- [ ] Refactor AI generator to support OpenAI-compatible providers (DeepSeek, Qwen) with configurable base URLs/models/API keys.
- [ ] Extend configuration/env handling for provider selection and new keys.
- [ ] Document DeepSeek/Qwen setup steps and updated environment variables.