from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / 'assets'
DATA_DIR = ASSETS_DIR / 'data'
DOCS_DIR = ASSETS_DIR / 'docs'
RESULTS_DIR = BASE_DIR / 'results'

MK_FILE = DATA_DIR / 'МК.dat'
DRIFT_FILE = DATA_DIR / 'Дрейф.dat'