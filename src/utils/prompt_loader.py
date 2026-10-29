"""
从磁盘加载 Prompt 文本。路径来自 config/prompts.yml，禁止把用户输入当系统提示。
"""
from utils.config_handler import prompts_config
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


def load_rag_prompts() -> str:
    """读取 RAG 总结 Prompt（由 RagSummarizeService 填入检索片段）。"""
    try:
        path = get_abs_path(prompts_config["rag_summarize_prompt_path"])
    except KeyError as e:
        logger.error("[load_rag_prompts]缺少 rag_summarize_prompt_path")
        raise e
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error("[load_rag_prompts]读取失败：%s", e)
        raise e
