# Official Implementation: "The KIP Dataset: Socialist Popular Science in a Sino-Soviet Image Dataset Based on Chinese and Soviet magazines (1956-1962)"

This repository contains the source code for the dataset cleaning and deduplication pipeline used in the paper **"The KIP Dataset: Socialist Popular Science in a Sino-Soviet Image Dataset Based on Chinese and Soviet magazines (1956-1962)"**.

## 📂 Dataset Structure

The script expects the dataset to be organized in a standard class-conditional directory structure (e.g., ImageNet style). It recursively scans all subdirectories.

```text
/path/to/dataset/
├── class_01/
│   ├── image_001.jpg
│   ├── image_002.png
│   └── ...
├── class_02/
│   ├── image_001.jpg
│   └── ...
└── ...

```

## 🛠️ Installation

The code relies on `imagededup` for hash calculation and `tqdm` for progress tracking.

```bash
git clone https://github.com/aziksh-ospanov/kip_dataset_scripts.git
cd kip_dataset_scripts

pip install imagededup tqdm

```

## 🚀 Usage

The script `dedup.py` serves as the main entry point. It supports multiple hashing algorithms (`phash`, `dhash`, `whash`, `ahash`) and adjustable sensitivity thresholds.

### 1. Audit (Dry Run)

We recommend running an audit first to visualize how many duplicates are detected without modifying the data.

```bash
python dedup.py --input_dir ./data/my_dataset --threshold 10

```

### 2. Cleaning (Remove Duplicates)

To replicate the cleaning process described in the paper, run with the `--delete` flag.

```bash
python dedup.py --input_dir ./data/my_dataset --threshold 10 --delete

```

### Arguments

| Argument | Description | Default |
| --- | --- | --- |
| `--input_dir` | Path to the dataset root directory. | **Required** |
| `--method` | Hashing algorithm (`phash`, `dhash`, `whash`, `ahash`). | `phash` |
| `--threshold` | Hamming distance threshold (lower = stricter). | `10` |
| `--delete` | If set, deletes files. Otherwise, lists them (Dry Run). | `False` |

## 📊 Method Details

As detailed in Section 3 of the paper, we utilize **Perceptual Hashing (PHash)**. Unlike cryptographic hashes (MD5/SHA), PHash is robust to minor transformations:

1. Images are resized and converted to grayscale.
2. A Discrete Cosine Transform (DCT) is applied.
3. A hash is generated based on the low-frequency DCT coefficients.
4. Duplicates are identified via Hamming distance (default ).
