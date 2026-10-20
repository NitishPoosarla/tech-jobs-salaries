"""08-technology-jobs — download the ds_salaries dataset (public mirror).

Source: Kaggle "Data Science Salaries 2020-2024" mirrored on GitHub; 12 columns
(experience level, role, remote ratio, company location, salaries in USD).
"""
from pathlib import Path
import sys

_shared_root = Path(__file__).resolve().parent
while _shared_root != _shared_root.parent and not (_shared_root / "shared").is_dir():
    _shared_root = _shared_root.parent
sys.path.insert(0, str(_shared_root))  # callable from repo root or standalone checkout
from shared.utils import download   # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
URL = ("https://raw.githubusercontent.com/YuluDuan/Hypothesis-Testing-Data-Science-"
       "salary-comparison-in-different-location/main/ds_salaries.csv")


def main() -> None:
    (PROJECT / "data" / "raw").mkdir(parents=True, exist_ok=True)
    download(URL, PROJECT / "data" / "raw" / "ds_salaries.csv", "ds_salaries")


if __name__ == "__main__":
    main()
