"""
提示词加载：主 Prompt / RAG / Skill（仅从项目 prompts 文件读取）
"""
from utils.config_handler import prompts_config
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


def load_system_prompts() -> str:
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
    try:
        return load_skill_prompt("weekly_review")
    except Exception:
        path = get_abs_path(prompts_config.get("report_prompt_path", "prompts/skills/weekly_review.txt"))
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


def load_skill_prompt(skill_name: str) -> str:
    skills_dir = prompts_config.get("skills_dir", "prompts/skills")
    path = get_abs_path(f"{skills_dir}/{skill_name}.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error("[load_skill_prompt]无法加载 skill=%s: %s", skill_name, e)
        raise e
