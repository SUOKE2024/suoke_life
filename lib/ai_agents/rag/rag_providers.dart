import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'rag_service.dart';
import '../models/embedding.dart';
import '../../domain/repositories/vector_store_repository.dart';
import '../../domain/repositories/knowledge_repository.dart';
import '../../di/providers.dart';

/// RAG服务提供者
final ragServiceProvider = Provider<RAGService>((ref) {
  final vectorStoreRepository = ref.watch(vectorStoreRepositoryProvider);
  final knowledgeRepository = ref.watch(knowledgeRepositoryProvider);
  
  return DefaultRAGService(
    vectorStoreRepository: vectorStoreRepository,
    knowledgeRepository: knowledgeRepository,
  );
});

/// 向量存储库提供者
final vectorStoreRepositoryProvider = Provider<VectorStoreRepository>((ref) {
  final databaseHelper = ref.watch(databaseHelperProvider);
  final secureStorage = ref.watch(secureStorageServiceProvider);
  
  return LocalVectorStoreRepository(databaseHelper, secureStorage);
});

/// 知识库存储库提供者
final knowledgeRepositoryProvider = Provider<KnowledgeRepository>((ref) {
  final databaseHelper = ref.watch(databaseHelperProvider);
  final apiClient = ref.watch(apiClientProvider);
  
  return LocalKnowledgeRepository(databaseHelper, apiClient);
});

/// RAG查询结果提供者，用于异步获取查询结果
final ragQueryResultProvider = FutureProvider.family<List<RAGResult>, RAGQuery>(
  (ref, query) async {
    final ragService = ref.watch(ragServiceProvider);
    return await ragService.query(
      query.text,
      type: query.type,
      limit: query.limit,
      filter: query.filter,
    );
  },
);

/// RAG会话提供者，管理对话会话状态
final ragSessionProvider = StateNotifierProvider<RAGSessionNotifier, RAGSession>(
  (ref) => RAGSessionNotifier(ref),
);

/// RAG会话通知器
class RAGSessionNotifier extends StateNotifier<RAGSession> {
  final Ref ref;
  
  RAGSessionNotifier(this.ref) : super(RAGSession(
    id: DateTime.now().millisecondsSinceEpoch.toString(),
    messages: [],
    context: {},
  ));
  
  /// 添加用户消息
  Future<void> addUserMessage(String message) async {
    final now = DateTime.now();
    
    state = state.copyWith(
      messages: [
        ...state.messages,
        RAGMessage(
          role: 'user',
          content: message,
          timestamp: now,
        ),
      ],
    );
    
    // 获取AI响应
    await _getAIResponse(message);
  }
  
  /// 清除会话
  void clearSession() {
    state = RAGSession(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      messages: [],
      context: {},
    );
  }
  
  /// 获取AI响应
  Future<void> _getAIResponse(String userMessage) async {
    try {
      // 1. 创建处理中的消息状态
      final now = DateTime.now();
      state = state.copyWith(
        messages: [
          ...state.messages,
          RAGMessage(
            role: 'assistant',
            content: '正在思考...',
            timestamp: now,
            isLoading: true,
          ),
        ],
      );
      
      // 2. 使用RAG服务获取查询结果
      final ragService = ref.read(ragServiceProvider);
      final ragResults = await ragService.query(
        userMessage,
        type: RAGType.decompositionRetrieval,
        limit: 5,
      );
      
      // 3. 生成AI响应（这里简化处理，实际应调用LLM服务）
      String aiResponse = '';
      if (ragResults.isNotEmpty) {
        aiResponse = '根据我的知识库，我找到了以下相关信息：\n\n';
        for (final result in ragResults) {
          aiResponse += '• ${result.content}\n\n';
        }
      } else {
        aiResponse = '很抱歉，我在知识库中没有找到相关信息。请尝试用不同的方式提问，或者让我了解更多上下文。';
      }
      
      // 4. 更新消息状态
      final messages = [...state.messages];
      messages.removeLast(); // 删除处理中的消息
      
      state = state.copyWith(
        messages: [
          ...messages,
          RAGMessage(
            role: 'assistant',
            content: aiResponse,
            timestamp: DateTime.now(),
            isLoading: false,
          ),
        ],
      );
    } catch (e) {
      // 处理错误
      final messages = [...state.messages];
      messages.removeLast(); // 删除处理中的消息
      
      state = state.copyWith(
        messages: [
          ...messages,
          RAGMessage(
            role: 'assistant',
            content: '抱歉，处理您的请求时出现了错误。请稍后再试。',
            timestamp: DateTime.now(),
            isLoading: false,
            error: e.toString(),
          ),
        ],
      );
    }
  }
}

/// RAG查询参数类
class RAGQuery {
  final String text;
  final RAGType type;
  final int limit;
  final Map<String, dynamic>? filter;
  
  RAGQuery({
    required this.text,
    this.type = RAGType.directRetrieval,
    this.limit = 5,
    this.filter,
  });
}

/// RAG会话类
class RAGSession {
  final String id;
  final List<RAGMessage> messages;
  final Map<String, dynamic> context;
  
  RAGSession({
    required this.id,
    required this.messages,
    required this.context,
  });
  
  RAGSession copyWith({
    String? id,
    List<RAGMessage>? messages,
    Map<String, dynamic>? context,
  }) {
    return RAGSession(
      id: id ?? this.id,
      messages: messages ?? this.messages,
      context: context ?? this.context,
    );
  }
}

/// RAG消息类
class RAGMessage {
  final String role;  // 'user' 或 'assistant'
  final String content;
  final DateTime timestamp;
  final bool isLoading;
  final String? error;
  
  RAGMessage({
    required this.role,
    required this.content,
    required this.timestamp,
    this.isLoading = false,
    this.error,
  });
} 