from typing import Any, Dict, List, Optional, Union

"""
setup - 索克生活项目模块
"""

import platform

from setuptools import Extension, setup

#! / usr / bin / env python3
"""
索克生活 - C扩展编译配置
"""


# 获取NumPy头文件路径
numpy_include = np.get_include()

# 根据平台设置编译选项
if platform.system() == "Windows":
    extra_compile_args = [" / O2", " / openmp"]
    extra_link_args = []
elif platform.system() == "Darwin":  # macOS
    extra_compile_args = [" - O3", " - Xpreprocessor", " - fopenmp"]
    extra_link_args = [" - lomp"]
else:  # Linux
    extra_compile_args = [" - O3", " - fopenmp"]
    extra_link_args = [" - lgomp"]

# 定义扩展模块
extensions = [
    Extension(
        name="tcm_analysis",
        sources=["c_algorithms / tcm_analysis.c"],
        include_dirs=[numpy_include],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        language="c",
    )
]

# 设置配置
setup(
    name="suoke_life_c_extensions",
    version="1.0.0",
    description="索克生活高性能C扩展模块",
    author="索克生活团队",
    author_email="dev@suoke.life",
    ext_modules=extensions,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: C",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific / Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
