import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/data/models/agent_model.dart';
import 'package:suoke_life/di/providers/agent_providers.dart';
import 'package:suoke_life/presentation/home/pages/home_page.dart';
import 'package:mockito/mockito.dart';

// 简化版的AgentModel供测试使用
AgentModel createTestAgent({
  required String id,
  required String name,
  required String type,
  required String description,
}) {
  return AgentModel(
    id: id,
    name: name,
    type: type,
    description: description,
    avatarUrl: 'https://test.com/avatar.png',
    capabilities: {'test_capability': true},
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  );
}

// 用于测试的Agent列表提供者覆盖
final testAgentsProvider = Provider<List<AgentModel>>((ref) {
  return [
    createTestAgent(
      id: 'xiaoke-service',
      name: '小柯',
      type: '健康管理',
      description: '这是测试描述',
    ),
    createTestAgent(
      id: 'xiaoai-service',
      name: '小艾',
      type: '综合顾问',
      description: '这是测试描述',
    ),
  ];
});

void main() {
  group('智能体服务卡片测试', () {
    testWidgets('HomePage应该正确显示智能体服务卡片', (WidgetTester tester) async {
      // 创建一个ProviderScope，覆盖预设智能体提供者
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            presetAgentsProvider.overrideWithProvider(testAgentsProvider),
          ],
          child: const MaterialApp(
            home: HomePage(),
          ),
        ),
      );
      
      // 等待异步操作完成
      await tester.pumpAndSettle();
      
      // 验证是否正确显示了"索克智能体"标题
      expect(find.text('索克智能体'), findsOneWidget);
      
      // 验证是否显示了测试智能体的名称
      expect(find.text('小柯'), findsOneWidget);
      expect(find.text('小艾'), findsOneWidget);
      
      // 验证是否显示了测试智能体的类型
      expect(find.text('健康管理'), findsOneWidget);
      expect(find.text('综合顾问'), findsOneWidget);
      
      // 验证是否显示了"开始对话"按钮
      expect(find.text('开始对话'), findsNWidgets(2));
    });
  });
} 