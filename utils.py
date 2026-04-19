"""
JaFaithSum - Utility functions
"""

import json
from collections import Counter


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_jsonl(path: str) -> list[dict]:
    """Load a JSONL file and return a list of records."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def filter_by_model(dataset: list[dict], model: str) -> list[dict]:
    """Return examples for a specific model (e.g., 'GPT-4o', 'Swallow', 'LLM-jp')."""
    return [ex for ex in dataset if ex["model"] == model]


def filter_by_annotation_mode(dataset: list[dict], mode: str) -> list[dict]:
    """Return examples with a specific annotation mode ('validated' or 'independent')."""
    return [ex for ex in dataset if ex["annotation_mode"] == mode]


# ---------------------------------------------------------------------------
# Summary-level label conversion
# ---------------------------------------------------------------------------

def to_binary_label(example: dict, paraphrase_as_unfaithful: bool = True) -> int:
    """
    Convert hallucination_present to a binary label (0: faithful, 1: unfaithful).

    Args:
        example: A dataset record.
        paraphrase_as_unfaithful: If True, treat 'paraphrase_error_only' as unfaithful (1).
                                  If False, treat it as faithful (0).

    Returns:
        0 (faithful) or 1 (unfaithful)
    """
    label = example["hallucination_present"]
    if label == "faithful":
        return 0
    elif label == "hallucinated":
        return 1
    else:  # paraphrase_error_only
        return 1 if paraphrase_as_unfaithful else 0


def get_binary_labels(dataset: list[dict], paraphrase_as_unfaithful: bool = True) -> list[int]:
    """
    Convert hallucination_present to binary labels for all examples.

    Args:
        dataset: List of dataset records.
        paraphrase_as_unfaithful: How to treat 'paraphrase_error_only'.

    Returns:
        List of binary labels (0 or 1).
    """
    return [to_binary_label(ex, paraphrase_as_unfaithful) for ex in dataset]


# ---------------------------------------------------------------------------
# Sentence-level annotation aggregation
# ---------------------------------------------------------------------------

def aggregate_sentence(sentence: dict, min_votes: int = 2) -> str:
    """
    Aggregate individual annotations for a sentence using a custom rule.

    The default rule (min_votes=2) matches the aggregation used in the dataset:
    - If no non-faithful labels: 'Not-hallucination'
    - If a label receives >= min_votes: that label (majority among non-faithful voters)
    - Otherwise: 'Unresolved'

    Args:
        sentence: A sentence object from the 'sentences' list.
        min_votes: Minimum number of annotators required to assign a label.

    Returns:
        Aggregated label string.
    """
    labels = [ann["label"] for ann in sentence.get("individual_annotations", [])]
    if not labels:
        return "Not-hallucination"
    counter = Counter(labels)
    most_common_label, count = counter.most_common(1)[0]
    if count >= min_votes:
        return most_common_label
    return "Unresolved"


def reaggregate_dataset(dataset: list[dict], min_votes: int = 2) -> list[dict]:
    """
    Re-aggregate sentence-level labels for all examples using a custom rule.
    Returns a new dataset with updated 'hallucination_type' fields.

    Args:
        dataset: List of dataset records.
        min_votes: Minimum votes required to assign a non-faithful label.

    Returns:
        New list of records with updated sentence-level labels.
    """
    import copy
    result = copy.deepcopy(dataset)
    for ex in result:
        for sent in ex.get("sentences", []):
            sent["hallucination_type"] = aggregate_sentence(sent, min_votes=min_votes)
    return result


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "dataset.jsonl"
    dataset = load_jsonl(path)
    print(f"Loaded {len(dataset)} examples.")

    # Filter by model
    gpt4o = filter_by_model(dataset, "GPT-4o")
    print(f"GPT-4o examples: {len(gpt4o)}")

    # Binary labels (paraphrase_error_only as unfaithful)
    labels_strict = get_binary_labels(dataset, paraphrase_as_unfaithful=True)
    print(f"Unfaithful (strict): {sum(labels_strict)} / {len(labels_strict)}")

    # Binary labels (paraphrase_error_only as faithful)
    labels_lenient = get_binary_labels(dataset, paraphrase_as_unfaithful=False)
    print(f"Unfaithful (lenient): {sum(labels_lenient)} / {len(labels_lenient)}")

    # Re-aggregate with stricter rule (unanimous = 6 votes)
    reaggregated = reaggregate_dataset(dataset, min_votes=6)
    all_sentences = [s for ex in reaggregated for s in ex["sentences"]]
    label_dist = Counter(s["hallucination_type"] for s in all_sentences)
    print(f"\nSentence label distribution (min_votes=6):")
    for label, count in label_dist.most_common():
        print(f"  {label}: {count}")
