from dataclasses import dataclass
from pathlib import Path

from Bio import SeqIO


@dataclass(frozen=True)
class DNAAnalysisResult:
    sequence_length: int
    gc_content: float


def analyze_fasta(file_path: Path) -> DNAAnalysisResult:
    records = SeqIO.parse(str(file_path), "fasta")
    total_length = 0
    gc_count = 0
    record_count = 0

    for record in records:
        sequence = str(record.seq).upper()
        if not sequence:
            continue
        if set(sequence) - set("ACGTN"):
            raise ValueError(
                f"Последовательность {record.id} содержит недопустимые символы"
            )
        record_count += 1
        total_length += len(sequence)
        gc_count += sequence.count("G") + sequence.count("C")

    if record_count == 0 or total_length == 0:
        raise ValueError("FASTA-файл не содержит непустых DNA-последовательностей")

    return DNAAnalysisResult(
        sequence_length=total_length,
        gc_content=gc_count * 100.0 / total_length,
    )