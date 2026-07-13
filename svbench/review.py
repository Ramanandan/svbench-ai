"""The Review agent -- the core contribution.

Given a discordant locus (a samplot image + a deterministic evidence packet),
Claude Opus 4.8 returns a structured `SVVerdict` explaining *why* the caller and
the truth set disagree, and whether the disagreement is a genuine caller error
or a benchmarking artifact.

Two entry points:
  * `review_locus`  -- one locus, synchronous, uses messages.parse (dev / demo).
  * `submit_batch` / `collect_batch` -- many loci via the Batches API (50%
    cheaper, async) for a full benchmark run.

API specifics are pinned to Opus 4.8: adaptive thinking + effort, structured
output, prompt caching on the stable system prompt. No temperature, no
budget_tokens (both 400 on this model).
"""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from typing import Iterable

import anthropic

from . import config
from .schema import EvidencePacket, ReviewedLocus, SVVerdict


def batch_custom_id(locus_id: str) -> str:
    """Sanitize one locus_id to the Batch API pattern ^[a-zA-Z0-9_-]{1,64}$
    (locus_ids contain ':', e.g. 'svim:FP:chr21:13017861:INS')."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", locus_id)[:64]


def batch_ids(packets) -> list[str]:
    """Unique, API-valid custom_ids for a batch, in packet order. locus_ids can
    collide when a caller emits two calls at the same position/type, so append a
    disambiguating suffix to duplicates. Must be called identically on both the
    submit side and the collect side so ids map back to the right packet."""
    ids, seen = [], {}
    for p in packets:
        base = batch_custom_id(p.locus_id)[:60]
        n = seen.get(base, 0)
        seen[base] = n + 1
        ids.append(base if n == 0 else f"{base}_{n}")
    return ids

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are a genomics expert reviewing why a structural-variant (SV) caller \
disagrees with the GIAB HG002 gold-standard truth set. You are given, for one \
locus: (1) a samplot read-alignment image showing read depth, split reads, and \
discordant read pairs across the region, and (2) a structured evidence packet \
with the caller's call, Truvari's label (FP = caller call with no truth match, \
FN = truth call the caller missed), and genomic-context flags.

Reason over BOTH the image and the packet. Decide which of these the locus is:
  - true_positive: a real variant, correctly represented by the caller
  - false_positive: the caller reported a variant the alignment evidence does not support
  - false_negative: a real variant the caller missed (alignment evidence supports it)
  - benchmark_artifact: the call is essentially correct but Truvari flagged it \
because of a REPRESENTATION difference (shifted breakpoint, split/merged event, \
or a call inside a tandem repeat / segmental duplication / low-mappability region \
where placement is ambiguous). This is NOT a caller error.
  - uncertain: the evidence genuinely does not support a confident call

Per-SV-type visual signatures (read the image with the right expectation):
  - DEL (deletion): coverage drops toward ~0 across the interval, with split \
reads / spanning-read gaps at both breakpoints. Heterozygous events drop on one \
haplotype only.
  - INS (insertion): NO depth drop. Look instead for a localized cluster of \
soft-clipped reads, split reads, and (for long reads) reads carrying extra \
inserted sequence at a single breakpoint. Coverage may bump slightly at the site.
  - DUP (duplication): a localized INCREASE in read depth over the duplicated \
interval, sometimes with discordant/split reads at the boundaries.

Guidance:
  - Read the image first, matching the expected signature for the SV type above.
  - A call sitting in a tandem repeat / segdup / low-mappability region, close \
to a truth call of the same type, is very often a benchmark_artifact rather than \
a true error -- say so when the evidence fits. This is especially common for INS \
inside tandem repeats, where inserted-sequence length is inherently ambiguous.
  - POPULATION EVIDENCE (packet field `population_known_sv`): if a structurally \
matching SV is already catalogued in gnomAD-SV / dbVar / DGV / HGSVC, a real SV \
is known to recur at this locus -- this CORROBORATES benchmark_artifact (or \
true_positive) over a genuine caller error, and should RAISE your confidence, \
especially when the read signature already fits. A high population allele \
frequency (max_pop_AF) is stronger still. This is asymmetric: absence of a \
catalog match is NEUTRAL (these catalogs are incomplete and sparse in exactly \
these repeat regions) -- never treat 'none found' as evidence the call is false. \
When a catalog match materially supported your verdict, include \
'population_support' in `evidence_used`.
  - Only cite evidence you can actually point to in the image or packet.
  - Prefer "uncertain" over a confident guess when the image is inconclusive.

Return ONLY the structured verdict.
"""

# Truth-free QC mode: no benchmark, no truth set. Judge a raw callset on the
# alignment evidence alone. Used to run SVBench AI on any genome (e.g. a sample
# with no gold-standard truth).
QC_SYSTEM_PROMPT = """\
You are a genomics expert doing quality control on a structural-variant (SV) \
caller's output for a sample that has NO truth set. For one call you are given a \
samplot read-alignment image (read depth, split reads, discordant pairs) and a \
structured packet (SV type, size, genomic-context flags). There is no benchmark \
label -- judge purely from the evidence whether the call is real.

Classify each call as:
  - true_positive: the alignment evidence supports a real variant of the stated type
  - false_positive: the evidence does NOT support the call (likely a caller/alignment artifact)
  - uncertain: evidence is genuinely insufficient to decide

Per-SV-type visual signatures:
  - DEL: coverage drop toward ~0 with split reads at both breakpoints.
  - INS: no depth drop; soft-clip / split / insert-carrying reads at one breakpoint.
  - DUP: localized depth increase over the interval.

Guidance:
  - Calls in tandem-repeat / segdup / low-mappability regions with weak or \
ambiguous read support are common false positives -- but a clear signature there \
is still real; weigh the actual evidence.
  - POPULATION EVIDENCE (packet field `population_known_sv`): a structurally \
matching SV catalogued in gnomAD-SV / dbVar / DGV / HGSVC means a real SV recurs \
at this locus in humans -- this supports true_positive and should RAISE \
confidence when the read signature is consistent. It is asymmetric: 'none found' \
is NEUTRAL (incomplete catalogs), never evidence the call is false. Cite \
'population_support' in `evidence_used` when a match supported your verdict.
  - Only cite evidence you can point to. Prefer "uncertain" when inconclusive.
  - Do NOT use the classes false_negative or benchmark_artifact (there is no truth set).

Return ONLY the structured verdict.
"""


# Appended when a trio (child + both parents) image is provided. Mendelian
# inheritance is an orthogonal, truth-independent validator.
TRIO_ADDENDUM = """\

TRIO / MENDELIAN EVIDENCE: The image shows THREE stacked samples in this order \
-- CHILD (top), FATHER (middle), MOTHER (bottom). Use inheritance to decide:
  - If the variant's signature (e.g. a DEL depth-drop, or INS soft-clip cluster) \
is visible in the CHILD and in AT LEAST ONE PARENT, the variant is INHERITED and \
therefore almost certainly REAL -- this strongly supports true_positive (or \
benchmark_artifact if it's a real event Truvari mislabeled), NOT false_positive.
  - If it is clearly present in the child but ABSENT in BOTH parents, it is \
either a rare de-novo event or an artifact -- be cautious, lower confidence, and \
say which you think it is.
  - State the inheritance pattern explicitly in `explanation`, and include \
'mendelian_inheritance' (and 'parental_support' or 'de_novo' as appropriate) in \
`evidence_used`.
"""


def _system_blocks(mode: str = "benchmark", trio: bool = False) -> list[dict]:
    """System prompt with a cache breakpoint so the (stable) rubric is billed
    once per 5-minute window across a run. mode='qc' uses the truth-free rubric;
    trio=True appends the Mendelian-inheritance guidance."""
    prompt = QC_SYSTEM_PROMPT if mode == "qc" else SYSTEM_PROMPT
    if trio:
        prompt = prompt + TRIO_ADDENDUM
    return [{"type": "text", "text": prompt, "cache_control": {"type": "ephemeral"}}]


def _image_block(image_path: str | Path) -> dict:
    data = base64.standard_b64encode(Path(image_path).read_bytes()).decode()
    return {
        "type": "image",
        "source": {"type": "base64", "media_type": "image/png", "data": data},
    }


def _user_content(packet: EvidencePacket) -> list[dict]:
    content: list[dict] = []
    if packet.image_path and Path(packet.image_path).exists():
        content.append(_image_block(packet.image_path))
    content.append({
        "type": "text",
        "text": (
            "Review this locus and return a structured verdict.\n\n"
            + packet.as_prompt_block()
        ),
    })
    return content


def _client() -> anthropic.Anthropic:
    # Zero-arg client resolves creds from env / `ant auth` profile.
    return anthropic.Anthropic()


def preview_request(packet: EvidencePacket) -> dict:
    """Assemble (but do NOT send) the request for one locus, for offline
    validation and demoing the prompt without spending credits."""
    content = _user_content(packet)
    img = next((b for b in content if b["type"] == "image"), None)
    return {
        "model": config.MODEL,
        "effort": config.EFFORT,
        "thinking": "adaptive",
        "system_chars": len(SYSTEM_PROMPT),
        "has_image": img is not None,
        "image_b64_len": len(img["source"]["data"]) if img else 0,
        "text_block": content[-1]["text"],
        "output_schema_keys": list(SVVerdict.model_json_schema()["properties"].keys()),
    }


# ---------------------------------------------------------------------------
# Synchronous single-locus review (dev / demo path)
# ---------------------------------------------------------------------------
def review_locus(packet: EvidencePacket, client: anthropic.Anthropic | None = None,
                 mode: str = "benchmark", trio: bool = False) -> ReviewedLocus:
    """Review one locus. Uses messages.create with a combined
    output_config={effort, format} (same shape as the batch path) and validates
    the returned JSON against SVVerdict -- this keeps a single, tested request
    shape across both paths and avoids relying on parse() merging effort +
    output_format. mode='qc' uses the truth-free rubric; trio=True adds Mendelian
    guidance (the image must be a 3-sample trio samplot)."""
    client = client or _client()
    resp = client.messages.create(
        model=config.MODEL,
        max_tokens=config.MAX_TOKENS,
        thinking={"type": "adaptive"},
        output_config={"effort": config.EFFORT, **_output_config_format()},
        system=_system_blocks(mode, trio),
        messages=[{"role": "user", "content": _user_content(packet)}],
    )
    if resp.stop_reason == "refusal":
        verdict = SVVerdict(
            classification="uncertain", confidence=0.0,
            primary_reason="model refused", evidence_used=[],
            explanation="Request was refused by safety classifiers.",
        )
    else:
        text = next((b.text for b in resp.content if b.type == "text"), "{}")
        try:
            verdict = SVVerdict.model_validate_json(text)
        except Exception as exc:  # noqa: BLE001
            verdict = SVVerdict(
                classification="uncertain", confidence=0.0,
                primary_reason="unparseable output", evidence_used=[],
                explanation=f"Could not parse verdict JSON: {exc}",
            )
    return ReviewedLocus(packet=packet, verdict=verdict)


# ---------------------------------------------------------------------------
# Batch review (full benchmark run)
# ---------------------------------------------------------------------------
# Structured outputs don't support these JSON-Schema constraint keywords; the
# parse() helper strips them client-side, but a hand-built schema must too.
# Local pydantic validation still enforces them on the returned JSON.
_UNSUPPORTED_SCHEMA_KEYS = {
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
    "minLength", "maxLength", "pattern", "minItems", "maxItems", "uniqueItems",
}


def _sanitize_schema(node):
    if isinstance(node, dict):
        return {k: _sanitize_schema(v) for k, v in node.items()
                if k not in _UNSUPPORTED_SCHEMA_KEYS}
    if isinstance(node, list):
        return [_sanitize_schema(v) for v in node]
    return node


def _output_config_format() -> dict:
    return {"format": {"type": "json_schema",
                       "schema": _sanitize_schema(SVVerdict.model_json_schema())}}


def submit_batch(packets: Iterable[EvidencePacket], client: anthropic.Anthropic | None = None) -> str:
    """Create a Message Batch, one request per locus. Returns the batch id.

    custom_id is a sanitized, de-duplicated form of packet.locus_id (see
    batch_ids); results (which arrive unordered) join back via the same mapping.
    """
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    client = client or _client()
    packets = list(packets)
    requests = [
        Request(
            custom_id=cid,
            params=MessageCreateParamsNonStreaming(
                model=config.MODEL,
                max_tokens=config.MAX_TOKENS,
                thinking={"type": "adaptive"},
                output_config={"effort": config.EFFORT, **_output_config_format()},
                system=_system_blocks(),
                messages=[{"role": "user", "content": _user_content(p)}],
            ),
        )
        for cid, p in zip(batch_ids(packets), packets)
    ]
    batch = client.messages.batches.create(requests=requests)
    return batch.id


def collect_batch(
    batch_id: str,
    packets_by_id: dict[str, EvidencePacket],
    client: anthropic.Anthropic | None = None,
) -> list[ReviewedLocus]:
    """Fetch a completed batch and join verdicts back to packets by custom_id."""
    client = client or _client()
    reviewed: list[ReviewedLocus] = []
    for result in client.messages.batches.results(batch_id):
        packet = packets_by_id.get(result.custom_id)
        if packet is None:
            continue
        if result.result.type != "succeeded":
            verdict = SVVerdict(
                classification="uncertain", confidence=0.0,
                primary_reason=f"batch result {result.result.type}",
                evidence_used=[], explanation=f"Batch item did not succeed: {result.result.type}.",
            )
        else:
            text = next((b.text for b in result.result.message.content if b.type == "text"), "{}")
            try:
                verdict = SVVerdict.model_validate_json(text)
            except Exception as exc:  # noqa: BLE001
                verdict = SVVerdict(
                    classification="uncertain", confidence=0.0,
                    primary_reason="unparseable batch output",
                    evidence_used=[], explanation=f"Could not parse verdict JSON: {exc}",
                )
        reviewed.append(ReviewedLocus(packet=packet, verdict=verdict))
    return reviewed


def batch_status(batch_id: str, client: anthropic.Anthropic | None = None) -> str:
    client = client or _client()
    return client.messages.batches.retrieve(batch_id).processing_status


def save_reviews(reviewed: list[ReviewedLocus], path: str | Path) -> None:
    Path(path).write_text(
        json.dumps([r.model_dump() for r in reviewed], indent=2)
    )
