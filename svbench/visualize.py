"""Visualization agent -- one samplot PNG per discordant locus.

samplot renders read depth, split reads, and discordant pairs across the SV
region -- exactly the signals Claude needs to adjudicate the call. Deterministic;
no model calls. Sets `packet.image_path` in place.
"""
from __future__ import annotations

import sys
from pathlib import Path

from . import config
from .schema import EvidencePacket
from .shell import require, run

# samplot -t expects one of these; map anything else to a plain window.
_SAMPLOT_TYPES = {"DEL", "DUP", "INV", "INS", "BND", "TRA"}


def render_locus(
    packet: EvidencePacket,
    out_dir: Path,
    bam: Path | None = None,
    pad_frac: float = 0.5,
) -> EvidencePacket:
    bam = Path(bam or config.SLICED_BAM)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / f"{packet.locus_id.replace(':', '_')}.png"

    # Reuse an already-rendered image (e.g. after a failed batch submit) instead
    # of re-slicing + re-rendering — samplot is the slow stage.
    if png.exists() and png.stat().st_size > 0:
        packet.image_path = str(png)
        return packet

    require("samplot")
    span = max(packet.end - packet.start, 1)
    pad = int(span * pad_frac) + 200  # context around the event
    start = max(1, packet.start - pad)
    end = packet.end + pad
    svtype = packet.svtype if packet.svtype in _SAMPLOT_TYPES else "DEL"

    # NB: samplot's -T is --transcript_file, NOT a title. It auto-titles from
    # the region; the caller/label context is carried in the report + dashboard.
    cmd = [
        "samplot", "plot",
        "-n", f"HG002 {packet.caller}:{packet.truvari_label}",
        "-b", str(bam),
        "-o", str(png),
        "-c", packet.chrom,
        "-s", str(start),
        "-e", str(end),
        "-t", svtype,
        "-W", "18", "-H", "6",  # wider figure -> larger, more legible plot
    ]
    try:
        run(cmd, stdout=sys.stderr, stderr=sys.stderr)
        packet.image_path = str(png)
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] samplot failed for {packet.locus_id}: {exc}", file=sys.stderr)
        packet.image_path = None
    return packet


def render_all(
    packets: list[EvidencePacket],
    out_dir: Path,
    bam: Path | None = None,
) -> list[EvidencePacket]:
    out = [render_locus(p, out_dir, bam=bam) for p in packets]
    ok = sum(1 for p in out if p.image_path)
    print(f"[visualize] rendered {ok}/{len(out)} images", file=sys.stderr)
    return out


def render_locus_trio(
    packet: EvidencePacket,
    out_dir: Path,
    child_bam: Path,
    father_bam: Path,
    mother_bam: Path,
    labels: tuple[str, str, str] = ("child", "father", "mother"),
    pad_frac: float = 0.5,
) -> EvidencePacket:
    """Render a 3-sample samplot (child + father + mother stacked) so the model
    can assess Mendelian inheritance at the locus."""
    require("samplot")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / f"{packet.locus_id.replace(':', '_')}_trio.png"
    span = max(packet.end - packet.start, 1)
    pad = int(span * pad_frac) + 200
    start = max(1, packet.start - pad)
    end = packet.end + pad
    svtype = packet.svtype if packet.svtype in _SAMPLOT_TYPES else "DEL"
    cmd = [
        "samplot", "plot",
        "-n", labels[0], labels[1], labels[2],
        "-b", str(child_bam), str(father_bam), str(mother_bam),
        "-o", str(png),
        "-c", packet.chrom, "-s", str(start), "-e", str(end), "-t", svtype,
        "-W", "18", "-H", "9",  # wider + taller (3 stacked samples)
    ]
    try:
        run(cmd, stdout=sys.stderr, stderr=sys.stderr)
        packet.image_path = str(png)
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] trio samplot failed for {packet.locus_id}: {exc}", file=sys.stderr)
        packet.image_path = None
    return packet
