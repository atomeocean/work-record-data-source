from pathlib import Path
from typing import Union, List, Callable, Optional
import logging

def get_project_root(root_depth: int = 2) -> Path:
    """
    根据当前文件获取项目根目录的路径
    Args:
        root_depth: 项目根目录的深度（从scripts/utils/path_utils.py向上追溯到仓库根目录的层级数）

    Returns:
        Path: 项目根目录的路径对象
    """
    return Path(__file__).resolve().parents[root_depth]

def path_exists(path: Union[str, Path]) -> bool:
    """
    验证参数中的路径是否存在
    :param path: 需要验证的路径
    :return: 验证结果
    """
    return Path(path).exists()

def list_all_files(dir_path: Union[str, Path]) -> List[str]:
    """
    获取指定目录下的所有文件名
    :param dir_path: 目标目录路径
    :return: 文件名列表
    """
    path_obj = Path(dir_path)
    # 返回该目录下的所有文件（不含文件夹）
    return [
        f.name for f in path_obj.iterdir()
        if f.is_file()
    ]


def list_files_by_extension(
        dir_path: Union[str, Path],
        extension: str
) -> List[str]:
    """
    获取指定目录下所有指定扩展名的文件名（不包含子目录）
    :param dir_path: 目标目录路径
    :param extension: 文件扩展名（不含.，例如 'json' 或 'txt'）
    :return: 文件名列表
    """
    path_obj = Path(dir_path)
    # 确保扩展名前带点
    ext = extension if extension.startswith(".") else f".{extension}"

    return [
        f.name for f in path_obj.iterdir()
        if f.is_file() and f.suffix == ext
    ]

def read_and_validate_file_path(
        path_builder: Callable[[], Path],
        error_message: Optional[str] = None,
        check_is_file: bool = True
) -> Path:
    """
    通用的文件路径读取和验证工具方法

    :param path_builder: 一个无参数的回调函数，用于构建文件路径
                        该函数内部负责读取用户输入并返回构建好的Path对象
    :param error_message: 自定义的错误提示信息，如果为None则使用默认提示
    :param check_is_file: 是否额外检查路径是文件而非目录，默认True
    :return: 验证存在的文件路径
    """
    while True:
        # 调用回调函数构建文件路径
        file_path = path_builder()

        # 验证文件是否存在
        if not file_path.exists():
            msg = error_message or f"❌ 路径 {file_path} 不存在，请重新输入。"
            print(msg)
            continue

        # 如果需要检查是否为文件
        if check_is_file and not file_path.is_file():
            print(f"❌ {file_path} 不是文件，请重新输入。")
            continue

        logging.info(f"✅ 找到目标文件: {file_path}")
        return file_path

def _get_candidate_paths(
        base_json_dir: Path,
        category: str,
        name_hyphen: str
) -> list[Path]:
    """生成所有候选文件路径（按优先级排序）"""
    category_dir = base_json_dir / f"{category}-json"
    candidates = [category_dir / f"{name_hyphen}.json"]

    if category == "staff":
        candidates.append(category_dir / "alumni" / f"{name_hyphen}.json")
    # 受益人暂时全选2026新客户
    elif category == "beneficiary":
        candidates.append(category_dir / "2026" / f"{name_hyphen}.json")
    return candidates

def find_target_json_file(
        project_root: Path,
        category: str,
        name_hyphen: str
) -> Optional[Path]:
    """
    查找目标 JSON 文件。
    对于 'staff' 类别，会尝试查找:
    1. docs/assets/json/staff-json/{name_hyphen}.json (在职)
    2. docs/assets/json/staff-json/alumni/{name_hyphen}.json (离职)
    
    对于其他类别，仅查找:
    docs/assets/json/{category}-json/{name_hyphen}.json
    
    :param project_root: 项目根目录 Path 对象
    :param category: 类别 (e.g., 'staff', 'beneficiary')
    :param name_hyphen: 连字符连接的名称 (e.g., 'san-zhang')
    :return: 找到的文件 Path 对象，如果未找到则返回 None
    """
    base_json_dir = project_root / "docs/assets/json"
    candidates = _get_candidate_paths(base_json_dir, category, name_hyphen)

    """
    遍历候选路径、返回第一个存在的
    """
    return next((path for path in candidates if path.exists()), None)

if __name__ == "__main__":
    # 测试代码
    print("--- 测试 path_utils.py ---")
    
    # 测试 get_project_root
    root = get_project_root()
    print(f"Project Root: {root}")
    
    # 测试 path_exists
    print(f"Root exists: {path_exists(root)}")
    
    # 测试 list_all_files (列出 scripts/utils 下的文件)
    current_dir = Path(__file__).parent
    print(f"Files in {current_dir.name}: {list_all_files(current_dir)}")
    
    print("--- 测试结束 ---")