Run tests

```bash
pytest tests/ -v
```

Before that make sure to setup a virtual environment. 
```bash
python3 -m venv .venv
source .venv/bin/activate # Linux
.venv/Scripts/activate # Windows
```

Then run

```bash
pip install -e . # in fare_estimator/
```

The -e flag is for automatically including all edits made.