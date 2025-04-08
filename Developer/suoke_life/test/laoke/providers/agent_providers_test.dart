import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_life/data/models/agent_model.dart';
import 'package:suoke_life/di/providers/agent_providers.dart';

void main() {
  group('智能体提供者测试', () {
    late ProviderContainer container;

    setUp(() {
      container = ProviderContainer();
    });

    tearDown(() {
      container.dispose();
    });

    test('预设智能体提供者应该返回4个智能体', () {
      // 获取预设智能体列表
      final agents = container.read(presetAgentsProvider);
      
      // 验证返回了4个预设智能体
      expect(agents.length, 4);
      
      // 验证每个智能体都有正确的ID
      expect(agents.map((a) => a.id).toList(), [
        'xiaoke-service',
        'xiaoai-service',
        'soer-service',
        'laoke-service',
      ]);
      
      // 验证每个智能体的名称
      expect(agents.map((a) => a.name).toList(), ['小柯', '小艾', '索尔', '老柯']);
      
      // 验证每个智能体都有类型
      expect(agents.every((a) => a.type.isNotEmpty), true);
      
      // 验证每个智能体都有描述
      expect(agents.every((a) => a.description.isNotEmpty), true);
      
      // 验证每个智能体都有能力
      expect(agents.every((a) => a.capabilities.isNotEmpty), true);
    });

    test('每个智能体应具有正确的专业领域', () {
      final agents = container.read(presetAgentsProvider);
      
      // 测试特定智能体的专业领域
      final xiaoke = agents.firstWhere((a) => a.id == 'xiaoke-service');
      expect(xiaoke.type, '健康管理');
      expect(xiaoke.capabilities.containsKey('health_tracking'), true);
      
      final xiaoai = agents.firstWhere((a) => a.id == 'xiaoai-service');
      expect(xiaoai.type, '综合顾问');
      expect(xiaoai.capabilities.containsKey('knowledge_graph'), true);
      
      final soer = agents.firstWhere((a) => a.id == 'soer-service');
      expect(soer.type, '心理顾问');
      expect(soer.capabilities.containsKey('emotional_support'), true);
      
      final laoke = agents.firstWhere((a) => a.id == 'laoke-service');
      expect(laoke.type, '中医专家');
      expect(laoke.capabilities.containsKey('herbal_medicine'), true);
    });
  });
} 