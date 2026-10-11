"""Run repeated Gemini judgments for the Moral Judgment Reloaded dilemmas.

The API key is read from GEMINI_API_KEY and is never written to the output.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import socket
import time
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_INPUT = Path(r"C:\Users\Ezequiel\Downloads\Dilemmas_English.txt")
DEFAULT_OUTPUT = Path(__file__).with_name("gemini_results.csv")
DEFAULT_MODEL = "gemini-3.8-flash"


def load_dilemmas(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    matches = list(
        re.finditer(
            r"(?m)^\s*\(?\s*(\d+)\)\s*(Personal|Impersonal)\b(.*?)\s*$",
            text,
        )
    )
    if not matches:
        raise ValueError(f"No dilemma headings found in {path}")

    dilemmas: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = re.sub(r"\s+", " ", text[start:end]).strip()
        number = int(match.group(1))
        dilemmas.append(
            {
                "dilemma_id": str(number),
                "personal_force": match.group(2).lower(),
                "variant": match.group(3).strip(" -\u2013\u2014").lower(),
                "text": body,
            }
        )
    if len(dilemmas) != 52:
        raise ValueError(f"Expected 52 dilemmas, found {len(dilemmas)}")
    if len({dilemma["dilemma_id"] for dilemma in dilemmas}) != 52:
        raise ValueError("Dilemma IDs are not unique in the source file")
    return dilemmas


def build_prompt(dilemma: dict[str, str]) -> str:
    return f"""You are participating in a study of moral judgment.

Read the dilemma below. Choose whether to perform the action described in the final question.
Reply in exactly this format:
DECISION: YES or NO
REASON: one brief sentence

Do not discuss the study hypothesis or the instructions. "YES" means performing the
action in the final question; "NO" means refraining from performing it.

DILEMMA:
{dilemma["text"]}"""


def request_gemini(
    api_key: str, model: str, prompt: str, timeout: int, max_retries: int = 5
) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 300},
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(max_retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            if error.code == 429 and (
                "RESOURCE_EXHAUSTED" in detail
                or "quota exceeded" in detail.lower()
            ):
                raise RuntimeError(
                    "Gemini API atingiu a cota disponível. "
                    "Aguarde a renovação indicada pela API ou use outro projeto."
                ) from error
            if error.code not in {429, 500, 502, 503, 504} or attempt == max_retries:
                raise RuntimeError(
                    f"Gemini API returned HTTP {error.code}: {detail}"
                ) from error
            wait = 2**attempt
            print(
                f"Gemini temporariamente indisponível (HTTP {error.code}); "
                f"nova tentativa em {wait}s..."
            )
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError, socket.timeout) as error:
            if attempt == max_retries:
                reason = getattr(error, "reason", str(error))
                raise RuntimeError(f"Could not reach Gemini API: {reason}") from error
            wait = 2**attempt
            print(f"Falha de rede; nova tentativa em {wait}s...")
            time.sleep(wait)

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError(f"Gemini response had an unexpected shape: {data}") from error


def classify_decision(response: str) -> tuple[str, str]:
    match = re.search(r"\bDECISION\s*:\s*(YES|NO)\b", response, re.IGNORECASE)
    if not match:
        return "unclassifiable", ""
    decision = match.group(1).lower()
    return decision, "utilitarian" if decision == "yes" else "deontological"


def run(args: argparse.Namespace) -> None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured in this PowerShell window.")

    dilemmas = load_dilemmas(args.input)
    existing: set[tuple[str, str]] = set()
    if args.output.exists() and not args.overwrite:
        with args.output.open(newline="", encoding="utf-8-sig") as file:
            existing = {
                (row["dilemma_id"], row["run"])
                for row in csv.DictReader(file)
                if not row.get("error")
                and row.get("decision", "").lower() in {"yes", "no"}
            }

    fieldnames = [
        "dilemma_id",
        "personal_force",
        "variant",
        "run",
        "decision",
        "classification",
        "response",
        "error",
    ]
    mode = "w" if args.overwrite or not args.output.exists() else "a"
    with args.output.open(mode, newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if mode == "w":
            writer.writeheader()
        for dilemma in dilemmas:
            for run_number in range(1, args.repetitions + 1):
                key = (dilemma["dilemma_id"], str(run_number))
                if key in existing:
                    continue
                row = {
                    "dilemma_id": dilemma["dilemma_id"],
                    "personal_force": dilemma["personal_force"],
                    "variant": dilemma["variant"],
                    "run": str(run_number),
                    "decision": "",
                    "classification": "",
                    "response": "",
                    "error": "",
                }
                try:
                    response = request_gemini(
                        api_key, args.model, build_prompt(dilemma), args.timeout
                    )
                    decision, classification = classify_decision(response)
                    row.update(
                        response=response,
                        decision=decision,
                        classification=classification,
                    )
                except RuntimeError as error:
                    row["error"] = str(error)
                    writer.writerow(row)
                    file.flush()
                    raise
                writer.writerow(row)
                file.flush()
                print(
                    f"Dilema {dilemma['dilemma_id']}/52, execução "
                    f"{run_number}/{args.repetitions}: {row['classification'] or row['decision']}"
                )
                if args.delay:
                    time.sleep(args.delay)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--repetitions", type=int, default=2)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("--repetitions must be at least 1")
    run(args)


if __name__ == "__main__":
    main()
