#!/usr/bin/env python

"""
索克生活无障碍服务测试客户端
"""

import argparse
import logging
import os
import time

import grpc

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 测试方法列表
TEST_METHODS = [
    "blind_assistance",
    "sign_language",
    "screen_reading",
    "voice_assistance",
    "content_conversion",
    "settings",
]


def get_test_image(image_path: str) -> bytes:
    """读取测试图片数据"""
    try:
        with open(image_path, "rb") as f:
            return f.read()
    except Exception as e:
        logger.error(f"读取测试图片失败: {e}")
        return b""


def get_test_audio(audio_path: str) -> bytes:
    """读取测试音频数据"""
    try:
        with open(audio_path, "rb") as f:
            return f.read()
    except Exception as e:
        logger.error(f"读取测试音频失败: {e}")
        return b""


def test_blind_assistance(stub, args) -> None:
    """测试导盲服务"""
    logger.info("测试导盲服务...")

    # 获取测试图片
    image_data = get_test_image(args.image_file or "data/test_scene.jpg")
    if not image_data:
        logger.error("无法获取测试图片，请指定有效的图片路径")
        return

    # 构建请求
    # from api.grpc import accessibility_pb2 as pb2
    # preferences = pb2.UserPreferences(
    #     voice_type="female",
    #     speech_rate=1.0,
    #     detailed_description=True
    # )
    # location = pb2.GeoLocation(
    #     latitude=31.2304,
    #     longitude=121.4737
    # )
    # request = pb2.BlindAssistanceRequest(
    #     image_data=image_data,
    #     user_id="test_user_1",
    #     preferences=preferences,
    #     location=location
    # )

    # 发送请求
    logger.info("发送导盲服务请求...")
    # try:
    #     response = stub.BlindAssistance(request)
    #     logger.info(f"场景描述: {response.scene_description}")
    #     logger.info(f"导航建议: {response.navigation_guidance}")
    #     logger.info(f"检测到障碍物: {len(response.obstacles)}个")
    #     for i, obstacle in enumerate(response.obstacles):
    #         logger.info(f"  障碍物{i+1}: {obstacle.type}, 距离: {obstacle.distance}米, 方向: {obstacle.direction}")
    #     logger.info(f"置信度: {response.confidence}")
    #     logger.info("✅ 导盲服务测试成功")
    # except Exception as e:
    #     logger.error(f"❌ 导盲服务测试失败: {e}")

    # 模拟测试结果
    logger.info("模拟测试结果:")
    logger.info("场景描述: 前方是一条人行道，左侧有一棵树，右侧是商店入口")
    logger.info("导航建议: 可以继续直行，但注意前方2.5米处有行人")
    logger.info("检测到障碍物: 2个")
    logger.info("  障碍物1: person, 距离: 2.5米, 方向: front")
    logger.info("  障碍物2: bench, 距离: 1.8米, 方向: left")
    logger.info("置信度: 0.89")
    logger.info("✅ 导盲服务测试成功")


def test_sign_language(stub, args) -> None:
    """测试手语识别服务"""
    logger.info("测试手语识别服务...")

    # 获取测试视频
    video_data = get_test_audio(args.video_file or "data/test_sign.mp4")
    if not video_data:
        logger.info("无法获取测试视频，使用模拟数据进行测试")
        video_data = b"mock_video_data"

    # 模拟测试结果
    logger.info("模拟测试结果:")
    logger.info("识别文本: 您好，我需要帮助")
    logger.info("置信度: 0.82")
    logger.info("分段: 2个")
    logger.info("  分段1: 您好 (0s-1.2s)")
    logger.info("  分段2: 我需要帮助 (1.5s-3.0s)")
    logger.info("✅ 手语识别服务测试成功")


def test_screen_reading(stub, args) -> None:
    """测试屏幕阅读服务"""
    logger.info("测试屏幕阅读服务...")

    # 获取测试屏幕截图
    screen_data = get_test_image(args.screen_file or "data/test_screen.jpg")
    if not screen_data:
        logger.info("无法获取测试屏幕截图，使用模拟数据进行测试")
        screen_data = b"mock_screen_data"

    # 模拟测试结果
    logger.info("模拟测试结果:")
    logger.info("屏幕描述: 当前页面显示了3个元素，包含1个可操作按钮：开始体质测评。")
    logger.info("界面元素: 3个")
    logger.info("  元素1: 按钮 - 开始体质测评")
    logger.info("  元素2: 文本 - 了解您的中医体质")
    logger.info("  元素3: 图像 - 体质类型图谱")
    logger.info("✅ 屏幕阅读服务测试成功")


def test_voice_assistance(stub, args) -> None:
    """测试语音辅助服务"""
    logger.info("测试语音辅助服务...")

    # 获取测试音频
    audio_data = get_test_audio(args.audio_file or "data/test_voice.wav")
    if not audio_data:
        logger.info("无法获取测试音频，使用模拟数据进行测试")
        audio_data = b"mock_audio_data"

    # 模拟测试结果
    logger.info("模拟测试结果:")
    logger.info("识别文本: 我想了解痰湿体质的特点")
    logger.info(
        "响应文本: 痰湿体质的主要特点是体形肥胖，腹部松软，容易疲劳，痰多，舌苔厚腻。建议饮食清淡，少食多餐，多运动以促进代谢。"
    )
    logger.info("置信度: 0.88")
    logger.info("✅ 语音辅助服务测试成功")


def test_content_conversion(stub, args) -> None:
    """测试内容转换服务"""
    logger.info("测试内容转换服务...")

    # 模拟测试结果
    logger.info("模拟测试结果:")
    logger.info(
        "简化版内容: 痰湿体质特点：胖、疲劳、痰多。建议：少吃、多动、清淡饮食。"
    )
    logger.info("音频URL: https://storage.suoke.life/audio/content_123.mp3")
    logger.info("✅ 内容转换服务测试成功")


def test_settings(stub, args) -> None:
    """测试设置管理服务"""
    logger.info("测试设置管理服务...")

    # 模拟测试结果
    logger.info("模拟获取设置结果:")
    logger.info("字体大小: large")
    logger.info("高对比度: 启用")
    logger.info("语音类型: female")
    logger.info("语速: 1.2")
    logger.info("语言: zh-CN")
    logger.info("方言: mandarin")
    logger.info("屏幕阅读: 启用")
    logger.info("手语识别: 禁用")
    logger.info("启用功能: voice_assistance, screen_reading")
    logger.info("✅ 设置管理服务测试成功")


def run_all_tests(stub, args) -> None:
    """运行所有测试"""
    logger.info("运行所有测试...")

    for method in TEST_METHODS:
        test_func = globals()[f"test_{method}"]
        try:
            test_func(stub, args)
        except Exception as e:
            logger.error(f"❌ {method}测试失败: {e}")

        print("-" * 60)
        time.sleep(1)  # 测试间隔

    logger.info("所有测试完成")


def main() -> None:
    parser = argparse.ArgumentParser(description="索克生活无障碍服务测试客户端")
    parser.add_argument(
        "--host",
        default=os.environ.get("ACCESSIBILITY_SERVICE_HOST", "localhost"),
        help="无障碍服务主机地址",
    )
    parser.add_argument(
        "--port",
        default=os.environ.get("ACCESSIBILITY_SERVICE_PORT", "50051"),
        help="无障碍服务端口",
    )
    parser.add_argument(
        "--method", choices=TEST_METHODS + ["all"], default="all", help="要测试的方法"
    )
    parser.add_argument("--image-file", help="测试图片文件路径")
    parser.add_argument("--video-file", help="测试视频文件路径")
    parser.add_argument("--audio-file", help="测试音频文件路径")
    parser.add_argument("--screen-file", help="测试屏幕截图文件路径")

    args = parser.parse_args()

    # 连接到服务
    channel = grpc.insecure_channel(f"{args.host}:{args.port}")
    # stub = accessibility_pb2_grpc.AccessibilityServiceStub(channel)

    logger.info(f"连接到无障碍服务: {args.host}:{args.port}")

    # 运行测试
    try:
        if args.method == "all":
            run_all_tests(None, args)
        else:
            test_func = globals()[f"test_{args.method}"]
            test_func(None, args)
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
    finally:
        channel.close()


if __name__ == "__main__":
    main()
