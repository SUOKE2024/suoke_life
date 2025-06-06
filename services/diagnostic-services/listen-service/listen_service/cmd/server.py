"""
server - 索克生活项目模块
"""

    from ..models.audio_models import AnalysisRequest, AudioFormat, AudioMetadata
from ..core.audio_analyzer import AudioAnalyzer
from ..core.tcm_analyzer import TCMFeatureExtractor
from ..delivery.grpc_server import ListenServiceGRPCServer
from ..delivery.rest_api import create_rest_app
from ..utils.cache import AudioCache, MemoryCache, RedisCache
from ..utils.logging import setup_logging
import asyncio
import click
import signal
import structlog
import sys
import uvicorn

"""
服务器启动命令行工具

支持启动gRPC服务器和REST API服务器。
"""




logger = structlog.get_logger(__name__)

@click.group()
@click.option("--log-level", default="INFO", help="日志级别")
@click.option("--log-format", default="json", help="日志格式 (json/console/plain)")
@click.option("--log-file", help="日志文件路径")
@click.pass_context
def cli(ctx, log_level, log_format, log_file):
    """索克生活闻诊服务命令行工具"""
    ctx.ensure_object(dict)

    # 设置日志
    setup_logging(
        level=log_level,
        format_type=log_format,
        log_file=log_file,
        service_name="listen-service",
    )

    ctx.obj["log_level"] = log_level
    ctx.obj["log_format"] = log_format
    ctx.obj["log_file"] = log_file

@cli.command()
@click.option("--host", default="0.0.0.0", help="监听主机")
@click.option("--port", default=50051, help="监听端口")
@click.option("--cache-backend", default="memory", help="缓存后端 (memory/redis)")
@click.option("--redis-url", default="redis://localhost:6379", help="Redis连接URL")
@click.pass_context
def grpc(ctx, host, port, cache_backend, redis_url):
    """启动gRPC服务器"""
    logger.info("启动gRPC服务器", host=host, port=port)

    try:
        # 创建缓存后端
        if cache_backend == "redis":
            cache = AudioCache(RedisCache(redis_url))
        else:
            cache = AudioCache(MemoryCache())

        # 创建分析器
        audio_analyzer = AudioAnalyzer(cache=cache)
        tcm_analyzer = TCMFeatureExtractor()

        # 创建gRPC服务器
        server = ListenServiceGRPCServer(
            audio_analyzer=audio_analyzer,
            tcm_analyzer=tcm_analyzer,
            cache=cache,
        )

        # 运行服务器
        asyncio.run(_run_grpc_server(server, host, port))

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止服务器")
    except Exception as e:
        logger.error("gRPC服务器启动失败", error=str(e), exc_info=True)
        sys.exit(1)

@cli.command()
@click.option("--host", default="0.0.0.0", help="监听主机")
@click.option("--port", default=8000, help="监听端口")
@click.option("--workers", default=1, help="工作进程数")
@click.option("--cache-backend", default="memory", help="缓存后端 (memory/redis)")
@click.option("--redis-url", default="redis://localhost:6379", help="Redis连接URL")
@click.option("--reload", is_flag=True, help="启用自动重载")
@click.pass_context
def rest(ctx, host, port, workers, cache_backend, redis_url, reload):
    """启动REST API服务器"""
    logger.info("启动REST API服务器", host=host, port=port, workers=workers)

    try:
        # 创建缓存后端
        if cache_backend == "redis":
            cache = AudioCache(RedisCache(redis_url))
        else:
            cache = AudioCache(MemoryCache())

        # 创建分析器
        audio_analyzer = AudioAnalyzer(cache=cache)
        tcm_analyzer = TCMFeatureExtractor()

        # 创建FastAPI应用
        app = create_rest_app(
            audio_analyzer=audio_analyzer,
            tcm_analyzer=tcm_analyzer,
            cache=cache,
        )

        # 配置uvicorn
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            workers=workers if not reload else 1,
            reload=reload,
            log_level=ctx.obj["log_level"].lower(),
            access_log=True,
        )

        # 启动服务器
        server = uvicorn.Server(config)
        server.run()

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止服务器")
    except Exception as e:
        logger.error("REST API服务器启动失败", error=str(e), exc_info=True)
        sys.exit(1)

@cli.command()
@click.option("--grpc-host", default="0.0.0.0", help="gRPC监听主机")
@click.option("--grpc-port", default=50051, help="gRPC监听端口")
@click.option("--rest-host", default="0.0.0.0", help="REST监听主机")
@click.option("--rest-port", default=8000, help="REST监听端口")
@click.option("--cache-backend", default="memory", help="缓存后端 (memory/redis)")
@click.option("--redis-url", default="redis://localhost:6379", help="Redis连接URL")
@click.pass_context
def hybrid(ctx, grpc_host, grpc_port, rest_host, rest_port, cache_backend, redis_url):
    """同时启动gRPC和REST API服务器"""
    logger.info(
        "启动混合服务器",
        grpc_host=grpc_host,
        grpc_port=grpc_port,
        rest_host=rest_host,
        rest_port=rest_port,
    )

    try:
        # 创建缓存后端
        if cache_backend == "redis":
            cache = AudioCache(RedisCache(redis_url))
        else:
            cache = AudioCache(MemoryCache())

        # 创建分析器
        audio_analyzer = AudioAnalyzer(cache=cache)
        tcm_analyzer = TCMFeatureExtractor()

        # 运行混合服务器
        asyncio.run(
            _run_hybrid_server(
                audio_analyzer,
                tcm_analyzer,
                cache,
                grpc_host,
                grpc_port,
                rest_host,
                rest_port,
            )
        )

    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止服务器")
    except Exception as e:
        logger.error("混合服务器启动失败", error=str(e), exc_info=True)
        sys.exit(1)

@cli.command()
@click.option("--cache-backend", default="memory", help="缓存后端 (memory/redis)")
@click.option("--redis-url", default="redis://localhost:6379", help="Redis连接URL")
def test_components(cache_backend, redis_url):
    """测试组件功能"""
    logger.info("测试组件功能")

    try:
        asyncio.run(_test_components(cache_backend, redis_url))
    except Exception as e:
        logger.error("组件测试失败", error=str(e), exc_info=True)
        sys.exit(1)

async def _run_grpc_server(server: ListenServiceGRPCServer, host: str, port: int):
    """运行gRPC服务器"""

    # 设置信号处理
    def signal_handler():
        logger.info("收到停止信号")
        asyncio.create_task(server.stop_server())

    # 注册信号处理器
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, lambda s, f: signal_handler())

    # 启动服务器
    await server.start_server(host, port)

async def _run_hybrid_server(
    audio_analyzer: AudioAnalyzer,
    tcm_analyzer: TCMFeatureExtractor,
    cache: AudioCache,
    grpc_host: str,
    grpc_port: int,
    rest_host: str,
    rest_port: int,
):
    """运行混合服务器"""

    # 创建gRPC服务器
    grpc_server = ListenServiceGRPCServer(
        audio_analyzer=audio_analyzer,
        tcm_analyzer=tcm_analyzer,
        cache=cache,
    )

    # 创建REST API应用
    rest_app = create_rest_app(
        audio_analyzer=audio_analyzer,
        tcm_analyzer=tcm_analyzer,
        cache=cache,
    )

    # 创建uvicorn配置
    uvicorn_config = uvicorn.Config(
        app=rest_app,
        host=rest_host,
        port=rest_port,
        log_level="info",
    )
    uvicorn_server = uvicorn.Server(uvicorn_config)

    # 停止标志
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("收到停止信号")
        stop_event.set()

    # 注册信号处理器
    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, lambda s, f: signal_handler())

    try:
        # 并发启动两个服务器
        grpc_task = asyncio.create_task(grpc_server.start_server(grpc_host, grpc_port))
        rest_task = asyncio.create_task(uvicorn_server.serve())

        logger.info("混合服务器已启动")

        # 等待停止信号
        await stop_event.wait()

        logger.info("正在停止服务器")

        # 停止服务器
        await grpc_server.stop_server()
        uvicorn_server.should_exit = True

        # 等待任务完成
        await asyncio.gather(grpc_task, rest_task, return_exceptions=True)

    except Exception as e:
        logger.error("混合服务器运行异常", error=str(e), exc_info=True)
        raise

async def _test_components(cache_backend: str, redis_url: str):
    """测试组件功能"""
    logger.info("开始组件测试")

    # 创建缓存后端
    if cache_backend == "redis":
        cache = AudioCache(RedisCache(redis_url))
    else:
        cache = AudioCache(MemoryCache())

    # 测试缓存
    logger.info("测试缓存功能")
    test_key = "test_key"
    test_value = {"test": "data"}

    await cache.backend.set(test_key, test_value, 60)
    cached_value = await cache.backend.get(test_key)

    if cached_value == test_value:
        logger.info("缓存测试通过")
    else:
        logger.error("缓存测试失败")
        return

    # 测试音频分析器
    logger.info("测试音频分析器")
    audio_analyzer = AudioAnalyzer(cache=cache)

    # 创建测试音频数据

    test_audio = (np.random.randn(16000) * 32767).astype(np.int16).tobytes()


    metadata = AudioMetadata(
        sample_rate=16000,
        channels=1,
        duration=1.0,
        format=AudioFormat.WAV,
        file_size=len(test_audio),
    )

    request = AnalysisRequest(
        request_id="test-request",
        audio_data=test_audio,
        metadata=metadata,
        analysis_type="test",
    )

    result = await audio_analyzer.analyze_audio(request)

    if result.success:
        logger.info("音频分析器测试通过")
    else:
        logger.error("音频分析器测试失败", error=result.error_message)
        return

    # 测试中医分析器
    logger.info("测试中医分析器")
    tcm_analyzer = TCMFeatureExtractor()

    if result.voice_features:
        tcm_result = await tcm_analyzer.analyze_tcm_features(result.voice_features)

        if tcm_result.confidence_score > 0:
            logger.info("中医分析器测试通过")
        else:
            logger.error("中医分析器测试失败")
            return

    logger.info("所有组件测试通过")

if __name__ == "__main__":
    cli()
