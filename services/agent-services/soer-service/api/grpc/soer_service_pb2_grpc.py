"""gRPC服务存根生成代码"""

import grpc

from . import soer_service_pb2 as soer_service_pb2


class SoerServiceStub:
    """索儿服务的客户端存根"""

    def __init__(self, channel):
        """构造函数

        Args:
            channel: 用于gRPC通信的Channel
        """
        self.GenerateHealthPlan = channel.unary_unary(
            '/suoke.soer.v1.SoerService/GenerateHealthPlan',
            request_serializer=soer_service_pb2.HealthPlanRequest.SerializeToString,
            response_deserializer=soer_service_pb2.HealthPlanResponse.FromString,
        )
        self.GetLifestyleRecommendation = channel.unary_unary(
            '/suoke.soer.v1.SoerService/GetLifestyleRecommendation',
            request_serializer=soer_service_pb2.LifestyleRequest.SerializeToString,
            response_deserializer=soer_service_pb2.LifestyleResponse.FromString,
        )
        self.AnalyzeSensorData = channel.unary_unary(
            '/suoke.soer.v1.SoerService/AnalyzeSensorData',
            request_serializer=soer_service_pb2.SensorDataRequest.SerializeToString,
            response_deserializer=soer_service_pb2.SensorDataResponse.FromString,
        )
        self.TrackNutrition = channel.unary_unary(
            '/suoke.soer.v1.SoerService/TrackNutrition',
            request_serializer=soer_service_pb2.NutritionRequest.SerializeToString,
            response_deserializer=soer_service_pb2.NutritionResponse.FromString,
        )
        self.DetectAbnormalPattern = channel.unary_unary(
            '/suoke.soer.v1.SoerService/DetectAbnormalPattern',
            request_serializer=soer_service_pb2.AbnormalPatternRequest.SerializeToString,
            response_deserializer=soer_service_pb2.AbnormalPatternResponse.FromString,
        )
        self.PredictHealthTrend = channel.unary_unary(
            '/suoke.soer.v1.SoerService/PredictHealthTrend',
            request_serializer=soer_service_pb2.HealthTrendRequest.SerializeToString,
            response_deserializer=soer_service_pb2.HealthTrendResponse.FromString,
        )
        self.GetSleepRecommendation = channel.unary_unary(
            '/suoke.soer.v1.SoerService/GetSleepRecommendation',
            request_serializer=soer_service_pb2.SleepRequest.SerializeToString,
            response_deserializer=soer_service_pb2.SleepResponse.FromString,
        )
        self.AnalyzeEmotionalState = channel.unary_unary(
            '/suoke.soer.v1.SoerService/AnalyzeEmotionalState',
            request_serializer=soer_service_pb2.EmotionalStateRequest.SerializeToString,
            response_deserializer=soer_service_pb2.EmotionalStateResponse.FromString,
        )


class SoerServiceServicer:
    """索儿服务的服务器端实现接口"""

    def GenerateHealthPlan(self, request, context):
        """生成个性化健康计划"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('方法 GenerateHealthPlan 未实现')
        raise NotImplementedError('方法 GenerateHealthPlan 未实现')

    def GetLifestyleRecommendation(self, request, context):
        """获取生活方式建议"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('方法 GetLifestyleRecommendation 未实现')
        raise NotImplementedError('方法 GetLifestyleRecommendation 未实现')

    def AnalyzeSensorData(self, request, context):
        """分析传感器数据"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('方法 AnalyzeSensorData 未实现')
        raise NotImplementedError('方法 AnalyzeSensorData 未实现')

    def TrackNutrition(self, request, context):
        """追踪并分析用户营养摄入"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('方法 TrackNutrition 未实现')
        raise NotImplementedError('方法 TrackNutrition 未实现')

    def DetectAbnormalPattern(self, request, context):
        """检测异常健康模式"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('方法 DetectAbnormalPattern 未实现')
        raise NotImplementedError('方法 DetectAbnormalPattern 未实现')

    def PredictHealthTrend(self, request, context):
        """预测健康趋势"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('方法 PredictHealthTrend 未实现')
        raise NotImplementedError('方法 PredictHealthTrend 未实现')

    def GetSleepRecommendation(self, request, context):
        """获取个性化睡眠建议"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('方法 GetSleepRecommendation 未实现')
        raise NotImplementedError('方法 GetSleepRecommendation 未实现')

    def AnalyzeEmotionalState(self, request, context):
        """分析情绪状态"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('方法 AnalyzeEmotionalState 未实现')
        raise NotImplementedError('方法 AnalyzeEmotionalState 未实现')


def add_SoerServiceServicer_to_server(servicer, server):
    """将Servicer添加到服务器"""
    rpc_method_handlers = {
        'GenerateHealthPlan': grpc.unary_unary_rpc_method_handler(
            servicer.GenerateHealthPlan,
            request_deserializer=soer_service_pb2.HealthPlanRequest.FromString,
            response_serializer=soer_service_pb2.HealthPlanResponse.SerializeToString,
        ),
        'GetLifestyleRecommendation': grpc.unary_unary_rpc_method_handler(
            servicer.GetLifestyleRecommendation,
            request_deserializer=soer_service_pb2.LifestyleRequest.FromString,
            response_serializer=soer_service_pb2.LifestyleResponse.SerializeToString,
        ),
        'AnalyzeSensorData': grpc.unary_unary_rpc_method_handler(
            servicer.AnalyzeSensorData,
            request_deserializer=soer_service_pb2.SensorDataRequest.FromString,
            response_serializer=soer_service_pb2.SensorDataResponse.SerializeToString,
        ),
        'TrackNutrition': grpc.unary_unary_rpc_method_handler(
            servicer.TrackNutrition,
            request_deserializer=soer_service_pb2.NutritionRequest.FromString,
            response_serializer=soer_service_pb2.NutritionResponse.SerializeToString,
        ),
        'DetectAbnormalPattern': grpc.unary_unary_rpc_method_handler(
            servicer.DetectAbnormalPattern,
            request_deserializer=soer_service_pb2.AbnormalPatternRequest.FromString,
            response_serializer=soer_service_pb2.AbnormalPatternResponse.SerializeToString,
        ),
        'PredictHealthTrend': grpc.unary_unary_rpc_method_handler(
            servicer.PredictHealthTrend,
            request_deserializer=soer_service_pb2.HealthTrendRequest.FromString,
            response_serializer=soer_service_pb2.HealthTrendResponse.SerializeToString,
        ),
        'GetSleepRecommendation': grpc.unary_unary_rpc_method_handler(
            servicer.GetSleepRecommendation,
            request_deserializer=soer_service_pb2.SleepRequest.FromString,
            response_serializer=soer_service_pb2.SleepResponse.SerializeToString,
        ),
        'AnalyzeEmotionalState': grpc.unary_unary_rpc_method_handler(
            servicer.AnalyzeEmotionalState,
            request_deserializer=soer_service_pb2.EmotionalStateRequest.FromString,
            response_serializer=soer_service_pb2.EmotionalStateResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'suoke.soer.v1.SoerService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
