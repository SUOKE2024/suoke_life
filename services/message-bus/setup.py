from setuptools import setup, find_packages

setup(
    name="message-bus",
    version="0.1.0",
    description="消息总线服务，负责系统间事件传递和通知",
    author="Soke Life Team",
    packages=find_packages(),
    install_requires=[
        "grpcio",
        "grpcio-tools",
        "grpcio-health-checking",
        "protobuf",
        "pydantic",
        "python-dotenv",
        "prometheus-client",
        "structlog",
        "pydantic-settings",
        "confluent-kafka",
        "aiokafka",
        "asyncio",
        "aiohttp",
        "redis",
        "PyJWT",
        "cryptography",
        "requests",
    ],
    python_requires=">=3.9",
) 