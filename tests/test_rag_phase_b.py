"""阶段 B：kb 元数据、增量 hash、md 加载、collection 命名。"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)


def test_collection_naming():
    from rag.vector_store import collection_name_for_personal, collection_name_for_sample

    assert collection_name_for_sample()
    assert "personal" in collection_name_for_personal(7) or collection_name_for_personal(7).endswith("7")


def test_kb_meta_bump(tmp_path, monkeypatch):
    import services.storage as storage
    from rag import kb_meta

    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "kb.db"))
    storage.ensure_db()
    assert kb_meta.get_kb_version("sample") == "0"
    v1 = kb_meta.bump_kb_version("sample")
    assert v1 == "1"
    assert kb_meta.get_kb_version("sample") == "1"
    kb_meta.upsert_kb_file(scope="sample", path="data/sample/a.txt", content_hash="abc", chunk_count=3)
    assert kb_meta.get_kb_file_hash("sample", "data/sample/a.txt") == "abc"


def test_md_loader(tmp_path):
    from utils.file_handler import md_loader

    p = tmp_path / "note.md"
    p.write_text("# 标题\n\n正文内容番茄", encoding="utf-8")
    docs = md_loader(str(p))
    assert docs
    assert "番茄" in docs[0].page_content


def test_pdf_loader_optional_password_signature():
    import inspect
    from utils.file_handler import pdf_loader

    sig = inspect.signature(pdf_loader)
    assert "password" in sig.parameters
    assert sig.parameters["password"].default is None


def test_ingest_cli_help():
    from rag.ingest import main
    import pytest

    with pytest.raises(SystemExit) as ei:
        main(["--help"])
    assert ei.value.code == 0
