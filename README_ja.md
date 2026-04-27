#日本語LLM要約のFaithfulness評価データセット

LLMによる日本語要約のHallucination検出のための評価データセットです。文単位のFaithfulnessアノテーションを含みます。

詳細は以下の論文を参照してください：
> Hikari Tanaka, Atsushi Keyaki, and Mamoru Komachi. 2026. [Constructing a Dataset for Hallucination Detection in Japanese Summarization with Fine-grained Faithfulness Labels](https://aclanthology.org/2026.eacl-srw.15/). In *Proceedings of the 19th Conference of the European Chapter of the Association for Computational Linguistics (Volume 4: Student Research Workshop)*, pages 207–218, Rabat, Morocco. Association for Computational Linguistics.

*[English README → README.md](README.md)*

---

## 概要

本データセットは以下の3要素で構成されます：
- 日本語ニュース記事（入力文書）
- 3種類のLLMによって生成された要約
- 人手による文単位のFaithfulnessアノテーション

各要約文に対して、入力文書との整合性（Faithfulness）の観点からHallucinationが含まれるかどうかのラベルが付与されています。

---

## データセット統計

| 項目 | 件数 |
|------|------|
| 記事数 | 130 |
| 要約数（example数） | 390 |
| 要約文数 | 1,949 |

**モデル別example数：**

| モデル | 件数 |
|--------|------|
| GPT-4o | 130 (33.3%) |
| Swallow | 130 (33.3%) |
| LLM-jp | 130 (33.3%) |

**`hallucination_present`の分布：**

| ラベル | 件数 | % |
|--------|------|---|
| `faithful` | 220 | 56.4% |
| `hallucinated` | 148 | 37.9% |
| `paraphrase_error_only` | 22 | 5.6% |

**文レベル`hallucination_type`の分布：**

| ラベル | 件数 | % |
|--------|------|---|
| `Not-hallucination` | 1,512 | 77.6% |
| `Unresolved-Single` | 163 | 8.4% |
| `Intrinsic Hallucination` | 130 | 6.7% |
| `Extrinsic Hallucination` | 49 | 2.5% |
| `Paraphrase Error` | 45 | 2.3% |
| `Unresolved-Disagreement` | 39 | 2.0% |
| `Mixed` | 11 | 0.6% |

---

## データ形式

JSONLファイルで配布されます。1行が1つの要約（example）に対応するJSONオブジェクトです。

### トップレベルフィールド

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `example_id` | string | 主キー。形式：`{input_id:03d}_{model}`（例：`000_GPT-4o`） |
| `input_id` | int | ニュース記事のID |
| `source_url` | string | ニュース記事のURL |
| `source_text` | string | ニュース記事の本文 |
| `model` | string | 要約を生成したLLM（[モデル詳細](#モデル詳細)参照） |
| `summary_text` | string | 要約の全文 |
| `hallucination_present` | string | 要約全体のFaithfulnessラベル（[ラベル定義](#ラベル定義)参照） |
| `annotation_mode` | string | アノテーション方式：`validated`または`independent` |
| `sentences` | list | 文単位のアノテーションオブジェクトのリスト（下記参照） |
| `xlsum_split` | string | XL-Sumにおける元の分割（`train`または`validation`） |
| `xlsum_summary` | string | XL-Sumにおける元の要約文 |

### 文レベルフィールド（`sentences`）

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `sentence_id` | int | 要約内の文のインデックス |
| `text` | string | 文のテキスト |
| `start_char` | int | `summary_text`内の開始文字位置 |
| `end_char` | int | `summary_text`内の終了文字位置 |
| `hallucination_type` | string | 集計済みFaithfulnessラベル（[ラベル定義](#ラベル定義)参照） |
| `votes` | object | 各非Faithfulラベルへの投票数（例：`{"Intrinsic Hallucination": 2}`） |
| `individual_annotations` | list | アノテーター別ラベルのリスト：`{"annotator_id": ..., "label": ...}` |

---

## ラベル定義

### `hallucination_present`（要約レベル）

| ラベル | 説明 |
|--------|------|
| `faithful` | 要約中にUnfaithfulな文が含まれない |
| `hallucinated` | 要約中にHallucinationを含む文が存在する |
| `paraphrase_error_only` | Unfaithfulな文を含むが、すべてParaphrase Errorであり Hallucinationは含まれない |

### `hallucination_type`（文レベル）

集計ルール：
- 6名全員が`Not-hallucination`を付与 → `Not-hallucination`
- 2名以上が非Faithfulラベルを付与し、かつその中で過半数が同一ラベル → そのラベル
- 1名のみ非Faithfulラベルを付与 → `Unresolved-Single`
- 2名以上が非Faithfulラベルを付与したが過半数ラベルなし → `Unresolved-Disagreement`

| ラベル | 説明 |
|--------|------|
| `Not-hallucination` | 全アノテーターがFaithfulと判断した文 |
| `Intrinsic Hallucination` | 入力文書に記載された内容と矛盾する記述を含む文 |
| `Extrinsic Hallucination` | 入力文書に存在しない情報を含む文 |
| `Paraphrase Error` | 言い換えによって意味が歪められた文。Faithfulnessの観点では不適切だが、厳密なHallucinationとは区別される |
| `Mixed` | 複数種類の非Faithfulエラーを含む文 |
| `Unresolved-Single` | 1名のみが非Faithfulと判断。ラベル未決定 |
| `Unresolved-Disagreement` | 複数名が非Faithfulと判断したが、過半数ラベルに至らず。ラベル未決定 |

---

## モデル詳細

| データセット上のモデル名 | モデル |
|--------------------------|--------|
| `GPT-4o` | [GPT-4o](https://developers.openai.com/api/docs/models/gpt-4o) |
| `Swallow` | [Swallow](https://huggingface.co/tokyotech-llm/Llama-3.1-Swallow-8B-Instruct-v0.2) |
| `LLM-jp` | [LLM-jp](https://huggingface.co/llm-jp/llm-jp-3-13b-instruct) |

---

## 使用例

### データセットの読み込み

```python
import json

def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

dataset = load_jsonl("dataset.jsonl")
```

### モデルでフィルタリング

```python
gpt4o_examples = [ex for ex in dataset if ex["model"] == "GPT-4o"]
```

### `hallucination_present`を二値ラベルとして使用

`paraphrase_error_only`をFaithful・Unfaithfulのどちらに倒すかは、タスクの定義に応じて選択できます：

```python
def to_binary(ex, paraphrase_as_unfaithful=True):
    label = ex["hallucination_present"]
    if label == "faithful":
        return 0
    elif label == "hallucinated":
        return 1
    else:  # paraphrase_error_only
        return 1 if paraphrase_as_unfaithful else 0

# paraphrase_error_onlyをUnfaithfulとして扱う場合
labels = [to_binary(ex, paraphrase_as_unfaithful=True) for ex in dataset]

# paraphrase_error_onlyをFaithfulとして扱う場合
labels = [to_binary(ex, paraphrase_as_unfaithful=False) for ex in dataset]
```

### 文レベルのアノテーションを独自ルールで集計

`individual_annotations`フィールドを用いて、集計ルールを変えることができます：

```python
from collections import Counter

def custom_aggregate(sentence, min_votes=2):
    """非Faithfulラベルにmin_votes名以上が投票した場合にそのラベルを採用する"""
    labels = [ann["label"] for ann in sentence["individual_annotations"]]
    if not labels:
        return "Not-hallucination"
    counter = Counter(labels)
    most_common_label, count = counter.most_common(1)[0]
    if count >= min_votes:
        return most_common_label
    return "Unresolved"
```

---

## ライセンス / License

本リポジトリは [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/) のもとで公開されています。

**著作権について**
- アノテーションデータおよび周辺コード（`utils.py`等）の著作権は著者らに帰属します。
- ニュース記事は [XL-Sum](https://github.com/csebuetnlp/xl-sum)（CC BY-NC-SA 4.0）を元にしており、記事内容の著作権は各著作権者に帰属します。
- LLMによる要約文については著作権を主張しません。
---

## 引用

本データセットを使用する場合は、以下の論文を引用してください：

```bibtex
@inproceedings{tanaka-etal-2026-constructing,
    title = "Constructing a Dataset for Hallucination Detection in {J}apanese Summarization with Fine-grained Faithfulness Labels",
    author = "Tanaka, Hikari  and
      Keyaki, Atsushi  and
      Komachi, Mamoru",
    booktitle = "Proceedings of the 19th Conference of the {E}uropean Chapter of the {A}ssociation for {C}omputational {L}inguistics (Volume 4: Student Research Workshop)",
    month = mar,
    year = "2026",
    address = "Rabat, Morocco",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2026.eacl-srw.15/",
    doi = "10.18653/v1/2026.eacl-srw.15",
    pages = "207--218",
}
```

ニュース記事を使用する場合は、XL-Sumも合わせて引用してください：

```bibtex
@inproceedings{hasan-etal-2021-xl,
    title = "{XL}-Sum: Large-Scale Multilingual Abstractive Summarization for 44 Languages",
    author = "Hasan, Tahmid  and
      Bhattacharjee, Abhik  and
      Islam, Md. Saiful  and
      Mubasshir, Kazi  and
      Li, Yuan-Fang  and
      Kang, Yong-Bin  and
      Rahman, M. Sohel  and
      Shahriyar, Rifat",
    booktitle = "Findings of the Association for Computational Linguistics: ACL-IJCNLP 2021",
    month = aug,
    year = "2021",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2021.findings-acl.82",
    doi = "10.18653/v1/2021.findings-acl.82",
    pages = "4693--4703",
}
```
