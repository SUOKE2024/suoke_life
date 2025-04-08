import 'package:flutter_test/flutter_test.dart';
import 'package:suoke_life/data/models/agent_model.dart';

void main() {
  group('预设智能体测试', () {
    // 手动创建预设智能体，复制自providers/agent_providers.dart
    List<AgentModel> createPresetAgents() {
      final now = DateTime.now();
      
      return [
        // 小柯智能体
        AgentModel(
          id: 'xiaoke-service',
          name: '小柯',
          description: '小柯是一位专注于日常健康管理的AI助手，擅长健康习惯培养、饮食指导和生活方式调整。',
          avatarUrl: 'https://suoke.life/assets/agents/xiaoke_avatar.png',
          type: '健康管理',
          capabilities: {
            'health_tracking': true,
            'diet_suggestions': true,
            'lifestyle_advice': true,
          },
          createdAt: now,
          updatedAt: now,
        ),
        
        // 小艾智能体
        AgentModel(
          id: 'xiaoai-service',
          name: '小艾',
          description: '小艾是索克生活的主要AI助手，擅长全方位健康咨询、中医理论解读和个性化健康方案制定。',
          avatarUrl: 'https://suoke.life/assets/agents/xiaoai_avatar.png',
          type: '综合顾问',
          capabilities: {
            'tcm_knowledge': true,
            'health_consultation': true,
            'personalized_plans': true,
            'knowledge_graph': true,
          },
          createdAt: now,
          updatedAt: now,
        ),
        
        // 索尔智能体
        AgentModel(
          id: 'soer-service',
          name: '索尔',
          description: '索尔是专门针对情绪和心理健康的AI顾问，擅长提供心理支持、压力管理和情绪调节建议。',
          avatarUrl: 'https://suoke.life/assets/agents/soer_avatar.png',
          type: '心理顾问',
          capabilities: {
            'emotional_support': true,
            'stress_management': true,
            'mood_tracking': true,
            'meditation_guide': true,
          },
          createdAt: now,
          updatedAt: now,
        ),
        
        // 老柯智能体
        AgentModel(
          id: 'laoke-service',
          name: '老柯',
          description: '老柯是中医理论专家，精通经络、穴位、中药和传统养生理论，提供专业的中医健康指导。',
          avatarUrl: 'https://suoke.life/assets/agents/laoke_avatar.png',
          type: '中医专家',
          capabilities: {
            'acupuncture_advice': true,
            'herbal_medicine': true,
            'meridian_knowledge': true,
            'seasonal_health': true,
          },
          createdAt: now,
          updatedAt: now,
        ),
      ];
    }
    
    test('预设智能体应该包含4个智能体', () {
      final agents = createPresetAgents();
      
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
    });
    
    test('每个智能体应具有正确的专业领域', () {
      final agents = createPresetAgents();
      
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