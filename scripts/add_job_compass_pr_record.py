"""
追加job compass pr信息的逻辑
1. 接收封装好的json数据(pr信息)
2. 找到对应日期的json文件，如果文件不存在则创建一个空的文件
3. 追加写入json数据
"""

import sys
import json
import logging
import argparse
from datetime import datetime
from scripts.utils.path_utils import get_project_root
from scripts.utils.date_utils import get_current_month
from scripts.utils.github_utils import (
    github_login,
    checkout_branch,
    pull_latest,
    create_branch,
    create_pr,
    delete_branch
)

# 获取项目根目录
PROJECT_ROOT = get_project_root()

# 设置pr写入文件路径
PR_FILE_DIR = PROJECT_ROOT / "docs/assets/json/pr-json"

def find_pr_json_file():
    """
    在/docs/assets/json/pr-json目录下查找当前日期的json文件
    如果没有，则创建对应文件
    :return: 文件路径
    """
    logging.info("开始查找目标PR数据文件")
    pr_date = get_current_month()
    file_name = f"pr-{pr_date}.json"
    file_path = PR_FILE_DIR / file_name

    # 如果文件不存在，初始化为空数组
    if not file_path.exists():
        logging.info(f"目标pr文件未找到，创建新的文件: {file_name}")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    return file_path

def add_pr_record_to_json_file(pr_file_path, pr_data):
    """
    将pr记录追加到json文件中
    :param pr_file_path: 文件路径
    :param pr_data: 待写入的数据
    """
    logging.info(f"开始追加pr数据，ID：#{pr_data['id']}")
    # 打开目标文件
    with open(pr_file_path, "r", encoding="utf-8") as f:
        pr_list = json.load(f)

    # 追加新的pr
    pr_list.append(pr_data)

    # 写回文件
    with open(pr_file_path, "w", encoding="utf-8") as f:
        json.dump(pr_list, f, ensure_ascii=False, indent=2)

    logging.info("pr数据成功添加")

def main():
    # 利用argparse接收参数，指定接收tag为pr_json的参数值
    parser = argparse.ArgumentParser(description="Process pr JSON data.")
    parser.add_argument(
        "--pr_json",
        required=True,
        help="The PR JSON object as a string"
    )

    args = parser.parse_args()

    # 解析参数中的json对象
    try:
        pr_data = json.loads(args.pr_json)
    except json.JSONDecodeError as e:
        logging.error(f"参数解析失败: 不是有效的JSON对象 -> {e}")
        return 1

    # 登录github
    github_login()

    # 切换到main分支并拉取最新代码
    main_branch = "main"
    checkout_branch(main_branch)
    pull_latest()

    # 创建新分支，添加时间戳防止分支名称重复
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_branch_name = f"job-compass-pr-record-{timestamp}"
    create_branch(new_branch_name)

    # 加载目标文件
    pr_file_path = find_pr_json_file()

    # 写入pr数据
    add_pr_record_to_json_file(pr_file_path, pr_data)

    # 发布pr
    title = f"添加pr记录-{pr_data['title']}"
    body = f"**pr作者:** {pr_data['author']}\n**pr链接:** [{pr_data['title']}]({pr_data['link']})"
    create_pr(new_branch_name, title, body)

    # 切换回main分支并删除本地分支
    checkout_branch(main_branch)
    delete_branch(new_branch_name)

    return 0


if __name__ == "__main__":
    sys.exit(main())