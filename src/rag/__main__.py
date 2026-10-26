"""
`python -m rag` 与 `python -m rag.ingest` 的入口转发。

实际参数解析在 rag.ingest.main（--scope sample|personal 等）。
"""
from rag.ingest import main

if __name__ == "__main__":
    raise SystemExit(main())
