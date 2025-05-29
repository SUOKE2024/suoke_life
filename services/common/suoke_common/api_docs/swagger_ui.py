#!/usr/bin/env python3
"""
Swagger UI服务器
提供Web界面来查看和测试API文档
"""

import asyncio
import logging

try:
    from aiohttp import ClientSession, web
    from aiohttp.web_response import Response

    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

from .openapi_generator import get_openapi_generator

logger = logging.getLogger(__name__)


class SwaggerUIServer:
    """Swagger UI服务器"""

    def __init__(
        self,
        generator_name: str = "default",
        host: str = "0.0.0.0",
        port: int = 8080,
        title: str = "API文档",
        swagger_ui_version: str = "4.15.5",
    ):
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp未安装，请安装: pip install aiohttp")

        self.generator_name = generator_name
        self.host = host
        self.port = port
        self.title = title
        self.swagger_ui_version = swagger_ui_version

        self.app: web.Application | None = None
        self.runner: web.AppRunner | None = None
        self.site: web.TCPSite | None = None

    def create_app(self) -> web.Application:
        """创建Web应用"""
        app = web.Application()

        # 添加路由
        app.router.add_get("/", self.index_handler)
        app.router.add_get("/docs", self.docs_handler)
        app.router.add_get("/openapi.json", self.openapi_json_handler)
        app.router.add_get("/openapi.yaml", self.openapi_yaml_handler)
        app.router.add_get("/health", self.health_handler)

        return app

    async def index_handler(self, request: web.Request) -> Response:
        """首页处理器"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.title}</title>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    text-align: center;
                }}
                .links {{
                    text-align: center;
                    margin-top: 30px;
                }}
                .links a {{
                    display: inline-block;
                    margin: 10px;
                    padding: 12px 24px;
                    background: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    transition: background 0.3s;
                }}
                .links a:hover {{
                    background: #0056b3;
                }}
                .info {{
                    background: #e9ecef;
                    padding: 20px;
                    border-radius: 4px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{self.title}</h1>
                <div class="info">
                    <p><strong>服务器:</strong> {self.host}:{self.port}</p>
                    <p><strong>生成器:</strong> {self.generator_name}</p>
                    <p><strong>Swagger UI版本:</strong> {self.swagger_ui_version}</p>
                </div>
                <div class="links">
                    <a href="/docs">查看API文档</a>
                    <a href="/openapi.json">下载JSON格式</a>
                    <a href="/openapi.yaml">下载YAML格式</a>
                    <a href="/health">健康检查</a>
                </div>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html, content_type="text/html")

    async def docs_handler(self, request: web.Request) -> Response:
        """文档页面处理器"""
        # 获取生成器
        generator = get_openapi_generator(self.generator_name)
        if not generator:
            return web.Response(
                text=f"未找到OpenAPI生成器: {self.generator_name}", status=404
            )

        # 生成Swagger UI HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>{self.title}</title>
            <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@{self.swagger_ui_version}/swagger-ui.css" />
            <style>
                html {{
                    box-sizing: border-box;
                    overflow: -moz-scrollbars-vertical;
                    overflow-y: scroll;
                }}
                *, *:before, *:after {{
                    box-sizing: inherit;
                }}
                body {{
                    margin:0;
                    background: #fafafa;
                }}
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@{self.swagger_ui_version}/swagger-ui-bundle.js"></script>
            <script src="https://unpkg.com/swagger-ui-dist@{self.swagger_ui_version}/swagger-ui-standalone-preset.js"></script>
            <script>
                window.onload = function() {{
                    const ui = SwaggerUIBundle({{
                        url: '/openapi.json',
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIStandalonePreset
                        ],
                        plugins: [
                            SwaggerUIBundle.plugins.DownloadUrl
                        ],
                        layout: "StandaloneLayout",
                        defaultModelsExpandDepth: 1,
                        defaultModelExpandDepth: 1,
                        docExpansion: "list",
                        filter: true,
                        showExtensions: true,
                        showCommonExtensions: true,
                        tryItOutEnabled: true
                    }});
                }};
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type="text/html")

    async def openapi_json_handler(self, request: web.Request) -> Response:
        """OpenAPI JSON处理器"""
        generator = get_openapi_generator(self.generator_name)
        if not generator:
            return web.Response(
                text=f"未找到OpenAPI生成器: {self.generator_name}", status=404
            )

        try:
            json_content = generator.generate_json()
            return web.Response(
                text=json_content,
                content_type="application/json",
                headers={"Content-Disposition": 'attachment; filename="openapi.json"'},
            )
        except Exception as e:
            logger.error(f"生成OpenAPI JSON失败: {e}")
            return web.Response(text=str(e), status=500)

    async def openapi_yaml_handler(self, request: web.Request) -> Response:
        """OpenAPI YAML处理器"""
        generator = get_openapi_generator(self.generator_name)
        if not generator:
            return web.Response(
                text=f"未找到OpenAPI生成器: {self.generator_name}", status=404
            )

        try:
            yaml_content = generator.generate_yaml()
            return web.Response(
                text=yaml_content,
                content_type="application/x-yaml",
                headers={"Content-Disposition": 'attachment; filename="openapi.yaml"'},
            )
        except Exception as e:
            logger.error(f"生成OpenAPI YAML失败: {e}")
            return web.Response(text=str(e), status=500)

    async def health_handler(self, request: web.Request) -> Response:
        """健康检查处理器"""
        generator = get_openapi_generator(self.generator_name)

        health_data = {
            "status": "healthy",
            "generator_name": self.generator_name,
            "generator_available": generator is not None,
            "endpoints_count": len(generator.endpoints) if generator else 0,
            "schemas_count": len(generator.schemas) if generator else 0,
        }

        import json

        return web.Response(
            text=json.dumps(health_data, ensure_ascii=False, indent=2),
            content_type="application/json",
        )

    async def start(self):
        """启动服务器"""
        try:
            self.app = self.create_app()
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()

            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()

            logger.info(f"Swagger UI服务器已启动: http://{self.host}:{self.port}")
            logger.info(f"API文档地址: http://{self.host}:{self.port}/docs")

        except Exception as e:
            logger.error(f"启动Swagger UI服务器失败: {e}")
            raise

    async def stop(self):
        """停止服务器"""
        try:
            if self.site:
                await self.site.stop()
                self.site = None

            if self.runner:
                await self.runner.cleanup()
                self.runner = None

            self.app = None

            logger.info("Swagger UI服务器已停止")

        except Exception as e:
            logger.error(f"停止Swagger UI服务器失败: {e}")

    async def run_forever(self):
        """运行服务器直到被中断"""
        await self.start()

        try:
            # 等待直到被中断
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在停止服务器...")
        finally:
            await self.stop()


def create_swagger_server(
    generator_name: str = "default",
    host: str = "0.0.0.0",
    port: int = 8080,
    title: str = "API文档",
) -> SwaggerUIServer:
    """创建Swagger UI服务器"""
    return SwaggerUIServer(
        generator_name=generator_name, host=host, port=port, title=title
    )


async def serve_docs(
    generator_name: str = "default",
    host: str = "0.0.0.0",
    port: int = 8080,
    title: str = "API文档",
):
    """启动文档服务器（便捷函数）"""
    server = create_swagger_server(generator_name, host, port, title)
    await server.run_forever()


if __name__ == "__main__":
    # 示例用法
    from .openapi_generator import create_default_generator

    # 创建示例生成器
    generator = create_default_generator("示例服务")

    # 启动文档服务器
    asyncio.run(serve_docs(generator_name="示例服务", title="示例服务API文档"))
