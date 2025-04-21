


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
uv add --script cc3_info.py --python 3.11 requests pycountry
```