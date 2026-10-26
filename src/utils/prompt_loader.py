"""
从磁盘加载 Prompt 文本。路径来自 config/prompts.yml，禁止把用户输入当系统提示。

- load_system_prompts：默认助手（prompts/main_prompt.txt）
- load_rag_prompts：RAG 总结模板（含 {input} {context}）
- load_skill_prompt：prompts/skills/{skill_name}.txt（由 middleware 白名单约束）
- load_report_prompts：兼容旧「周报」入口，等价 weekly_review
"""
from utils.config_handler import prompts_config
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


def load_system_prompts() -> str:
    """读取主系统提示词；缺配置或缺文件则抛错，避免静默空 Prompt。"""
    try:
        path = get_abs_path(prompts_config["main_prompt_path"])
    except KeyError as e:
        logger.error("[load_system_prompts]缺少 main_prompt_path")
        raise e
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error("[load_system_prompts]读取失败：%s", e)
        raise e


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


def load_report_prompts() -> str:
    """旧接口：周报复盘技能 Prompt。"""
    try:
        return load_skill_prompt("weekly_review")
    except Exception:
        path = get_abs_path(prompts_config.get("report_prompt_path", "prompts/skills/weekly_review.txt"))
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


def load_skill_prompt(skill_name: str) -> str:
    """按技能 id 加载对应 txt。调用方必须先做白名单校验，避免路径拼接任意文件。"""
    skills_dir = prompts_config.get("skills_dir", "prompts/skills")
    path = get_abs_path(f"{skills_dir}/{skill_name}.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error("[load_skill_prompt]无法加载 skill=%s: %s", skill_name, e)
        raise e
