import 'package:flutter/foundation.dart';
import '../../../models/chat_message.dart';
import '../../../services/ai/ai_service.dart';
import '../../../intelligence/core/types.dart';
import '../../../intelligence/core/base_assistant.dart';
import '../../../intelligence/core/exceptions.dart';

class XiaoiService extends BaseAssistant {
  // 小艾特定配置
  static const Map<String, dynamic> _xiaoiConfig = {
    'role': 'health_assistant',
    'personality': 'friendly',
    'expertise': ['health', 'medical', 'wellness'],
    'language_style': 'professional_casual',
    'response_format': 'structured',
  };

  XiaoiService({
    required super.aiService,
    required super.sessionManager,
    required super.contextManager,
    required super.errorHandler,
    required super.validator,
    required super.analysisService,
  }) : super(
    assistantName: 'xiaoi',
    defaultModel: 'xiaoi_v1',
    defaultConfig: _xiaoiConfig,
  );

  @override
  Future<void> initialize() async {
    // 初始化健康知识库
    await _initHealthKnowledgeBase();
  }

  Future<void> _initHealthKnowledgeBase() async {
    // 实现健康知识库初始化
  }

  @override
  Future<void> warmup() async {
    // 预热健康咨询模型
    // 缓存常用医疗术语
    // 准备快速响应模板
  }

  @override
  Future<bool> validate() async {
    // 验证医疗知识库完整性
    // 检查必要资源可用性
    // 确认服务就绪状态
    return true;
  }

  @override
  Future<Map<String, dynamic>> getCapabilities() async {
    return {
      'expertise': ['health_consultation', 'medical_knowledge', 'wellness_advice'],
      'languages': ['zh-CN', 'en'],
      'features': [
        'symptom_analysis',
        'health_education',
        'medication_guidance',
      ],
      'limitations': [
        'no_diagnosis',
        'no_prescription',
        'no_emergency_service',
      ],
    };
  }
} 