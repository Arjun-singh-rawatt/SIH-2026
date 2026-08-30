# AI Providers Extension Directory

This directory is reserved for future plug-in AI providers:

- `gemini_provider.py` (Google Gemini 1.5 Flash / Pro via `google-generativeai`)
- `huggingface_provider.py` (Local/remote fine-tuned RoBERTa SIF classifier)
- `openai_provider.py` (OpenAI GPT-4o / Azure OpenAI)
- `custom_classifier.py` (ONNX / Torch custom safety precursor inference pipeline)

All providers must implement the `AIProvider` protocol defined in `app.ai.base.AIProvider`.
