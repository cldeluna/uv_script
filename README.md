
# Standalone UV Script

Companion Repository for Ultra Valuable UV


```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv --version

```
```
cd <unzipped or cloned directory for this repository
ls -al
uv --version
uv run cc3_info.py

```



```bash
uv add --script cc3_info.py --python 3.11 requests pycountry python-dotenv

% uv sync --script cc3_info.py 
Using script environment at: /Users/claudiadeluna/.cache/uv/environments-v2/cc3-info-1b81c18f915397c7
Resolved 7 packages in 157ms
Audited 7 packages in 0.04ms


```