# scripts/utils/__init__.py

"""
工具模块
"""

from .gh_utils import check_gh_installed
from .logging_utils import setup_logging

# 定义包的公开API
__all__ = ['check_gh_installed', 'setup_logging']