import argparse
import json
import os
import time
from typing import Any, Generator

import ollama
from dotenv import load_dotenv
from ollama import ChatResponse, Client

load_dotenv()
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST")  # type: ignore

MODEL: str = "gemma4:12b"

BATCH_SIZE: int = 10
NUM_CTX: int = 16384
MAX_RETRIES: int = 3


INTERESTING_EVENT_IDS: set[int] = {
    1,  # Process Create
    3,  # Network Connection
    7,  # Image Loaded
    11,  # File Create
    12,  # Registry object create/delete
    13,  # Registry value set
    14,  # Registry rename
    18,  # Pipe Created
    22,  # DNS Query
}


client: Client = ollama.Client(host=OLLAMA_HOST)


SYSTEM_PROMPT: str = """
You are a senior cybersecurity analyst specialising in Sysmon telemetry. 

Analyse the supplied Sysmon events.

Return only:

{
  "malicious_indexes": []
}

The array must contain only integer indexes from the input.

Example:

{
  "malicious_indexes": [1,5,9]
}

If no events are malicious:

{
  "malicious_indexes": []
}

Consider:

- malware execution
- suspicious process execution
- PowerShell abuse
- encoded commands
- command interpreter abuse
- suspicious parent-child relationships
- persistence
- registry abuse
- suspicious DLL loading
- suspicious file creation
- malicious network activity
- suspicious DNS activity
- aspnet_compiler targeting unusual dlls

Do not classify something as malicious only because:

- it is uncommon
- the filename is unfamiliar
- an error occurred
- the user is unknown
- metadata looks unusual

Do not provide explanations.
Do not provide markdown.
Do not add extra fields.
"""

COMMON_FIELDS: set[str] = {
    "EventID",
    "UtcTime",
    "Computer",
    "User",
    "Image",
    "ProcessId",
    "ProcessGuid",
    "ParentImage",
    "ParentProcessId",
    "ParentProcessGuid",
    "ParentCommandLine",
    "CommandLine",
    "Hashes",
    "HashType",
    "IntegrityLevel",
    "LogonId",
    "TerminalSessionId",
}


EVENT_FIELDS: dict[int, set[str]] = {
    1: {
        "CurrentDirectory",
        "OriginalFileName",
        "Description",
        "Product",
        "Company",
        "Signed",
        "Signature",
        "SignatureStatus",
    },
    3: {
        "Protocol",
        "SourceIp",
        "SourcePort",
        "DestinationIp",
        "DestinationPort",
        "DestinationHostname",
        "Initiated",
    },
    7: {
        "ImageLoaded",
        "FileVersion",
        "Description",
        "Product",
        "Company",
        "OriginalFileName",
        "Signed",
        "Signature",
        "SignatureStatus",
    },
    11: {
        "TargetFilename",
        "CreationUtcTime",
        "Contents",
        "RuleName",
        "CurrentDirectory",
        "OriginalFileName",
        "Description",
        "Product",
        "Company",
        "Signed",
        "Signature",
        "SignatureStatus",
    },
    12: {
        "EventType",
        "TargetObject",
        "Details",
    },
    13: {
        "EventType",
        "TargetObject",
        "Details",
    },
    14: {
        "EventType",
        "TargetObject",
        "Details",
    },
    18: {
        "PipeName",
    },
    22: {
        "QueryName",
        "QueryStatus",
        "QueryResults",
    },
}


def load_filtered_events(filename: str) -> dict[int, dict[str, str]]:
    events: dict[int, dict[str, str]] = {}
    index: int = 0

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            event_id = (
                obj.get("EventID")
                or obj.get("EventId")
                or obj.get("eventID")
                or obj.get("eventId")
            )

            try:
                event_id: int = int(event_id)
            except TypeError, ValueError:
                continue

            if event_id not in INTERESTING_EVENT_IDS:
                continue

            events[index] = obj
            index += 1

    return events


def build_payload_event(index: int, event: dict[str, str]) -> dict[str, Any]:
    event_id = (
        event.get("EventID")
        or event.get("EventId")
        or event.get("eventID")
        or event.get("eventId")
    )

    try:
        event_id = int(event_id)  # type: ignore
    except TypeError, ValueError:
        event_id = None

    fields: set[str] = set(COMMON_FIELDS)

    fields.update(EVENT_FIELDS.get(event_id, set()))  # type: ignore

    result: dict[str, Any] = {"index": index}

    for field in fields:
        value: Any = event.get(field)

        if value is not None:
            result[field] = value

    return result


def create_batches(events: dict[int, dict[str, Any]]) -> Generator[dict[int, Any]]:
    indexes: list[int] = list(events.keys())

    for i in range(0, len(indexes), BATCH_SIZE):
        batch_indexes = indexes[i : i + BATCH_SIZE]

        yield {idx: events[idx] for idx in batch_indexes}


def parse_llm_result(output: str, valid_indexes: set[int]) -> list[int] | None:
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    indexes = data.get("malicious_indexes")

    if not isinstance(indexes, list):
        return None

    result: list[int] = []

    for idx in indexes:
        if isinstance(idx, int) and idx in valid_indexes:
            result.append(idx)

    return result


def analyse_batch(batch: dict[Any, Any]):
    payload: list = []

    for index, event in batch.items():
        payload.append(build_payload_event(index, event))

    valid_indexes: set[int] = set(batch.keys())

    for _ in range(MAX_RETRIES):
        try:
            start = time.time()
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

            elapsed = time.time() - start
            output = response["message"]["content"].strip()
            result = parse_llm_result(output, valid_indexes)

            if result is not None:
                return result, {
                    "input_tokens": response.get("prompt_eval_count", 0),
                    "output_tokens": response.get("eval_count", 0),
                    "seconds": elapsed,
                }
        except Exception:
            pass

        time.sleep(1)

    raise RuntimeError("LLM failed after retries")


def get_filename() -> str:
    parser = argparse.ArgumentParser(
        description="Process a JSONL fiel to extract malcicious logs."
    )
    parser.add_argument("filename", help="Path to the input file")
    args = parser.parse_args()

    return args.filename


def main():
    filename_blob: str = get_filename()
    input_file: str = f"{filename_blob}.jsonl"
    output_file: str = f"malicious_{filename_blob}.jsonl"

    events: dict[int, dict[str, Any]] = load_filtered_events(input_file)
    total_batches: int = (len(events) + BATCH_SIZE - 1) // BATCH_SIZE
    processed: int = 0
    malicious_count: int = 0
    completed_batches: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_seconds: float = 0

    with open(output_file, "w", encoding="utf-8") as out:
        for batch_number, batch in enumerate(create_batches(events), start=1):
            try:
                malicious_indexes, stats = analyse_batch(batch)
                total_input_tokens += stats["input_tokens"]
                total_output_tokens += stats["output_tokens"]
                total_seconds += stats["seconds"]

                for idx in malicious_indexes:
                    out.write(json.dumps(events[idx], ensure_ascii=False) + "\n")

                    malicious_count += 1

                processed += len(batch)
                completed_batches += 1

                print(f"Batch {batch_number}/{total_batches} completed")

            except Exception:
                print(f"Batch {batch_number}/{total_batches} failed")

    print()
    print("Finished")
    print(f"Processed events: {processed}")
    print(f"Malicious objects written: {malicious_count}")
    print(f"Completed batches: {completed_batches}/{total_batches}")
    print(f"Input tokens: {total_input_tokens}")
    print(f"Output tokens: {total_output_tokens}")
    print(f"Total tokens: {total_input_tokens + total_output_tokens}")
    print(f"Runtime seconds: {total_seconds:.2f}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    main()
