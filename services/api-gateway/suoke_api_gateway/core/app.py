"""应用主模块"""

from fastapi import FastAPI

from .config import get_settings


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    return app


def main() -> None:
    """主函数"""
    pass


if __name__ == "__main__":
    main()
