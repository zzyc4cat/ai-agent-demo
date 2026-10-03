"""
文件处理工具类
"""
import os
import hashlib
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import  PyPDFLoader, TextLoader

def get_file_md5_hex(filepath:str):
    """获取文件的md5的十六进制字符串，用来做去重判断"""
    if not os.path.isfile(filepath):
        logger.error(f"[md5计算]文件{filepath}不存在")
        return

    if not os.path.isfile(filepath):
        logger.error(f"[md5计算]路径{filepath}不是文件")
        return

    md5_obj=hashlib.md5()

    chunk_size=4096     # 4KB分片，避免文件过大爆内存
    try:
        with open(filepath,'rb') as f:  # 必须二进制读取
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
                """
                chunk = f.read(chunk_size)
                while chunk :
                    md5_obj.update(chunk)
                    chunk = f.read(chunk_size)
                """
            md5_hex=md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
        logger.error(f"计算文件{filepath}md5是吧{str(e)}")


def listdir_with_allowed_type(path: str, allowed_type: tuple[str]):
    """返回文件夹内的文件列表（允许的文件后缀，递归子目录）。"""
    files: list[str] = []
    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type]{path}不是文件夹")
        return tuple()

    suffixes = []
    for s in allowed_type:
        s = str(s).lower().strip()
        if not s:
            continue
        if not s.startswith("."):
            s = "." + s
        suffixes.append(s)
    suffix_tuple = tuple(suffixes)
    if not suffix_tuple:
        return tuple()

    for root, _dirs, names in os.walk(path):
        for name in names:
            if name.lower().endswith(suffix_tuple):
                files.append(os.path.join(root, name))
    return tuple(files)


def pdf_loader(filepath: str, password: str | None = None) -> list[Document]:
    """加载 pdf 文档。"""
    if password:
        return PyPDFLoader(filepath, password=password).load()
    return PyPDFLoader(filepath).load()


def txt_loader(filepath: str) -> list[Document]:
    """加载 txt 文档。"""
    return TextLoader(filepath, encoding="utf-8").load()


def md_loader(filepath: str) -> list[Document]:
    """加载 markdown 文档。"""
    return TextLoader(filepath, encoding="utf-8").load()
