"""
dependency_manager - 索克生活项目模块
"""

from collections.abc import Callable
from functools import wraps
from typing import Any
import importlib
import logging
import warnings

#! / usr / bin / env python

"""
可选依赖管理器
用于优雅处理可选的科学计算库和其他依赖
"""


logger = logging.getLogger(__name__)


class OptionalDependency:
    """可选依赖包装器"""

    def __init__(self, name: str, import_name: str = None,
                fallback_message: str = None, install_hint: str = None):
        self.name = name
        self.import_name = import_name or name
        self.fallback_message = fallback_message or f"{name}库未安装，将使用简化版本"
        self.install_hint = install_hint or f"pip install {name}"
        self._module = None
        self._available = None

    @property
    def available(self) - > bool:
        """检查依赖是否可用"""
        if self._available is None:
            try:
                self._module = importlib.import_module(self.import_name)
                self._available = True
                logger.debug(f"✅ {self.name} 库可用")
            except ImportError:
                self._available = False
                logger.info(f"⚠️ {self.fallback_message}")
                logger.debug(f"💡 安装提示: {self.install_hint}")
        return self._available

    @property
    def module(self) - > Any | None:
        """获取模块对象"""
        if self.available:
            return self._module
        return None

    def require(self) - > Any:
        """要求依赖必须可用，否则抛出异常"""
        if not self.available:
            raise ImportError(f"{self.name} 是必需的依赖，但未安装。{self.install_hint}")
        return self._module


class DependencyManager:
    """依赖管理器"""

    def __init__(self) - > None:
        """TODO: 添加文档字符串"""
        self._dependencies: dict[str, OptionalDependency] = {}
        self._setup_dependencies()

    def _setup_dependencies(self) - > None:
        """设置所有可选依赖"""

        # 科学计算库
        self._dependencies['pandas'] = OptionalDependency(
            'pandas',
            fallback_message = "Pandas库未安装，高级数据分析功能将使用简化版本",
            install_hint = "pip install pandas> = 2.1.0"
        )

        self._dependencies['numpy'] = OptionalDependency(
            'numpy',
            fallback_message = "NumPy库未安装，数值计算将使用Python内置功能",
            install_hint = "pip install numpy> = 1.24.0"
        )

        self._dependencies['scipy'] = OptionalDependency(
            'scipy',
            fallback_message = "SciPy库未安装，科学计算功能受限",
            install_hint = "pip install scipy> = 1.11.0"
        )

        self._dependencies['scikit - learn'] = OptionalDependency(
            'sklearn',
            import_name = 'sklearn',
            fallback_message = "Scikit - learn库未安装，机器学习功能受限",
            install_hint = "pip install scikit - learn> = 1.3.0"
        )

        # 深度学习库
        self._dependencies['torch'] = OptionalDependency(
            'torch',
            fallback_message = "PyTorch库未安装，深度学习功能受限",
            install_hint = "pip install torch> = 2.1.0"
        )

        self._dependencies['tensorflow'] = OptionalDependency(
            'tensorflow',
            fallback_message = "TensorFlow库未安装，部分AI功能受限",
            install_hint = "pip install tensorflow> = 2.15.0"
        )

        # 计算机视觉库
        self._dependencies['cv2'] = OptionalDependency(
            'opencv - python',
            import_name = 'cv2',
            fallback_message = "OpenCV库未安装，图像处理功能受限",
            install_hint = "pip install opencv - python> = 4.8.0"
        )

        self._dependencies['PIL'] = OptionalDependency(
            'Pillow',
            import_name = 'PIL',
            fallback_message = "Pillow库未安装，图像处理功能受限",
            install_hint = "pip install Pillow> = 10.0.0"
        )

        # 音频处理库
        self._dependencies['librosa'] = OptionalDependency(
            'librosa',
            fallback_message = "Librosa库未安装，音频分析功能受限",
            install_hint = "pip install librosa> = 0.10.0"
        )

        self._dependencies['sounddevice'] = OptionalDependency(
            'sounddevice',
            fallback_message = "SoundDevice库未安装，音频录制功能受限",
            install_hint = "pip install sounddevice> = 0.4.0"
        )

        # 桌面自动化库
        self._dependencies['pyautogui'] = OptionalDependency(
            'pyautogui',
            fallback_message = "PyAutoGUI库未安装，桌面自动化功能受限",
            install_hint = "pip install pyautogui> = 0.9.0"
        )

        self._dependencies['pynput'] = OptionalDependency(
            'pynput',
            fallback_message = "PyInput库未安装，输入监控功能受限",
            install_hint = "pip install pynput> = 1.7.0"
        )

    def get(self, name: str) - > OptionalDependency:
        """获取依赖"""
        if name not in self._dependencies:
            raise ValueError(f"未知的依赖: {name}")
        return self._dependencies[name]

    def is_available(self, name: str) - > bool:
        """检查依赖是否可用"""
        return self.get(name).available

    def get_module(self, name: str) - > Any | None:
        """获取模块对象"""
        return self.get(name).module

    def require(self, name: str) - > Any:
        """要求依赖必须可用"""
        return self.get(name).require()

    def check_all(self) - > dict[str, bool]:
        """检查所有依赖的可用性"""
        return {name: dep.available for name, dep in self._dependencies.items()}

    def get_missing_dependencies(self) - > list[str]:
        """获取缺失的依赖列表"""
        return [name for name, dep in self._dependencies.items() if not dep.available]

    def get_available_dependencies(self) - > list[str]:
        """获取可用的依赖列表"""
        return [name for name, dep in self._dependencies.items() if dep.available]

    def print_status(self) - > None:
        """打印依赖状态"""
        print("📦 依赖状态检查:")
        print(" = " * 50)

        available = self.get_available_dependencies()
        missing = self.get_missing_dependencies()

        if available:
            print("✅ 可用的依赖:")
            for dep in available:
                print(f"  • {dep}")

        if missing:
            print("\n⚠️ 缺失的依赖:")
            for dep in missing:
                dep_obj = self.get(dep)
                print(f"  • {dep}: {dep_obj.install_hint}")

        print(f"\n📊 总计: {len(available)} / {len(self._dependencies)} 个依赖可用")


def optional_import(dependency_name: str):
    """装饰器：标记函数需要可选依赖"""
    def decorator(func: Callable) - > Callable:
        """TODO: 添加文档字符串"""
        @wraps(func)
        def wrapper( * args, * *kwargs):
            """TODO: 添加文档字符串"""
            dep_manager = DependencyManager()
            if not dep_manager.is_available(dependency_name):
                dep = dep_manager.get(dependency_name)
                warnings.warn(f"{dep.fallback_message}", UserWarning, stacklevel = 2)
                # 可以选择返回简化版本或抛出异常
                return None
            return func( * args, * *kwargs)
        return wrapper
    return decorator


def require_dependency(dependency_name: str):
    """装饰器：要求函数必须有指定依赖"""
    def decorator(func: Callable) - > Callable:
        """TODO: 添加文档字符串"""
        @wraps(func)
        def wrapper( * args, * *kwargs):
            """TODO: 添加文档字符串"""
            dep_manager = DependencyManager()
            dep_manager.require(dependency_name)
            return func( * args, * *kwargs)
        return wrapper
    return decorator


# 全局依赖管理器实例
dependency_manager = DependencyManager()


# 便捷函数
def get_dependency(name: str) - > OptionalDependency:
    """获取依赖"""
    return dependency_manager.get(name)


def is_available(name: str) - > bool:
    """检查依赖是否可用"""
    return dependency_manager.is_available(name)


def get_module(name: str) - > Any | None:
    """获取模块对象"""
    return dependency_manager.get_module(name)


def require(name: str) - > Any:
    """要求依赖必须可用"""
    return dependency_manager.require(name)


if __name__ == "__main__":
    # 测试依赖管理器
    dm = DependencyManager()
    dm.print_status()
