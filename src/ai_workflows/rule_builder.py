import argparse
import json
import os
import time
import uuid
from datetime import date
from typing import Any

from dotenv import load_dotenv
from ollama import Client

load_dotenv()
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST")  # type: ignore

MODEL: str = "gemma4:12b"
NUM_CTX: int = 262144
MAX_RETRIES: int = 3

client: Client = Client(host=OLLAMA_HOST)

# Small models need tutoring in the sense that I need to tell them what to do
# and how to do it. I am providing a prompt with examples to replicate, things
# to avoid, and how to think about generalising rules. Bigger modesl may improve
# this reasoning
SIGMA_SYNTAX_RULES = """
Sigma field-matching rules you MUST follow:

- Plain match example:
      Image: 'C:\\Windows\\System32\\wevtutil.exe'
- Ends with string needs the <field_name>|endswith modifier. Example:
      Image|endswith: '\\wevtutil.exe'
- To require a field contain MULTIPLE substrings simultaneously (AND), use
  `<field_name>|contains|all` with a YAML list - never concatenate wildcards into one string:
      CommandLine|contains|all:
          - 'uninstall-manifest'
          - 'Microsoft-Antimalware-Service'
- To match ANY of several substrings (OR), use `<field_name>|contains` with a list:
      CommandLine|contains:
          - 'foo'
          - 'bar'
- Use `<field_name>|contains` and a list of values to represent OR between the values
  and a `<field_name>|contains|all` and a list of values to represent AND condition 
  between the values
- Never write a value like `"*foo*" "*bar*"` as a single string. That is not
  valid Sigma syntax under any modifier.
- Multiple fields inside one selection block are implicitly ANDed.
- Multiple selection blocks combined in `condition` (e.g. `selection1 and not filter`)
  let you express AND/OR/NOT across blocks - use a `filter` block with
  `condition: selection and not filter` to exclude known-good activity when
  you can see one in the data (e.g. a signed, expected parent process).
- Only use fields that actually appear in the supplied events. Do not invent
  fields, the detection block is ALWAYS named "detection".
- When using `|endswith: '\\value'`, you should only use one (1) backslash, if you
use two (2) backslashes you must double quote it, i.e. "\\\\value"
- Avoid usage like: 
        CommandLine: 
            - "*\\"-ExecutionPolicy\\" \\"Bypass\\"*"
        this should be
        CommandLine|contains|all:
            - '-ExecutionPolicy'
            - 'Bypass'
        OR
        CommandLine|contains:
            - '-ExecutionPolicy Bypass'
- It is better to separate items into different selections and to attempt to 
match more than one thing in the log. For example:
    selection_1:
        Image|endswith: '\\rundll32.exe'
        CommandLine|contains: '.jpg'
    selection_2:
        CommandLine|contais|all:
            - 'rundll32.exe'
            - '.jpg'
    condition: selection_1 or selection_2
- Never have a field:value that is `fieldName: *`, that is detecting on everything.
- If you use the asterisk (`*`) in any values or list of values, single or double quote
the string that contains it. But it will always be better if you use a <field_name>|contains|all 
modifier and break the string into substrings to match. Example:
    ```
    Image:
        - "*\\AppData\\*\\Temp\\*"
    ```
    is NOT allowed, it should be CORRECT LIKE tHE FOLLOWING:
    ```
    Image|contains|all:
        - "\\AppData\\"
        - "\\Temp\\"
    ```
"""


DETECTION_EXAMPLE = """
title: Suspicious wevtutil Usage to Disable Antimalware Service
id: 3d1f2b3a-1111-4a2b-9c3d-000000000001
status: experimental
description: Detects wevtutil.exe being used to remove the Microsoft-Antimalware-Service event log manifest, a technique used to blind Defender logging before further malicious activity.
references:
    - internal-case-0001
author: Automated Analysis
date: 2026-07-24
tags:
    - attack.defense_evasion
    - attack.t1562.001
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\wevtutil.exe'
        CommandLine|contains|all:
            - 'uninstall-manifest'
            - 'Microsoft-Antimalware-Service'
    condition: selection
falsepositives:
    - Legitimate log manifest maintenance by administrators (rare)
level: high
"""

CORRELATION_EXAMPLE = """
title: Defender Tampering Followed by Outbound Connection
id: 3d1f2b3a-1111-4a2b-9c3d-000000000003
status: experimental
description: Correlates Defender log tampering with a subsequent outbound network connection from the same host within a short window, indicating tampering followed by likely C2 or exfiltration activity.
correlation:
    type: temporal
    rules:
        - 3d1f2b3a-1111-4a2b-9c3d-000000000001
        - 3d1f2b3a-1111-4a2b-9c3d-000000000002
    group-by:
        - Computer
    timespan: 5m
level: high
"""

DETECTION_TEMPLATE = """
title: <short descriptive title>
id: <UUID PROVIDED BELOW - use it as-is>
status: experimental
description: <one or two sentences on what this detects and why>
author: AI Workflows
date: <TODAY'S DATE PROVIDED BELOW>
tags:
    - attack.<tactic>
    - attack.<techniqueid>
logsource:
    category: <process_creation | file_event | registry_event | pipe_created | dns_query | image_load>
    product: windows
detection:
    selection:
        <field or field|modifier>: <value or list of values>
    selection_2:
        <Another field or field|modifier>: <another value or list of values>
    condition: selection
level: <informational | low | medium | high | critical>
"""

CORRELATION_TEMPLATE = """
title: <short descriptive title for the correlated behavior>
id: <new UUID PROVIDED BELOW - use it verbatim>
status: experimental
description: <what sequence/pattern of events this identifies and why it matters>
correlation:
    type: <temporal | event_count | value_count>
    rules:
        - <id of detection_rule_1>
        - <id of detection_rule_2>
    group-by:
        - <field events must share, e.g. Computer, User, ProcessGuid>
    timespan: <e.g. 5m, 1h>
level: <medium | high | critical>
"""


SYSTEM_PROMPT = f"""
You are a senior detection engineer specialising in Sysmon telemetry and SigmaHQ rules.

{SIGMA_SYNTAX_RULES}

You are given a JSON array of Sysmon events that have been flagged as suspicious. 
Perform an in-depth review across ALL of the events together (not one at a time) 
and produce SigmaHQ-compliant detection rules as described below.

You must produce exactly:

1. TWO standalone Sigma detection rules, each targeting a distinct malicious
   behaviour you observe in the events, i.e. different techniques, different
   event types, different processes. DO NOT write two rules for the same
   single indicator. You may use two or more "selections" and 
   create conditional and-or logic in the condition section. Where possible
   avoid doing condition: selection, in which the selection only contains 1 or 2
   items as that does not match your seniority as a detection engineer.
2. ONE Sigma correlation rule that ties together 1 (in event_count) or 2 (in temporal)
   of the standalone sigma detection rules events (via the two detection rules above, or via 
   event_count logic) to describe a higher-confidence attack 
   pattern, i.e. process creation followed by an outbound connection from the 
   same host/user within a short timespan. 

Here is a worked example of a correctly-formed detection rule:
{DETECTION_EXAMPLE}
And a worked example of a correlation rule:
{CORRELATION_EXAMPLE}

Do NOT add or edit root keys, you are not allowed to do that.

IMPORTANT - READ EXTREMELY CAREFULLY:
- Detections should have more than one field for each selection block. Alternatively,
detections should have 2 or more selection blocks with one field match it. Anything less
is not up to professional standard.
- A selection block and fields are more precise the more information they contain. EXAMPLES:
    BAD precision: `<file_name>|contains: folder`. 
    GOOD Precision: ```
        <field_name>|contains:
            - \\folder1\\folder2\\
            - \\folder3\\
            - \\folder4\\
        <another_field>|endswith: "\\something.exe"
    ```
- Firstly, you must prioritise precision of the rule, secondly generalisation capabilities.
- Make sure the rule is created trying to avoid False Positives.
- After that, be concerned about how well the rule will generalise.
- You need to balance the specificity of the rule against the sample to prevent unwanted
noise with the generalisation capabilities of the rule. Every rule requires balance
between specificity and broadness, to (1) reduce noise and (2) generalise where possible.
- Instead of detecting "abc.ps1 drops xyz.exe in C:\\system32\\ and then executes it" aim for
"*.ps1 drops *.exe in 'suspicious directory' and executes it". Detection rules
MUST be sound on their own, i.e. a detection rule can't just be something that is 
non malicious and only defined to be used in a correlation, it must have security 
value on its own.

BASIC CONSTRAINTS:
- If you use the asterisk (`*`) in any detection block values or list of values, single or double quote
the string that contains it. HOWEVER, it will always be BETTER if you use a `|contains|all` or `|contains` 
modifier and break the string into substrings to match.
- DO NOT USE THE EXECUTION LOG, that is an EVENTID 1 where the .exe or the .ps1 sits
in C:\\Users\\zerodave\\Desktop\\Studies. You will see flags for bypass in powershell,
or execution from that folder. You CANNOT develop a detection around that event.
- You may use follow on events that use that path
but it should be generalising to something like `Image|endswith: '.exe'` rather than 
the full path.
- A more robust deteciton would have 2 or more selections and a condition like:
selection1 and (selection2 or selection3) to have better chances of catching evil
- Avoid using things that do not establish malicious behaviour. For example:
Adding a Windows Defender exclusion is not malicious, BUT adding a windows defender
exclusion for an .exe or .ps1 in a temp or appdata path is considered suspicious.
- You must focus on creating quality detection rules at all times, not just 'things'
that would detect the set of logs provided. Think about the big picture, everytime
you create a rule, ask yourself: is that rule good at (1) identifying real evil and 
(2) generalisation.
- Do NOT hallucinate mitre attack tactics for the tags. Use known TACTICs ONLY.
- Do NOT hallucinate malicious behaviour just because it is unusual.


Use these exact UUIDs for the "id" field, do not invent your own:
- detection_rule_1 id: {{DETECTION_ID_1}}
- detection_rule_2 id: {{DETECTION_ID_2}}
- correlation_rule id: {{CORRELATION_ID}}

Use this date for the "date" field: {{TODAY}}

Follow this template for each detection rule (fill in the placeholders,
keep the YAML structure and key names exactly as shown):

{DETECTION_TEMPLATE}

Follow this template for the correlation rule (fill in the placeholders,
keep the YAML structure and key names exactly as shown). The "rules" list
must reference the id values of two of detection_rule_1, detection_rule_2, and
deteciton_rule_3 above. Choose and correlate the two that make the MOST sense
from a security point of view:

{CORRELATION_TEMPLATE}

Base every rule strictly on fields and values actually present in the
supplied events. Do not invent field values, hostnames, hashes, or IPs
that are not in the input. If you cannot justify two distinct detections
or one meaningful correlation from the data, still produce your best
analytical judgement but note the low-confidence reasoning inside the
rule's "description" field.

Respond ONLY with a single JSON object of this exact shape, and nothing else:

{{
  "detection_rule_1": "<complete YAML for rule 1 as a single string, newlines as \\n>",
  "detection_rule_2": "<complete YAML for rule 2 as a single string, newlines as \\n>",
  "correlation_rule": "<complete YAML for the correlation rule as a single string, newlines as \\n>"
}}

Do not add markdown fences, commentary, or extra fields.
"""


def load_events(filename: str) -> list[str]:
    events: list[str] = []

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            events.append(obj)

    return events


def parse_llm_result(output: Any) -> dict[str, str] | None:
    try:
        data: Any = json.loads(output)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    required_keys = {"detection_rule_1", "detection_rule_2", "correlation_rule"}

    if not required_keys.issubset(data.keys()):
        return None

    for key in required_keys:
        if not isinstance(data[key], str) or not data[key].strip():
            return None

    return data


def analyse_events(
    events: list[str],
    detection_id_1: str,
    detection_id_2: str,
    correlation_id: str,
) -> tuple[dict[str, str], dict[str, Any]]:
    system_prompt: str = "<|think|>\n" + (
        SYSTEM_PROMPT.replace("{DETECTION_ID_1}", detection_id_1)
        .replace("{DETECTION_ID_2}", detection_id_2)
        .replace("{CORRELATION_ID}", correlation_id)
        .replace("{TODAY}", date.today().isoformat())
    )

    payload: str = json.dumps(events, ensure_ascii=False)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            start = time.time()
            response = client.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": payload},
                ],
                format="json",
                options={
                    "temperature": 0,
                    "num_ctx": NUM_CTX,
                    "num_predict": 131072,
                },
            )

            elapsed = time.time() - start
            output: Any = response["message"]["content"].strip()
            result: dict[str, str] = parse_llm_result(output)  # type: ignore

            if result is not None:
                stats = {
                    "input_tokens": response.get("prompt_eval_count", 0),
                    "output_tokens": response.get("eval_count", 0),
                    "seconds": elapsed,
                }
                return result, stats
            print(
                f"Attempt {attempt}/{MAX_RETRIES}: response failed validation, retrying"
            )
        except Exception as exc:
            print(f"Attempt {attempt}/{MAX_RETRIES}: request failed ({exc}), retrying")

        time.sleep(1)

    raise RuntimeError("LLM failed to produce valid rule content after retries")


def write_yaml(path: str, content: str):
    # Model returns YAML text with literal \n escapes already decoded by json.loads
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")


def get_filename() -> str:
    parser = argparse.ArgumentParser(
        description="Process a JSONL fiel to extract malcicious logs."
    )
    parser.add_argument("filename", help="Path to the input file")
    args = parser.parse_args()

    return args.filename


def main():
    input_file: str = get_filename()
    input_sample_id: str = os.path.basename(input_file).split("_")[2]
    output_path: str = f"./detection_rules/ai_workflows/AIW_{input_sample_id}/"

    events: list[str] = load_events(input_file)
    if not events:
        print(f"No events found in {input_file}")
        return

    os.makedirs(output_path, exist_ok=True)

    detection_id_1: str = str(uuid.uuid4())
    detection_id_2: str = str(uuid.uuid4())
    correlation_id: str = str(uuid.uuid4())

    print(f"Loaded {len(events)} malicious events from {input_file}")
    print("Requesting in-depth analysis and rule generation...")

    try:
        result, stats = analyse_events(
            events, detection_id_1, detection_id_2, correlation_id
        )
    except RuntimeError as exc:
        print(f"Failed: {exc}")
        return

    write_yaml(
        os.path.join(output_path, f"detection_rule_1_{detection_id_1}.yml"),
        result["detection_rule_1"],
    )
    write_yaml(
        os.path.join(output_path, f"detection_rule_2_{detection_id_2}.yml"),
        result["detection_rule_2"],
    )
    write_yaml(
        os.path.join(output_path, f"correlation_rule_{correlation_id}.yml"),
        result["correlation_rule"],
    )

    print()
    print("Finished")
    print(f"Detection rule 1: detection_rule_1_{detection_id_1}.yml")
    print(f"Detection rule 2: detection_rule_2_{detection_id_2}.yml")
    print(f"Correlation rule: correlation_rule_{correlation_id}.yml")
    print(f"Input tokens: {stats['input_tokens']}")
    print(f"Output tokens: {stats['output_tokens']}")
    print(f"Runtime seconds: {stats['seconds']:.2f}")
    print(f"Output directory: {output_path}")


if __name__ == "__main__":
    main()
