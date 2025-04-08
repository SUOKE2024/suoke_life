// AI服务提供者
// 用于注册和获取AI模型提供商服务

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import '../../ai_agents/services/model_provider_adapter.dart';
import '../../ai_agents/services/providers/baidu_provider_adapter.dart';
import '../../core/utils/config.dart';
import 'dart:typed_data';
import 'package:suoke_life/core/native/tongue_analysis_bridge.dart';

/// 模型提供商类型提供者
final modelProviderTypeProvider = StateProvider<ModelProviderType>((ref) {
  // 默认使用百度文心一言
  return ModelProviderType.baidu;
});

/// 模型提供商适配器提供者
final modelProviderAdapterProvider = Provider<ModelProviderAdapter>((ref) {
  final providerType = ref.watch(modelProviderTypeProvider);
  
  switch (providerType) {
    case ModelProviderType.baidu:
      return BaiduProviderAdapter(
        apiKey: AppConfig.baiduApiKey,
        secretKey: AppConfig.baiduSecretKey,
        client: http.Client(),
      );
    case ModelProviderType.ali:
      // TODO: 实现阿里通义千问适配器
      throw UnimplementedError('阿里通义千问适配器未实现');
    case ModelProviderType.xunfei:
      // TODO: 实现讯飞星火适配器
      throw UnimplementedError('讯飞星火适配器未实现');
    case ModelProviderType.zhipu:
      // TODO: 实现智谱ChatGLM适配器
      throw UnimplementedError('智谱ChatGLM适配器未实现');
    case ModelProviderType.deepseek:
      // TODO: 实现DeepSeek适配器
      throw UnimplementedError('DeepSeek适配器未实现');
    case ModelProviderType.openai:
      // TODO: 实现OpenAI适配器(国际版，需要代理)
      throw UnimplementedError('OpenAI适配器未实现');
    case ModelProviderType.local:
      // TODO: 实现本地模型适配器
      throw UnimplementedError('本地模型适配器未实现');
  }
});

/// 模型提供商名称提供者
final modelProviderNameProvider = Provider<String>((ref) {
  final adapter = ref.watch(modelProviderAdapterProvider);
  return adapter.providerName;
});

/// 支持的模型列表提供者
final supportedModelsProvider = Provider<List<String>>((ref) {
  final adapter = ref.watch(modelProviderAdapterProvider);
  return adapter.getSupportedModels();
});

/// 当前选择的模型提供者
final selectedModelProvider = StateProvider<String>((ref) {
  final models = ref.watch(supportedModelsProvider);
  // 返回第一个可用模型，如果没有则返回空字符串
  return models.isNotEmpty ? models.first : '';
});

/// 生成嵌入向量提供者
final generateEmbeddingProvider = Provider.family<Future<List<double>>, String>(
  (ref, text) {
    final adapter = ref.watch(modelProviderAdapterProvider);
    final selectedModel = ref.watch(selectedModelProvider);
    
    return adapter.generateEmbedding(
      text: text,
      modelName: selectedModel,
    );
  },
);

/// 聊天完成提供者 (Future)
final chatCompletionProvider = FutureProvider.family<AgentResponse, ChatCompletionParams>(
  (ref, params) async {
    final adapter = ref.watch(modelProviderAdapterProvider);
    
    return adapter.chatCompletion(
      messages: params.messages,
      options: params.options,
      timeout: params.timeout,
      retries: params.retries,
    );
  },
);

/// 聊天完成参数
class ChatCompletionParams {
  final List<AgentMessage> messages;
  final ModelCallOptions options;
  final Duration timeout;
  final int retries;
  
  const ChatCompletionParams({
    required this.messages,
    required this.options,
    this.timeout = const Duration(seconds: 30),
    this.retries = 3,
  });
  
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    
    return other is ChatCompletionParams &&
        listEquals(other.messages, messages) &&
        other.options == options &&
        other.timeout == timeout &&
        other.retries == retries;
  }
  
  @override
  int get hashCode {
    return Object.hash(
      Object.hashAll(messages),
      options,
      timeout,
      retries,
    );
  }
}

/// 列表比较工具函数
bool listEquals<T>(List<T>? a, List<T>? b) {
  if (a == null) return b == null;
  if (b == null || a.length != b.length) return false;
  for (int i = 0; i < a.length; i++) {
    if (a[i] != b[i]) return false;
  }
  return true;
}

/// 舌像分析服务提供者
final tongueAnalysisProvider = Provider<TongueAnalysisService>((ref) {
  return TongueAnalysisService();
});

/// 舌像分析结果状态提供者
final tongueAnalysisResultProvider = StateProvider<AsyncValue<TongueAnalysisResult?>>((ref) {
  return const AsyncValue.data(null);
});

/// 舌像分析服务
class TongueAnalysisService {
  final _bridge = TongueAnalysisBridge();
  
  TongueAnalysisService() {
    _bridge.initialize();
  }
  
  /// 分析舌像
  Future<TongueAnalysisResult> analyzeImage(Uint8List imageData) async {
    return await _bridge.analyzeTongueImage(imageData);
  }
} 