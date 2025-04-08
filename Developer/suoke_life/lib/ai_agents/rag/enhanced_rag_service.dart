// 增强版RAG服务
// 使用模型提供商适配器实现高级知识检索功能

import 'dart:async';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import '../models/agent_message.dart';
import '../models/agent_response.dart';
import '../services/model_provider_adapter.dart';
import '../utils/logger.dart';
import '../../core/utils/config.dart';

/// 嵌入向量
class EmbeddingVector {
  /// 向量ID
  final String id;
  
  /// 向量值
  final List<double> vector;
  
  /// 文本内容
  final String text;
  
  /// 元数据
  final Map<String, dynamic>? metadata;
  
  /// 构造函数
  const EmbeddingVector({
    required this.id,
    required this.vector,
    required this.text,
    this.metadata,
  });
}

/// 检索结果
class RetrievalResult {
  /// 文档ID
  final String id;
  
  /// 文档内容
  final String content;
  
  /// 文档来源
  final String source;
  
  /// 相似度得分
  final double score;
  
  /// 元数据
  final Map<String, dynamic>? metadata;
  
  /// 构造函数
  const RetrievalResult({
    required this.id,
    required this.content,
    required this.source,
    required this.score,
    this.metadata,
  });
}

/// 增强版RAG服务
class EnhancedRagService {
  /// HTTP客户端
  final http.Client _client;
  
  /// 模型提供商适配器
  final ModelProviderAdapter _modelProvider;
  
  /// RAG服务基础URL
  final String _ragServiceUrl;
  
  /// 构造函数
  EnhancedRagService({
    required ModelProviderAdapter modelProvider,
    http.Client? client,
    String? ragServiceUrl,
  }) : 
    _modelProvider = modelProvider,
    _client = client ?? http.Client(),
    _ragServiceUrl = ragServiceUrl ?? '${AppConfig.apiBaseUrl}/rag';
  
  /// 生成问题的嵌入向量
  Future<List<double>> generateEmbedding(String text) async {
    try {
      return await _modelProvider.generateEmbedding(text: text);
    } catch (e) {
      LoggerUtil.error('生成嵌入向量异常: ${e.toString()}');
      throw Exception('生成嵌入向量失败: ${e.toString()}');
    }
  }
  
  /// 基于嵌入向量搜索知识库
  Future<List<RetrievalResult>> searchKnowledgeBase({
    required List<double> embedding,
    required String collection,
    int limit = 5,
    double minScore = 0.7,
    Map<String, dynamic>? filter,
  }) async {
    try {
      final headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };
      
      final requestBody = {
        'embedding': embedding,
        'collection': collection,
        'limit': limit,
        'min_score': minScore,
      };
      
      if (filter != null) {
        requestBody['filter'] = filter;
      }
      
      final response = await _client.post(
        Uri.parse('$_ragServiceUrl/search'),
        headers: headers,
        body: jsonEncode(requestBody),
      );
      
      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        
        final List<RetrievalResult> results = [];
        for (final item in jsonResponse['results']) {
          results.add(RetrievalResult(
            id: item['id'],
            content: item['content'],
            source: item['source'],
            score: item['score'].toDouble(),
            metadata: item['metadata'],
          ));
        }
        
        return results;
      } else {
        final error = '搜索知识库失败: ${response.statusCode} - ${response.body}';
        LoggerUtil.error(error);
        throw Exception(error);
      }
    } catch (e) {
      LoggerUtil.error('搜索知识库异常: ${e.toString()}');
      throw Exception('搜索知识库失败: ${e.toString()}');
    }
  }
  
  /// 基于自然语言查询搜索知识库
  Future<List<RetrievalResult>> searchByText({
    required String query,
    required String collection,
    int limit = 5,
    double minScore = 0.7,
    Map<String, dynamic>? filter,
  }) async {
    try {
      // 生成查询的嵌入向量
      final embedding = await generateEmbedding(query);
      
      // 使用嵌入向量搜索
      return await searchKnowledgeBase(
        embedding: embedding,
        collection: collection,
        limit: limit,
        minScore: minScore,
        filter: filter,
      );
    } catch (e) {
      LoggerUtil.error('文本搜索知识库异常: ${e.toString()}');
      throw Exception('文本搜索知识库失败: ${e.toString()}');
    }
  }
  
  /// 增强生成（RAG流程）
  Future<AgentResponse> generateWithRAG({
    required String query,
    required List<AgentMessage> baseMessages,
    required String collection,
    required ModelCallOptions options,
    int retrievalLimit = 5,
    double minScore = 0.7,
    String systemPromptTemplate = '使用以下检索到的上下文信息回答用户问题。如果上下文信息不足以回答问题，请基于你自身的知识给出最佳回答，并明确指出哪些内容是基于上下文，哪些是基于你的知识。\n\n上下文信息:\n{context}\n\n回答时要确保信息准确，避免编造内容，如果确实不知道某个信息，请诚实告知你不知道。',
  }) async {
    try {
      // 1. 搜索相关文档
      final retrievalResults = await searchByText(
        query: query,
        collection: collection,
        limit: retrievalLimit,
        minScore: minScore,
      );
      
      // 如果没有检索到结果，直接使用基础消息生成
      if (retrievalResults.isEmpty) {
        LoggerUtil.warn('未检索到相关知识，使用基础模型生成回答');
        return await _modelProvider.chatCompletion(
          messages: baseMessages,
          options: options,
        );
      }
      
      // 2. 构建上下文
      final contextBuilder = StringBuffer();
      for (int i = 0; i < retrievalResults.length; i++) {
        final result = retrievalResults[i];
        contextBuilder.writeln('文档 ${i + 1}:');
        contextBuilder.writeln(result.content);
        contextBuilder.writeln('来源: ${result.source}');
        contextBuilder.writeln('---');
      }
      
      // 3. 替换系统提示中的上下文
      final systemPrompt = systemPromptTemplate.replaceAll(
        '{context}', 
        contextBuilder.toString(),
      );
      
      // 4. 构建新的消息列表
      final enhancedMessages = <AgentMessage>[];
      
      // 添加系统提示
      enhancedMessages.add(AgentMessage(
        role: AgentMessageRole.system,
        content: systemPrompt,
      ));
      
      // 添加除系统提示外的基础消息
      for (final message in baseMessages) {
        if (message.role != AgentMessageRole.system) {
          enhancedMessages.add(message);
        }
      }
      
      // 5. 使用增强消息生成回答
      final response = await _modelProvider.chatCompletion(
        messages: enhancedMessages,
        options: options,
      );
      
      // 添加检索元数据
      final enhancedResponse = AgentResponse(
        id: response.id,
        model: response.model,
        content: response.content,
        toolCalls: response.toolCalls,
        usage: response.usage,
        // 添加RAG元数据
        metadata: {
          'rag_info': {
            'retrieval_count': retrievalResults.length,
            'sources': retrievalResults.map((r) => {
              'id': r.id,
              'source': r.source,
              'score': r.score,
            }).toList(),
          },
        },
      );
      
      return enhancedResponse;
    } catch (e) {
      LoggerUtil.error('RAG生成异常: ${e.toString()}');
      throw Exception('RAG生成失败: ${e.toString()}');
    }
  }
  
  /// 关闭服务
  void dispose() {
    _client.close();
  }
}

/// 增强版RAG服务提供者
final enhancedRagServiceProvider = Provider<EnhancedRagService>((ref) {
  final modelProvider = ref.watch(modelProviderAdapterProvider);
  
  // 创建增强版RAG服务
  return EnhancedRagService(
    modelProvider: modelProvider,
  );
}); 