# Sample Text Processor Tool

This is a sample tool that demonstrates how to implement a tool using the FastAPI Tools Framework. This tool uses an LLM to process text in different ways (summarize, analyze, etc.) based on prompts.

## 📋 Overview

The Sample Text Processor:
- Takes input text and processes it using an LLM
- Supports different "prompt types" for different processing tasks
- Demonstrates how to load prompts from YAML files
- Shows how to integrate with the LLM client

## 📁 Structure

```
sample_text_processor/
├── __init__.py          # Package indicator
├── tool.py              # Main tool implementation
├── schemas.py           # Input/output schemas
├── config.toml          # Tool-specific configuration
└── prompts/             # Prompt templates
    ├── summarize.yaml   # Summarization prompt
    └── analyze.yaml     # Analysis prompt
```

## 💻 Implementation Details

### Input Schema

The tool accepts:
- `text`: The text to process
- `max_length`: Maximum length of the processed text (default: 100)
- `prompt_type`: Type of processing to perform (summarize, analyze, etc.)

### Output Schema

The tool returns:
- `processed_text`: The processed text
- `original_length`: Length of the original text
- `processed_length`: Length of the processed text

### Configuration

Tool-specific settings are defined in `config.toml`:
- Default prompt type
- Maximum output length
- LLM-specific settings (temperature, max tokens)

### Prompts

The tool uses YAML files to define prompts for different processing tasks:
- `summarize.yaml`: Prompt for summarizing text
- `analyze.yaml`: Prompt for analyzing text

## 🚀 Usage

### API Request Example

```json
POST /tools/text_processor

{
  "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies aliquam, nunc nisl aliquet nunc, quis aliquam nisl nunc quis nisl. Nullam auctor, nisl eget ultricies aliquam, nunc nisl aliquet nunc, quis aliquam nisl nunc quis nisl.",
  "max_length": 50,
  "prompt_type": "summarize"
}
```

### API Response Example

```json
{
  "processed_text": "This text is about Lorem ipsum, featuring repetitive phrases and structure.",
  "original_length": 259,
  "processed_length": 69
}
```

## ✨ Adding New Prompt Types

To add a new prompt type:

1. Create a new YAML file in the `prompts` directory, e.g., `evaluate.yaml`
2. Define the system and human messages:
   ```yaml
   system: |
     You are an expert evaluator. Evaluate the provided text for clarity,
     coherence, and effectiveness.
   
   human: |
     Please evaluate the following text:
     
     {text}
     
     Limit your evaluation to {max_length} words.
   ```
3. The tool will automatically pick up the new prompt type

## 🔄 How It Works

1. When the tool is called, it loads prompts from YAML files in the `prompts` directory
2. It selects the appropriate prompt based on the `prompt_type` parameter
3. It accesses the LLM client through `get_model()`
4. It constructs a LangChain chain with the prompt and LLM
5. It executes the chain with the input text
6. It returns the processed text and metadata

This sample demonstrates patterns and best practices for creating your own tools.