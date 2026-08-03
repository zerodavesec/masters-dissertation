# Local LLMs

The research uses local LLMs to create detection rules. Notably there are 2 different workflows:

1. A Parsing and Classification Workflow that reads through a set of lines in a JSONL file and decides whether they are suspicious/malicious or not. By doing this, a file is created in the form of `malicious_<original_filename>.jsonl`.
   - This file is then used for the AI + Manual approach, where the rules will be created manually from those logs, as well as,
   - Serving as the previous step for the complete AI workflow. This logs are then fed to the `rule_builder` workflow that will decide to create 3 detection rules and 1 correlation. Out of the three detection rules, 2 are picked manually.
2. The `rule_builder` workflow is a set of constraints and instructions on how to successfully create SigmaHQ detection and correlation rules.

## Ollama

Ollama is being used to load and serve local LLMs in my home network. The prompt used to to so is:

```bash
OLLAMA_HOST=0.0.0.0:11434 OLLAMA_CONTEXT_LENGTH=262144 nohup ollama serve > ~/ollama.log 2>&1 &
```

Other `ollama` information:
Commands run on August 3rd.

```bash
$ ollama --version
ollama version is 0.32.2
```

```bash
$ curl http://localhost:11434/api/version
{"version": "0.32.2"}%

$ curl http://localhost:11434/api/tags

```

## Gemma4:12b Configuration in scripts

One of the most difficult decision was to chose one or more llms for these processes. Initially, the models chosen were:

- Gemma4:e4b for the `parsing_and_classification` workflow.
- Gemma4:12b for the `rule_builder` workflow.

However, after prior-to-experimentation testing, the difference in speed between the `e4b` and the `12b` models was not relevant for the timeline of this research. It takes twice as much time but results seem to be better as the model is 3 times bigger or "smarter".

Other models were considered such as Gemma4:27b and Qwen3.6:27b and Qwen3.6:35b, however, the workflows were one to three orders of magnitude slower due to `tok/s` but also due to the increased reasoning of those models. Often taking over 2 hours for tasks where the 12 billion parameter model Gemma4:12b performed in single-digit minutes.

The premise of this research is whether we can automate detection engineering, not at a grand scale with limited resources but in a local workstation with similar specs of what a detection engineer will have. The environment, the sandbox, the machine learning model, and ultimate the AI workflows can all be run in a computer with a discrete GPU and 16 GiB of RAM. Even without a discrete GPU and a CPU/NPU with 16GiB of RAM.

### Model Specs and Configuration

The model specs are:

The configuration parameters are:

- `parsing_and_classification` workflow:
  - Temperature: 0
  - Context: 16384
  - Full config in [parsing_and_classification.py](../../src/ai_workflows/parsing_and_classification.py)

  ```python
    response: ChatResponse = client.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(payload, ensure_ascii=False),
            },
        ],
        format="json",
        options={"temperature": 0, "num_ctx": NUM_CTX},
    )
  ```

- `rule_builder` workflow:
  - Temperature: 0
  - Context: 262144
  - Full config in [rule_builder](../../src/ai_workflows/rule_builder.py)
  ```python
    response = client.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": payload},
        ],
        format="json",
        options={"temperature": 0, "num_ctx": NUM_CTX},
    )
  ```

## Gemma4:12b Model Information

Commands run on August 3rd.

```bash
$ ollama list
NAME            ID              SIZE    MODIFIED
gemma4:12b      4eb23ef187e2    9.6GB   10 days ago
```

```bash
$ ollama show gemma4:12b
```

```bash
$ ollama show gemma4:12 --modelfile
```
