# python-dotenv-fixed

> [!IMPORTANT]
> 本家 [python-dotenv](https://github.com/theskumar/python-dotenv) では
> `load_dotenv(dotenv_path=Path("../.env"))` のように相対パスを渡すと、
> **コマンドを実行したカレントディレクトリ** を基準に解決されてしまいます。
> このパッケージは本家 python-dotenv をそのまま使いつつ、`dotenv_fixed_path` という引数を追加して
> **`load_dotenv()` を呼び出したファイルのあるディレクトリ** を基準にパスを解決できるようにしたものです。
>
> In upstream python-dotenv a relative `dotenv_path` is resolved against the current
> working directory. This add-on keeps using the official python-dotenv and adds a
> `dotenv_fixed_path` argument that is resolved against the directory of the calling file.

## インストール / Install

```sh
pip install git+https://github.com/Okaz02/python-dotenv.git
```

本家の `python-dotenv` は依存パッケージとして PyPI から自動でインストールされます。
本家の更新は `pip install -U python-dotenv` でそのまま取り込めます。

## 使い方 / Usage

```
project/
├── .env
└── src/
    └── app.py
```

```python
# src/app.py
from pathlib import Path

from dotenv_fixed import load_dotenv

load_dotenv(dotenv_fixed_path=Path("../.env"))  # always project/.env
```

`python src/app.py` でも `cd src && python app.py` でも、同じ `project/.env` が読み込まれます。

- `load_dotenv()` と `dotenv_values()` が `dotenv_fixed_path` に対応しています。
  それ以外の引数 (`override`, `encoding` など) は本家にそのまま渡されます。
- `dotenv_fixed_path` を指定しなければ、本家の `load_dotenv()` / `dotenv_values()` と完全に同じ動作です。
- `dotenv_path` と `dotenv_fixed_path` を同時に指定すると `TypeError` になります。
- 絶対パスはそのまま使われます。REPL / IPython / `python -c` など呼び出し元ファイルがない場合は、
  カレントディレクトリが基準になります。
- 他の関数 (`find_dotenv`, `set_key` など) は本家の `dotenv` から直接 import してください。

## License

BSD-3-Clause (same as python-dotenv).
