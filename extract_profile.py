"""
Part A - Extraction Layer

Reads a raw, unstructured dispatcher-driver phone transcript and produces
a structured driver profile via an LLM extraction call.

Usage:
    export ANTHROPIC_API_KEY=...
    python extract_profile.py transcript.txt > driver_profile.json
"""

import sys
import json
import anthropic

EXTRACTION_PROMPT = """You are extracting a structured driver profile from a raw \
dispatcher-driver phone call transcript. The driver never states these fields \
as clean data, they are scattered through ordinary speech and sometimes only \
implied rather than said outright.

Extract exactly these fields:
- current_location (city, state)
- current_lat, current_lon
- home_base (city, state)
- home_lat, home_lon
- min_rate_per_mile (number, USD)
- equipment_types (list of strings: only what the driver actually runs, not \
  every trailer type that comes up in the conversation)
- weight_capacity_lb (number; if not stated directly, infer a reasonable value \
  for the stated equipment and explain the inference in "notes")
- notes (string: flag every field where you interpreted rather than read a \
  literal statement, and why)

Return ONLY valid JSON. No preamble, no markdown fences.

TRANSCRIPT:
{transcript}
"""


def extract(transcript: str) -> dict:
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[
            {"role": "user", "content": EXTRACTION_PROMPT.format(transcript=transcript)}
        ],
    )
    raw = resp.content[0].text.strip()
    return json.loads(raw)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "transcript.txt"
    with open(path) as f:
        transcript_text = f.read()
    profile = extract(transcript_text)
    print(json.dumps(profile, indent=2))
