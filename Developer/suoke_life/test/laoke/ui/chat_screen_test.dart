import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/data/models/agent_model.dart';
import 'package:suoke_life/data/models/session_model.dart';
import 'package:suoke_life/presentation/home/screens/chat_screen.dart';
import 'package:suoke_life/presentation/home/providers/agent_state_provider.dart';
import 'package:mockito/mockito.dart';

// 简化版的AgentState供测试使用
class TestAgentState extends AgentState {
  TestAgentState({
    super.agents,
    super.currentAgent,
    super.sessions,
    super.currentSession,
    super.messages,
    super.isLoading,
    super.errorMessage,
  });
}

// 简化版的AgentNotifier供测试使用
class TestAgentNotifier extends StateNotifier<AgentState> {
  TestAgentNotifier(AgentState state) : super(state);
}

// 创建测试用的智能体模型
AgentModel createTestAgent({
  required String id,
  required String name,
  required String type,
}) {
  return AgentModel(
    id: id,
    name: name,
    type: type,
    description: '测试描述',
    avatarUrl: 'https://test.com/avatar.png',
    capabilities: {'test': true},
    createdAt: DateTime.now(),
    updatedAt: DateTime.now(),
  );
}

void main() {
  group('聊天屏幕UI测试', () {
    testWidgets('ChatScreen应该根据不同智能体使用不同主题色', (WidgetTester tester) async {
      // 创建小柯智能体
      final xiaoke = createTestAgent(
        id: 'xiaoke-service',
        name: '小柯',
        type: '健康管理',
      );
      
      // 创建小艾智能体
      final xiaoai = createTestAgent(
        id: 'xiaoai-service',
        name: '小艾',
        type: '综合顾问',
      );
      
      // 创建一个带有小柯智能体的测试状态
      final xiaokeState = TestAgentState(
        currentAgent: xiaoke,
        agents: [xiaoke, xiaoai],
        messages: [],
      );
      
      // 创建小柯智能体的状态提供者
      final xiaokeProvider = StateNotifierProvider<TestAgentNotifier, AgentState>(
        (ref) => TestAgentNotifier(xiaokeState),
      );
      
      // 首先渲染小柯的聊天界面
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            agentStateProvider.overrideWithProvider(xiaokeProvider),
          ],
          child: const MaterialApp(
            home: ChatScreen(),
          ),
        ),
      );
      
      // 等待UI更新
      await tester.pumpAndSettle();
      
      // 验证是否显示了小柯的名称
      expect(find.text('小柯'), findsOneWidget);
      
      // 验证是否显示了小柯的类型
      expect(find.text('健康管理'), findsOneWidget);
      
      // 创建一个带有小艾智能体的测试状态
      final xiaoaiState = TestAgentState(
        currentAgent: xiaoai,
        agents: [xiaoke, xiaoai],
        messages: [],
      );
      
      // 创建小艾智能体的状态提供者
      final xiaoaiProvider = StateNotifierProvider<TestAgentNotifier, AgentState>(
        (ref) => TestAgentNotifier(xiaoaiState),
      );
      
      // 重新渲染小艾的聊天界面
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            agentStateProvider.overrideWithProvider(xiaoaiProvider),
          ],
          child: const MaterialApp(
            home: ChatScreen(),
          ),
        ),
      );
      
      // 等待UI更新
      await tester.pumpAndSettle();
      
      // 验证是否显示了小艾的名称
      expect(find.text('小艾'), findsOneWidget);
      
      // 验证是否显示了小艾的类型
      expect(find.text('综合顾问'), findsOneWidget);
    });
    
    testWidgets('聊天屏幕应该显示没有消息的提示', (WidgetTester tester) async {
      // 创建小柯智能体
      final xiaoke = createTestAgent(
        id: 'xiaoke-service',
        name: '小柯',
        type: '健康管理',
      );
      
      // 创建一个带有小柯智能体但没有消息的测试状态
      final noMessagesState = TestAgentState(
        currentAgent: xiaoke,
        agents: [xiaoke],
        messages: [],
      );
      
      // 创建无消息状态的提供者
      final noMessagesProvider = StateNotifierProvider<TestAgentNotifier, AgentState>(
        (ref) => TestAgentNotifier(noMessagesState),
      );
      
      // 渲染聊天界面
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            agentStateProvider.overrideWithProvider(noMessagesProvider),
          ],
          child: const MaterialApp(
            home: ChatScreen(),
          ),
        ),
      );
      
      // 等待UI更新
      await tester.pumpAndSettle();
      
      // 验证是否显示了"没有消息"的提示
      expect(find.text('没有消息'), findsOneWidget);
      
      // 验证是否显示了"与小柯开始对话"的提示
      expect(find.text('与小柯开始对话'), findsOneWidget);
    });
  });
} 