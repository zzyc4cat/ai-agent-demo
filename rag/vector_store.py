"""
向量工具类
"""
import os
from os import read
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from model.factory import embedding_model
from utils.path_tool import get_abs_path
from utils.file_handler import *
from utils.config_handler import chroma_config
from utils.logger_handler import logger

class VectorStoreService:
    """向量存储类"""
    def __init__(self):
        """向量存储实例"""
        # 加载已有持久化向量库
        self.vector_store = Chroma(
            collection_name=chroma_config["collection_name"],                   # 集合名称
            embedding_function=embedding_model,                                 # 模型实例
            persist_directory=get_abs_path(chroma_config["persist_directory"])) # 本地持久化文件夹路径

        # 递归字符分割器，用于把长文档切分成块，之后存入 Chroma 向量库
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_config["chunk_size"],         # 每个文本块最大字符数
            chunk_overlap=chroma_config["chunk_overlap"],   # 块与块之间重叠字符
            separators=chroma_config["separators"],         # 递归分割符列表，优先级从高到低
            length_function=len)                            # 计算块大小的函数；默认 len，统计字符数

    def get_retriever(self):
        """"""
        return self.vector_store.as_retriever(
            search_type="similarity",                       # 检索模式：默认
            search_kwargs = {"k": chroma_config["k"]})      # 检索参数

    def load_document(self):
        """
        从数据文件夹内读取数据文件，转为向量存入向量库
        要计算文件的MD5值去重
        """
        files=[]
        md5_file_path=get_abs_path(chroma_config["md5_hex_store"])

        def check_md5_hex(md5_for_check:str):
            """检查文件重复性（MD5）"""
            if not os.path.exists(md5_file_path):
                open(md5_file_path, "w", encoding="utf-8").close()   # 创建文件
                return False    # md5 没处理过

            with open(md5_file_path, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True     # md5 处理过

            return False

        def save_md5_hex(md5_for_check:str):
            """添加文件（md5）"""
            with open(md5_file_path, "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")

        def get_file_documents(read_path:str):
            """
            加载文档
            :param read_path:文件路径
            :return:list[Document]
            """
            if read_path.endswith(".txt"):
                return txt_loader(read_path)

            if read_path.endswith(".pdf"):
                return pdf_loader(read_path)

            return []

        allowed_files_path=listdir_with_allowed_type(
            get_abs_path(chroma_config["data_path"]),
            tuple(chroma_config["allow_konwledge_file_type"]),)

        for path in allowed_files_path:
            # 获取文件的md5
            md5_hex = get_file_md5_hex(path)
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]{path} 内容已经存在知识库内，跳过")
                continue

            try:
                documents: list[Document] = get_file_documents(path)

                if not documents:
                    logger.warning(f"[加载知识库]{path} 内没有有效文本内容，跳过")
                    continue

                split_document: list[Document] = self.spliter.split_documents(documents)

                if not split_document:
                    logger.warning(f"[加载知识库]{path} 分片后没有有效文本内容，跳过")
                    continue

                # 将内容存入向量库
                self.vector_store.add_documents(split_document)

                # 记录这个已经处理好的文件的md5，避免下次重复加载
                save_md5_hex(md5_hex)

                logger.info(f"[加载知识库]{path} 内容加载成功")
            except Exception as e:
                # exc_info 为 Ture 会记录详细的报错堆栈，如果为 False 仅记录报错信息本身
                logger.error(f"[加载知识库]{path} 内容加载失败：{str(e)}", exc_info=True)
