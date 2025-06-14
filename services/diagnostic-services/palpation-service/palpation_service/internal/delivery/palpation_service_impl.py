"""
palpation_service_impl - 索克生活项目模块
"""

from collections.abc import Iterator
from internal.model.pulse_analyzer import PulseAnalyzer
from internal.model.tcm_pattern_mapper import TCMPatternMapper
from internal.repository.session_repository import SessionRepository
from internal.repository.user_repository import UserRepository
from internal.signal.abdominal_analyzer import AbdominalAnalyzer
from internal.signal.pulse_processor import PulseProcessor
from internal.signal.skin_analyzer import SkinAnalyzer
from pathlib import Path
from pkg.utils.metrics import MetricsCollector
from typing import Any
import grpc
import logging
import time
import uuid

#! / usr / bin / env python

"""
切诊服务实现
负责实现gRPC服务接口
"""



# 导入内部模块

# 导入生成的gRPC代码

logger = logging.getLogger(__name__)

class PalpationServiceImpl(pb2_grpc.PalpationServiceServicer):
    """切诊服务实现类"""

    def __init__(
        self,
        config: dict[str, Any],
        session_repository: SessionRepository,
        user_repository: UserRepository,
    ):
        """
        初始化切诊服务实现

        Args:
            config: 服务配置
            session_repository: 会话存储库
            user_repository: 用户存储库
        """
        self.config = config
        self.session_repository = session_repository
        self.user_repository = user_repository

        # 初始化信号处理组件
        pulse_config = config.get("pulse_analysis", {})
        self.pulse_processor = PulseProcessor(pulse_config)

        # 初始化脉象分析器
        self.pulse_analyzer = PulseAnalyzer(pulse_config)

        # 初始化腹诊分析器
        abdominal_config = config.get("abdominal_analysis", {})
        self.abdominal_analyzer = AbdominalAnalyzer(abdominal_config)

        # 初始化皮肤触诊分析器
        skin_config = config.get("skin_analysis", {})
        self.skin_analyzer = SkinAnalyzer(skin_config)

        # 初始化中医证型映射器
        tcm_config = config.get("tcm_pattern_mapping", {})
        self.tcm_pattern_mapper = TCMPatternMapper(tcm_config)

        # 指标收集器
        metrics_config = config.get("metrics", {})
        self.metrics = MetricsCollector(metrics_config)

        # 集成服务客户端
        self.xiaoai_client = None
        self.rag_client = None

        # 加载服务版本信息
        self.version = self._load_version()

        logger.info("切诊服务实现初始化完成")

    def _load_version(None):
        """加载服务版本信息"""
        try:
            version_file = Path(__file__).resolve().parents[3] / "VERSION"
            if version_file.exists():
                return version_file.read_text().strip()
            return "0.1.0"  # 默认版本
        except Exception as e:
            logger.warning(f"无法加载版本信息: {e}")
            return "unknown"

    def StartPulseSession(
        self, request: pb2.StartPulseSessionRequest, context: grpc.ServicerContext
    ) - > pb2.StartPulseSessionResponse:
        """
        开始脉诊会话

        Args:
            request: 开始会话请求
            context: gRPC上下文

        Returns:
            开始会话响应
        """
        start_time = time.time()

        # 创建会话ID
        session_id = str(uuid.uuid4())

        try:
            # 获取用户信息
            user_id = request.user_id
            user = self.user_repository.get_user(user_id)

            if not user:
                logger.warning(f"用户不存在: {user_id}")
                return pb2.StartPulseSessionResponse(
                    session_id = "", success = False, error_message = f"User not found: {user_id}"
                )

            # 创建会话记录
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "start_time": time.time(),
                "device_info": {
                    "device_id": request.device_info.device_id,
                    "model": request.device_info.model,
                    "firmware_version": request.device_info.firmware_version,
                    "sensor_types": list(request.device_info.sensor_types),
                },
                "calibration_data": {
                    "values": list(request.calibration_data.calibration_values),
                    "timestamp": request.calibration_data.calibration_timestamp,
                    "operator": request.calibration_data.calibration_operator,
                },
                "status": "started",
                "data_packets": [],
                "analysis_results": {},
            }

            # 保存会话
            self.session_repository.create_session(session_id, session_data)

            # 确定采样配置
            sampling_config = request.device_info.sensor_types
            device_config = self._get_device_config(request.device_info.model)

            sampling_config_response = pb2.SamplingConfig(
                sampling_rate = device_config.get("sampling_rate", 1000),
                sampling_duration = device_config.get("sampling_duration", 30),
                required_positions = [
                    "CUN_LEFT",
                    "GUAN_LEFT",
                    "CHI_LEFT",
                    "CUN_RIGHT",
                    "GUAN_RIGHT",
                    "CHI_RIGHT",
                ],
                minimum_pressure = device_config.get("minimum_pressure", 0),
                maximum_pressure = device_config.get("maximum_pressure", 100),
            )

            # 记录指标
            self.metrics.record_counter(
                "pulse_sessions_started", 1, {"device_model": request.device_info.model}
            )

            return pb2.StartPulseSessionResponse(
                session_id = session_id,
                success = True,
                error_message = "",
                sampling_config = sampling_config_response,
            )

        except Exception as e:
            logger.exception(f"开始脉诊会话失败: {e!s}")
            self.metrics.record_counter("pulse_sessions_errors", 1, {"error_type": "start_session"})

            return pb2.StartPulseSessionResponse(
                session_id = "", success = False, error_message = f"Failed to start pulse session: {e!s}"
            )
        finally:
            # 记录延迟
            end_time = time.time()
            self.metrics.record_histogram("pulse_session_start_latency", end_time - start_time)

    def _get_device_config(dict[str, Any]):
        """获取设备配置"""
        devices_config = self.config.get("devices", {})
        supported_models = devices_config.get("supported_models", [])

        for model_config in supported_models:
            if model_config.get("model") == device_model:
                return model_config

        # 如果找不到匹配的设备配置，使用默认值
        return {
            "sampling_rate": devices_config.get("sampling_rate", 1000),
            "sampling_duration": 30,
            "minimum_pressure": 0,
            "maximum_pressure": 100,
        }

    def RecordPulseData(
        self, request_iterator: Iterator[pb2.PulseDataPacket], context: grpc.ServicerContext
    ) - > pb2.RecordPulseDataResponse:
        """
        记录脉诊数据

        Args:
            request_iterator: 脉搏数据包流
            context: gRPC上下文

        Returns:
            记录数据响应
        """
        start_time = time.time()
        session_id = None
        packets_received = 0

        try:
            # 收集数据包
            data_packets = []

            for packet in request_iterator:
                if session_id is None:
                    session_id = packet.session_id

                if packet.session_id ! = session_id:
                    logger.warning(
                        f"数据包会话ID不匹配: 预期 {session_id}, 实际 {packet.session_id}"
                    )
                    continue

                # 转换为字典存储
                packet_data = {
                    "timestamp": packet.timestamp,
                    "pressure_data": list(packet.pressure_data),
                    "velocity_data": list(packet.velocity_data),
                    "position": self._get_position_name(packet.position),
                    "skin_temperature": packet.skin_temperature,
                    "skin_moisture": packet.skin_moisture,
                }

                data_packets.append(packet_data)
                packets_received + = 1

            if not session_id:
                logger.error("未收到数据包")
                return pb2.RecordPulseDataResponse(
                    session_id = "",
                    packets_received = 0,
                    success = False,
                    error_message = "No data packets received",
                )

            # 获取会话数据
            session = self.session_repository.get_session(session_id)
            if not session:
                logger.error(f"会话不存在: {session_id}")
                return pb2.RecordPulseDataResponse(
                    session_id = session_id,
                    packets_received = packets_received,
                    success = False,
                    error_message = f"Session not found: {session_id}",
                )

            # 更新会话数据
            session["data_packets"].extend(data_packets)
            session["last_update_time"] = time.time()

            # 保存更新后的会话
            self.session_repository.update_session(session_id, session)

            # 记录指标
            self.metrics.record_counter("pulse_data_packets_received", packets_received)
            self.metrics.record_histogram("pulse_data_packet_count", packets_received)

            return pb2.RecordPulseDataResponse(
                session_id = session_id,
                packets_received = packets_received,
                success = True,
                error_message = "",
            )

        except Exception as e:
            logger.exception(f"记录脉诊数据失败: {e!s}")
            self.metrics.record_counter("pulse_sessions_errors", 1, {"error_type": "record_data"})

            return pb2.RecordPulseDataResponse(
                session_id = session_id if session_id else "",
                packets_received = packets_received,
                success = False,
                error_message = f"Failed to record pulse data: {e!s}",
            )
        finally:
            # 记录延迟
            end_time = time.time()
            self.metrics.record_histogram("pulse_data_recording_latency", end_time - start_time)

    def _get_position_name(str):
        """将枚举值转换为位置名称"""
        position_map = {
            0: "UNKNOWN_POSITION",
            1: "CUN_LEFT",
            2: "GUAN_LEFT",
            3: "CHI_LEFT",
            4: "CUN_RIGHT",
            5: "GUAN_RIGHT",
            6: "CHI_RIGHT",
        }
        return position_map.get(position_enum, "UNKNOWN_POSITION")

    def ExtractPulseFeatures(
        self, request: pb2.ExtractPulseFeaturesRequest, context: grpc.ServicerContext
    ) - > pb2.ExtractPulseFeaturesResponse:
        """
        提取脉象特征

        Args:
            request: 特征提取请求
            context: gRPC上下文

        Returns:
            脉象特征响应
        """
        start_time = time.time()

        try:
            session_id = request.session_id

            # 获取会话数据
            session = self.session_repository.get_session(session_id)
            if not session:
                logger.error(f"会话不存在: {session_id}")
                return pb2.ExtractPulseFeaturesResponse(
                    session_id = session_id,
                    success = False,
                    error_message = f"Session not found: {session_id}",
                )

            data_packets = session.get("data_packets", [])
            if not data_packets:
                logger.error(f"会话没有数据包: {session_id}")
                return pb2.ExtractPulseFeaturesResponse(
                    session_id = session_id,
                    success = False,
                    error_message = f"No data packets in session: {session_id}",
                )

            # 按位置分组数据包
            position_data = {}
            for packet in data_packets:
                position = packet.get("position", "UNKNOWN_POSITION")
                if position not in position_data:
                    position_data[position] = {
                        "pressure_data": [],
                        "velocity_data": [],
                        "timestamps": [],
                    }

                position_data[position]["pressure_data"].extend(packet.get("pressure_data", []))
                position_data[position]["velocity_data"].extend(packet.get("velocity_data", []))
                position_data[position]["timestamps"].append(packet.get("timestamp", 0))

            # 提取特征
            all_features = []
            quality_metrics = None

            # 处理每个位置的数据
            for position, data in position_data.items():
                # 跳过未知位置的数据
                if position == "UNKNOWN_POSITION":
                    continue

                # 确保有足够的数据
                pressure_data = data.get("pressure_data", [])
                if len(pressure_data) < 100:  # 至少需要100个数据点
                    logger.warning(f"位置 {position} 的数据不足: {len(pressure_data)} 点")
                    continue

                # 提取特征

                features_result = self.pulse_processor.extract_features(
                    np.array(pressure_data), position
                )

                # 获取质量指标
                if quality_metrics is None and "quality" in features_result:
                    quality = features_result.get("quality", {})
                    quality_metrics = pb2.PulseQualityMetrics(
                        signal_quality = quality.get("signal_quality", 0),
                        noise_level = quality.get("noise_level", 0),
                        is_valid = quality.get("is_valid", False),
                        quality_issues = quality.get("quality_issues", ""),
                    )

                # 转换特征为响应格式
                feature_dict = features_result.get("features", {})
                for feature_name, feature_value in feature_dict.items():
                    # 跳过标准差特征
                    if feature_name.endswith("_std"):
                        continue

                    pulse_feature = pb2.PulseFeature(
                        feature_name = feature_name,
                        feature_value = float(feature_value),
                        feature_description = self._get_feature_description(feature_name),
                        position = self._get_position_enum(position),
                    )
                    all_features.append(pulse_feature)

            # 如果没有提取到特征
            if not all_features:
                logger.error(f"未能提取到脉象特征: {session_id}")
                return pb2.ExtractPulseFeaturesResponse(
                    session_id = session_id,
                    success = False,
                    error_message = "Failed to extract pulse features from the data",
                )

            # 如果没有质量指标
            if quality_metrics is None:
                quality_metrics = pb2.PulseQualityMetrics(
                    signal_quality = 0,
                    noise_level = 1.0,
                    is_valid = False,
                    quality_issues = "Failed to assess signal quality",
                )

            # 保存特征到会话
            session["features"] = {
                "extraction_time": time.time(),
                "features": [
                    {"name": f.feature_name, "value": f.feature_value, "position": f.position}
                    for f in all_features
                ],
                "quality": {
                    "signal_quality": quality_metrics.signal_quality,
                    "noise_level": quality_metrics.noise_level,
                    "is_valid": quality_metrics.is_valid,
                    "quality_issues": quality_metrics.quality_issues,
                },
            }

            # 更新会话状态
            session["status"] = "features_extracted"

            # 保存会话
            self.session_repository.update_session(session_id, session)

            # 记录指标
            self.metrics.record_counter("pulse_features_extracted", 1)
            self.metrics.record_gauge("pulse_features_count", len(all_features))

            return pb2.ExtractPulseFeaturesResponse(
                session_id = session_id,
                features = all_features,
                quality_metrics = quality_metrics,
                success = True,
                error_message = "",
            )

        except Exception as e:
            logger.exception(f"提取脉象特征失败: {e!s}")
            self.metrics.record_counter(
                "pulse_sessions_errors", 1, {"error_type": "extract_features"}
            )

            return pb2.ExtractPulseFeaturesResponse(
                session_id = request.session_id,
                success = False,
                error_message = f"Failed to extract pulse features: {e!s}",
            )
        finally:
            # 记录延迟
            end_time = time.time()
            self.metrics.record_histogram("pulse_feature_extraction_latency", end_time - start_time)

    def _get_position_enum(int):
        """将位置名称转换为枚举值"""
        position_map = {
            "UNKNOWN_POSITION": 0,
            "CUN_LEFT": 1,
            "GUAN_LEFT": 2,
            "CHI_LEFT": 3,
            "CUN_RIGHT": 4,
            "GUAN_RIGHT": 5,
            "CHI_RIGHT": 6,
        }
        return position_map.get(position_name, 0)

    def _get_feature_description(str):
        """获取特征描述"""
        # 特征描述映射
        descriptions = {
            "main_peak_amplitude": "主波幅度",
            "main_peak_position": "主波位置",
            "rising_time": "上升时间",
            "rising_slope": "上升斜率",
            "falling_slope": "下降斜率",
            "dicrotic_peak_amplitude": "重搏波幅度",
            "dicrotic_peak_position": "重搏波位置",
            "dicrotic_ratio": "重搏波与主波比值",
            "pulse_width": "脉搏宽度",
            "area_under_curve": "曲线下面积",
            "energy": "脉象能量",
            "mean": "平均值",
            "std": "标准差",
            "skewness": "偏度",
            "kurtosis": "峰度",
            "dominant_frequency": "主频率",
            "dominant_frequency_power": "主频率能量",
            "total_power": "总能量",
            "low_frequency_ratio": "低频能量比",
            "mid_frequency_ratio": "中频能量比",
            "high_frequency_ratio": "高频能量比",
            "spectral_entropy": "频谱熵",
            "wavelet_approximation_energy": "小波近似能量",
            "wavelet_entropy": "小波熵",
        }

        # 对于小波细节能量特征
        if feature_name.startswith("wavelet_detail_") and feature_name.endswith("_energy"):
            level = feature_name.split("_")[2]
            return f"小波细节能量(级别{level})"

        return descriptions.get(feature_name, feature_name)

    def AnalyzePulse(
        self, request: pb2.AnalyzePulseRequest, context: grpc.ServicerContext
    ) - > pb2.AnalyzePulseResponse:
        """
        分析脉象

        Args:
            request: 脉象分析请求
            context: gRPC上下文

        Returns:
            脉象分析响应
        """
        start_time = time.time()

        try:
            session_id = request.session_id
            user_id = request.user_id

            # 获取会话数据
            session = self.session_repository.get_session(session_id)
            if not session:
                logger.error(f"会话不存在: {session_id}")
                return pb2.AnalyzePulseResponse(
                    session_id = session_id,
                    success = False,
                    error_message = f"Session not found: {session_id}",
                )

            # 确保有特征数据
            if "features" not in session:
                logger.error(f"会话没有特征数据: {session_id}")
                return pb2.AnalyzePulseResponse(
                    session_id = session_id,
                    success = False,
                    error_message = f"No features extracted for session: {session_id}",
                )

            # 使用脉象分析器分析
            user = self.user_repository.get_user(user_id)
            user_info = {
                "user_id": user_id,
                "age": user.get("age", 0) if user else 0,
                "gender": user.get("gender", "") if user else "",
                "health_status": user.get("health_status", {}) if user else {},
            }

            analysis_options = {
                "use_tcm_model": (
                    request.options.use_tcm_model
                    if hasattr(request, "options") and request.options
                    else True
                ),
                "use_western_model": (
                    request.options.use_western_model
                    if hasattr(request, "options") and request.options
                    else False
                ),
                "analysis_depth": (
                    request.options.analysis_depth
                    if hasattr(request, "options") and request.options
                    else "standard"
                ),
                "specific_conditions": (
                    list(request.options.specific_conditions)
                    if hasattr(request, "options") and request.options
                    else []
                ),
            }

            # 获取脉象特征
            features = session["features"]

            # 分析脉象
            analysis_result = self.pulse_analyzer.analyze_pulse(
                features = features, user_info = user_info, options = analysis_options
            )

            # 转换脉象类型
            pulse_types = []
            for pulse_type in analysis_result.get("pulse_types", []):
                enum_value = self._get_pulse_wave_type_enum(pulse_type.get("type", "UNKNOWN_WAVE"))
                pulse_types.append(enum_value)

            # 转换中医脉象模式
            tcm_patterns = []
            for pattern in analysis_result.get("tcm_patterns", []):
                tcm_pattern = pb2.TCMPulsePattern(
                    pattern_name = pattern.get("pattern_name", ""),
                    confidence = pattern.get("confidence", 0.0),
                    description = pattern.get("description", ""),
                    related_conditions = pattern.get("related_conditions", []),
                )
                tcm_patterns.append(tcm_pattern)

            # 转换脏腑状况
            organ_conditions = []
            for condition in analysis_result.get("organ_conditions", []):
                organ_condition = pb2.OrganCondition(
                    organ_name = condition.get("organ_name", ""),
                    condition = condition.get("condition", ""),
                    severity = condition.get("severity", 0.0),
                    description = condition.get("description", ""),
                )
                organ_conditions.append(organ_condition)

            # 获取分析总结和置信度
            analysis_summary = analysis_result.get("analysis_summary", "")
            confidence_score = analysis_result.get("confidence_score", 0.0)

            # 保存分析结果到会话
            session["pulse_analysis"] = {
                "analysis_time": time.time(),
                "pulse_types": [self._get_pulse_wave_type_name(pt) for pt in pulse_types],
                "tcm_patterns": [p.pattern_name for p in tcm_patterns],
                "organ_conditions": [
                    {
                        "organ_name": oc.organ_name,
                        "condition": oc.condition,
                        "severity": oc.severity,
                    }
                    for oc in organ_conditions
                ],
                "analysis_summary": analysis_summary,
                "confidence_score": confidence_score,
            }

            # 更新会话状态
            session["status"] = "pulse_analyzed"

            # 保存会话
            self.session_repository.update_session(session_id, session)

            # 记录指标
            self.metrics.record_counter("pulse_analysis_completed", 1)
            self.metrics.record_histogram("pulse_analysis_confidence", confidence_score)

            return pb2.AnalyzePulseResponse(
                session_id = session_id,
                pulse_types = pulse_types,
                tcm_patterns = tcm_patterns,
                organ_conditions = organ_conditions,
                analysis_summary = analysis_summary,
                confidence_score = confidence_score,
                success = True,
                error_message = "",
            )

        except Exception as e:
            logger.exception(f"分析脉象失败: {e!s}")
            self.metrics.record_counter("pulse_sessions_errors", 1, {"error_type": "analyze_pulse"})

            return pb2.AnalyzePulseResponse(
                session_id = request.session_id,
                success = False,
                error_message = f"Failed to analyze pulse: {e!s}",
            )
        finally:
            # 记录延迟
            end_time = time.time()
            self.metrics.record_histogram("pulse_analysis_latency", end_time - start_time)

    def _get_pulse_wave_type_enum(int):
        """将脉象类型名称转换为枚举值"""
        pulse_type_map = {
            "UNKNOWN_WAVE": 0,
            "FLOATING": 1,  # 浮脉
            "SUNKEN": 2,  # 沉脉
            "SLOW": 3,  # 迟脉
            "RAPID": 4,  # 数脉
            "SLIPPERY": 5,  # 滑脉
            "ROUGH": 6,  # 涩脉
            "WIRY": 7,  # 弦脉
            "MODERATE": 8,  # 和脉
            "FAINT": 9,  # 微脉
            "SURGING": 10,  # 洪脉
            "TIGHT": 11,  # 紧脉
            "EMPTY": 12,  # 虚脉
            "LEATHER": 13,  # 革脉
            "WEAK": 14,  # 弱脉
            "SCATTERED": 15,  # 散脉
            "INTERMITTENT": 16,  # 代脉
            "BOUND": 17,  # 结脉
            "HASTY": 18,  # 促脉
            "HIDDEN": 19,  # 伏脉
            "LONG": 20,  # 长脉
            "SHORT": 21,  # 短脉
            "THREADY": 22,  # 细脉
            "SOFT": 23,  # 软脉
            "REGULARLY_INTERMITTENT": 24,  # 结脉
            "IRREGULARLY_INTERMITTENT": 25,  # 代脉
        }
        return pulse_type_map.get(type_name, 0)

    def _get_pulse_wave_type_name(str):
        """将脉象类型枚举值转换为名称"""
        pulse_type_map = {
            0: "UNKNOWN_WAVE",
            1: "FLOATING",  # 浮脉
            2: "SUNKEN",  # 沉脉
            3: "SLOW",  # 迟脉
            4: "RAPID",  # 数脉
            5: "SLIPPERY",  # 滑脉
            6: "ROUGH",  # 涩脉
            7: "WIRY",  # 弦脉
            8: "MODERATE",  # 和脉
            9: "FAINT",  # 微脉
            10: "SURGING",  # 洪脉
            11: "TIGHT",  # 紧脉
            12: "EMPTY",  # 虚脉
            13: "LEATHER",  # 革脉
            14: "WEAK",  # 弱脉
            15: "SCATTERED",  # 散脉
            16: "INTERMITTENT",  # 代脉
            17: "BOUND",  # 结脉
            18: "HASTY",  # 促脉
            19: "HIDDEN",  # 伏脉
            20: "LONG",  # 长脉
            21: "SHORT",  # 短脉
            22: "THREADY",  # 细脉
            23: "SOFT",  # 软脉
            24: "REGULARLY_INTERMITTENT",  # 结脉
            25: "IRREGULARLY_INTERMITTENT",  # 代脉
        }
        return pulse_type_map.get(type_enum, "UNKNOWN_WAVE")

    def AnalyzeAbdominalPalpation(
        self, request: pb2.AbdominalPalpationRequest, context: grpc.ServicerContext
    ) - > pb2.AbdominalPalpationResponse:
        """
        分析腹诊数据

        Args:
            request: 腹诊分析请求
            context: gRPC上下文

        Returns:
            腹诊分析响应
        """
        start_time = time.time()

        try:
            user_id = request.user_id

            # 获取用户信息
            user = self.user_repository.get_user(user_id)
            if not user:
                logger.warning(f"用户不存在: {user_id}")

            # 转换区域数据
            regions_data = []
            for region in request.regions:
                region_data = {
                    "region_id": region.region_id,
                    "region_name": region.region_name,
                    "tenderness_level": region.tenderness_level,
                    "tension_level": region.tension_level,
                    "has_mass": region.has_mass,
                    "texture_description": region.texture_description,
                    "comments": region.comments,
                }
                regions_data.append(region_data)

            # 分析腹诊数据
            analysis_result = self.abdominal_analyzer.analyze_regions(regions_data)

            # 转换分析结果为响应格式
            findings = []
            for finding in analysis_result.get("findings", []):
                abdominal_finding = pb2.AbdominalFinding(
                    region_id = finding.get("region_id", ""),
                    finding_type = finding.get("finding_type", ""),
                    description = finding.get("description", ""),
                    confidence = finding.get("confidence", 0.0),
                    potential_causes = finding.get("potential_causes", []),
                )
                findings.append(abdominal_finding)

            # 获取分析总结
            analysis_summary = analysis_result.get("analysis_summary", "")

            # 存储分析结果
            analysis_id = str(uuid.uuid4())
            analysis_data = {
                "analysis_id": analysis_id,
                "user_id": user_id,
                "analysis_time": time.time(),
                "regions_data": regions_data,
                "findings": analysis_result.get("findings", []),
                "analysis_summary": analysis_summary,
            }

            # 保存到数据库
            self.session_repository.create_abdominal_analysis(analysis_id, analysis_data)

            # 记录指标
            self.metrics.record_counter("abdominal_analyses_completed", 1)
            self.metrics.record_gauge("abdominal_findings_count", len(findings))

            return pb2.AbdominalPalpationResponse(
                findings = findings, analysis_summary = analysis_summary, success = True, error_message = ""
            )

        except Exception as e:
            logger.exception(f"分析腹诊数据失败: {e!s}")
            self.metrics.record_counter("abdominal_analysis_errors", 1)

            return pb2.AbdominalPalpationResponse(
                success = False, error_message = f"Failed to analyze abdominal palpation data: {e!s}"
            )
        finally:
            # 记录延迟
            end_time = time.time()
            self.metrics.record_histogram("abdominal_analysis_latency", end_time - start_time)

    def AnalyzeSkinPalpation(
        self, request: pb2.SkinPalpationRequest, context: grpc.ServicerContext
    ) - > pb2.SkinPalpationResponse:
        """
        分析皮肤触诊数据

        Args:
            request: 皮肤触诊分析请求
            context: gRPC上下文

        Returns:
            皮肤触诊分析响应
        """
        start_time = time.time()

        try:
            user_id = request.user_id

            # 获取用户信息
            user = self.user_repository.get_user(user_id)
            if not user:
                logger.warning(f"用户不存在: {user_id}")

            # 转换区域数据
            regions_data = []
            for region in request.regions:
                region_data = {
                    "region_id": region.region_id,
                    "region_name": region.region_name,
                    "moisture_level": region.moisture_level,
                    "elasticity": region.elasticity,
                    "texture": region.texture,
                    "temperature": region.temperature,
                    "color": region.color,
                }
                regions_data.append(region_data)

            # 分析皮肤触诊数据
            analysis_result = self.skin_analyzer.analyze_regions(regions_data)

            # 转换分析结果为响应格式
            findings = []
            for finding in analysis_result.get("findings", []):
                skin_finding = pb2.SkinFinding(
                    region_id = finding.get("region_id", ""),
                    finding_type = finding.get("finding_type", ""),
                    description = finding.get("description", ""),
                    related_conditions = finding.get("related_conditions", []),
                )
                findings.append(skin_finding)

            # 获取分析总结
            analysis_summary = analysis_result.get("analysis_summary", "")

            # 存储分析结果
            analysis_id = str(uuid.uuid4())
            analysis_data = {
                "analysis_id": analysis_id,
                "user_id": user_id,
                "analysis_time": time.time(),
                "regions_data": regions_data,
                "findings": analysis_result.get("findings", []),
                "analysis_summary": analysis_summary,
            }

            # 保存到数据库
            self.session_repository.create_skin_analysis(analysis_id, analysis_data)

            # 记录指标
            self.metrics.record_counter("skin_analyses_completed", 1)
            self.metrics.record_gauge("skin_findings_count", len(findings))

            return pb2.SkinPalpationResponse(
                findings = findings, analysis_summary = analysis_summary, success = True, error_message = ""
            )

        except Exception as e:
            logger.exception(f"分析皮肤触诊数据失败: {e!s}")
            self.metrics.record_counter("skin_analysis_errors", 1)

            return pb2.SkinPalpationResponse(
                success = False, error_message = f"Failed to analyze skin palpation data: {e!s}"
            )
        finally:
            # 记录延迟
            end_time = time.time()
            self.metrics.record_histogram("skin_analysis_latency", end_time - start_time)

    def HealthCheck(self, request, context):
        """
        实现健康检查接口

        Args:
            request: HealthCheckRequest 包含检查级别
            context: gRPC上下文

        Returns:
            HealthCheckResponse 健康状态响应
        """
        logger.info(f"收到健康检查请求, 级别: {request.level}")
        start_time = time.time()

        response = pb2.HealthCheckResponse()
        response.version = self.version
        response.timestamp = int(time.time())

        # 检查服务自身状态
        service_component = response.components.add()
        service_component.component_name = "palpation_service"
        service_component.status = pb2.HealthCheckResponse.ServiceStatus.SERVING
        service_component.details = "服务正常运行"
        service_component.response_time_ms = 0

        # 执行数据库健康检查 (BASIC级别)
        if request.level > = pb2.HealthCheckRequest.HealthCheckLevel.BASIC:
            db_check_start = time.time()
            try:
                db_status = self._check_database_health()
                db_component = response.components.add()
                db_component.component_name = "database"
                db_component.status = pb2.HealthCheckResponse.ServiceStatus.SERVING
                db_component.details = "数据库连接正常"
                db_component.response_time_ms = int((time.time() - db_check_start) * 1000)
            except Exception as e:
                logger.error(f"数据库健康检查失败: {e}")
                db_component = response.components.add()
                db_component.component_name = "database"
                db_component.status = pb2.HealthCheckResponse.ServiceStatus.NOT_SERVING
                db_component.details = f"数据库连接失败: {e!s}"
                db_component.response_time_ms = int((time.time() - db_check_start) * 1000)

                # 如果数据库不可用，整个服务标记为不可用
                response.status = pb2.HealthCheckResponse.ServiceStatus.NOT_SERVING
                return response

        # 执行全面检查 (FULL级别)
        if request.level == pb2.HealthCheckRequest.HealthCheckLevel.FULL:
            # 检查集成服务连接
            integration_names = ["xiaoai_service", "rag_service"]
            for integration_name in integration_names:
                integration_check_start = time.time()
                try:
                    integration_status = self._check_integration_health(integration_name)
                    integration_component = response.components.add()
                    integration_component.component_name = integration_name

                    if integration_status:
                        integration_component.status = pb2.HealthCheckResponse.ServiceStatus.SERVING
                        integration_component.details = f"{integration_name} 连接正常"
                    else:
                        integration_component.status = (
                            pb2.HealthCheckResponse.ServiceStatus.SERVICE_UNKNOWN
                        )
                        integration_component.details = f"{integration_name} 服务状态未知"

                    integration_component.response_time_ms = int(
                        (time.time() - integration_check_start) * 1000
                    )
                except Exception as e:
                    logger.warning(f"{integration_name} 健康检查失败: {e}")
                    integration_component = response.components.add()
                    integration_component.component_name = integration_name
                    integration_component.status = pb2.HealthCheckResponse.ServiceStatus.NOT_SERVING
                    integration_component.details = f"{integration_name} 连接失败: {e!s}"
                    integration_component.response_time_ms = int(
                        (time.time() - integration_check_start) * 1000
                    )

            # 检查模型可用性
            model_check_start = time.time()
            try:
                model_status = self._check_models_health()
                model_component = response.components.add()
                model_component.component_name = "ml_models"
                model_component.status = pb2.HealthCheckResponse.ServiceStatus.SERVING
                model_component.details = "模型加载正常"
                model_component.response_time_ms = int((time.time() - model_check_start) * 1000)
            except Exception as e:
                logger.error(f"模型健康检查失败: {e}")
                model_component = response.components.add()
                model_component.component_name = "ml_models"
                model_component.status = pb2.HealthCheckResponse.ServiceStatus.NOT_SERVING
                model_component.details = f"模型加载失败: {e!s}"
                model_component.response_time_ms = int((time.time() - model_check_start) * 1000)

                # 如果核心模型不可用，服务可能无法正常工作
                response.status = pb2.HealthCheckResponse.ServiceStatus.NOT_SERVING
                return response

        # 设置总体服务状态
        response.status = pb2.HealthCheckResponse.ServiceStatus.SERVING

        # 记录总响应时间
        total_time_ms = int((time.time() - start_time) * 1000)
        logger.info(f"健康检查完成，耗时: {total_time_ms}ms, 状态: {response.status}")

        return response

    def _check_database_health(None):
        """检查数据库健康状态"""
        try:
            # 执行简单查询，验证数据库连接
            self.session_repository.ping()
            self.user_repository.ping()
            return True
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            raise

    def _check_integration_health(self, integration_name):
        """检查集成服务健康状态"""
        try:
            # TODO: 实现实际的集成服务健康检查
            # 这里是简化实现，实际应该调用各服务的健康检查接口
            return True
        except Exception as e:
            logger.warning(f"集成服务 {integration_name} 健康检查失败: {e}")
            return False

    def _check_models_health(None):
        """检查模型健康状态"""
        try:
            # 验证脉诊处理器模型加载状态
            self.pulse_processor.check_model_loaded()

            # 验证腹诊分析器模型加载状态
            self.abdominal_analyzer.check_model_loaded()

            # 验证皮肤分析器模型加载状态
            self.skin_analyzer.check_model_loaded()

            return True
        except Exception as e:
            logger.error(f"模型健康检查失败: {e}")
            raise
