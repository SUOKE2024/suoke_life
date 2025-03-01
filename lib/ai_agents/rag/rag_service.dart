import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';

import '../../core/network/api_client.dart';
import '../../core/storage/database_service.dart';
import '../models/ai_agent.dart';
import '../../core/utils/logger.dart';
import '../../domain/repositories/knowledge_repository.dart';
import '../../domain/repositories/vector_store_repository.dart';
import '../models/embedding.dart';
import '../core/autonomous_learning_system.dart';

/// RAG检索类型
enum RAGType {
  /// 单步检索，基于查询直接返回结果
  directRetrieval,

  /// 多步检索，分解查询为多个步骤
  decompositionRetrieval,

  /// 反馈检索，根据用户反馈调整结果
  feedbackRetrieval,

  /// 多跳检索，多次查询，每次基于前一次结果
  multiHop,
}

/// RAG查询结果类
class RAGResult {
  final String documentId;
  final String content;
  final double? relevanceScore;
  final Map<String, dynamic>? metadata;

  RAGResult({
    required this.documentId,
    required this.content,
    this.relevanceScore,
    this.metadata,
  });

  @override
  String toString() =>
      'RAGResult{documentId: $documentId, relevanceScore: $relevanceScore}';
}

/// RAG查询参数
class RAGQueryOptions {
  /// 集合/知识库名称
  final String collection;

  /// 最大返回结果数
  final int limit;

  /// 最小相关性分数
  final double minScore;

  /// 筛选器
  final Map<String, dynamic>? filter;

  /// 是否包含元数据
  final bool includeMetadata;

  /// 特定字段列表
  final List<String>? fields;

  RAGQueryOptions({
    required this.collection,
    this.limit = 5,
    this.minScore = 0.5,
    this.filter,
    this.includeMetadata = true,
    this.fields,
  });
}

/// RAG服务接口
abstract class RAGService {
  /// 查询知识库
  Future<List<RAGResult>> query(
    String query, {
    required String collection,
    int limit = 5,
    Map<String, dynamic>? filter,
  });

  /// 添加文档到知识库
  Future<String> addDocument({
    required String content,
    required String collection,
    String? title,
    String? type,
    String? source,
    Map<String, dynamic>? metadata,
  });

  /// 批量添加文档到知识库
  Future<List<String>> addDocuments({
    required List<Map<String, dynamic>> documents,
    required String collection,
  });

  /// 从知识库删除文档
  Future<void> deleteDocument({
    required String documentId,
    required String collection,
  });

  /// 更新知识库中的文档
  Future<void> updateDocument({
    required String documentId,
    required String content,
    required String collection,
    String? title,
    String? type,
    String? source,
    Map<String, dynamic>? metadata,
  });

  /// 创建知识库集合
  Future<void> createCollection(String collection);

  /// 删除知识库集合
  Future<void> deleteCollection(String collection);

  /// 列出所有知识库集合
  Future<List<String>> listCollections();
}

/// 默认RAG服务实现
class DefaultRAGService implements RAGService {
  final VectorStoreRepository vectorStoreRepository;
  final KnowledgeRepository knowledgeRepository;

  DefaultRAGService({
    required this.vectorStoreRepository,
    required this.knowledgeRepository,
  });

  /// 当前的嵌入模型提供者
  EmbeddingProvider _embeddingProvider = EmbeddingProvider.local;

  /// 设置嵌入模型提供者
  set embeddingProvider(EmbeddingProvider provider) {
    _embeddingProvider = provider;
  }

  /// 生成文本嵌入
  Future<Embedding> _generateEmbedding(String text) async {
    try {
      // 首先检查是否有缓存的嵌入
      final cachedEmbedding = await vectorStoreRepository.getCachedEmbedding(
        text,
      );

      if (cachedEmbedding != null) {
        return cachedEmbedding;
      }

      // 使用知识库生成嵌入
      final embedding = await knowledgeRepository.generateEmbedding(text);

      // 缓存嵌入
      await vectorStoreRepository.cacheEmbedding(text, embedding);

      return embedding;
    } catch (e, stackTrace) {
      logger.e('生成嵌入向量失败', error: e, stackTrace: stackTrace);

      // 创建一个随机嵌入作为退路方案
      final random = Random();
      final dimension = 384; // 常见嵌入维度
      final vector = List<double>.generate(
        dimension,
        (_) => random.nextDouble() * 2 - 1,
      );

      return Embedding(
        vector: vector,
        documentId: 'fallback_${DateTime.now().millisecondsSinceEpoch}',
        text: text,
      );
    }
  }

  @override
  Future<List<RAGResult>> query(
    String query, {
    required String collection,
    int limit = 5,
    Map<String, dynamic>? filter,
  }) async {
    try {
      // 生成查询的嵌入向量
      final queryEmbedding = await _generateEmbedding(query);

      // 在向量存储中搜索相似嵌入
      final searchResults = await vectorStoreRepository.similaritySearch(
        embedding: queryEmbedding,
        collection: collection,
        limit: limit,
        filter: filter,
      );

      // 转换为RAG结果
      final results =
          searchResults.map((result) {
            return RAGResult(
              content: result.content,
              documentId: result.documentId,
              relevanceScore: result.score,
              metadata: result.metadata,
            );
          }).toList();

      // 记录学习数据
      if (results.isNotEmpty) {
        await learningSystem.collectData(
          LearningDataItem(
            id: 'rag_query_${DateTime.now().millisecondsSinceEpoch}',
            type: LearningDataType.userInteraction,
            source: LearningDataSource.userInput,
            content: {
              'query': query,
              'collection': collection,
              'results': results.map((r) => r.toMap()).toList(),
            },
            timestamp: DateTime.now(),
          ),
        );
      }

      return results;
    } catch (e, stackTrace) {
      logger.e('RAG查询失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  @override
  Future<String> addDocument({
    required String content,
    required String collection,
    String? title,
    String? type,
    String? source,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 合并元数据
      final documentMetadata = {
        'title': title,
        'type': type,
        'source': source,
        'timestamp': DateTime.now().toIso8601String(),
        ...?metadata,
      };

      // 生成内容的嵌入向量
      final embedding = await _generateEmbedding(content);

      // 将文档添加到向量存储
      final documentId = await vectorStoreRepository.addDocument(
        content: content,
        embedding: embedding,
        collection: collection,
        metadata: documentMetadata,
      );

      // 添加到知识库索引
      await knowledgeRepository.indexDocument(
        documentId: documentId,
        content: content,
        metadata: documentMetadata,
      );

      return documentId;
    } catch (e, stackTrace) {
      logger.e('添加文档失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  @override
  Future<List<String>> addDocuments({
    required List<Map<String, dynamic>> documents,
    required String collection,
  }) async {
    final documentIds = <String>[];

    for (final doc in documents) {
      try {
        final documentId = await addDocument(
          content: doc['content'],
          collection: collection,
          title: doc['title'],
          type: doc['type'],
          source: doc['source'],
          metadata: doc['metadata'],
        );

        documentIds.add(documentId);
      } catch (e) {
        logger.w('添加文档失败: ${doc['title'] ?? '未知标题'}', error: e);
        // 继续处理下一个文档
      }
    }

    return documentIds;
  }

  @override
  Future<void> deleteDocument({
    required String documentId,
    required String collection,
  }) async {
    try {
      // 从向量存储中删除
      await vectorStoreRepository.deleteDocument(
        documentId: documentId,
        collection: collection,
      );

      // 从知识库索引中删除
      await knowledgeRepository.deleteDocument(documentId);
    } catch (e, stackTrace) {
      logger.e('删除文档失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  @override
  Future<void> updateDocument({
    required String documentId,
    required String content,
    required String collection,
    String? title,
    String? type,
    String? source,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 合并元数据
      final documentMetadata = {
        'title': title,
        'type': type,
        'source': source,
        'timestamp': DateTime.now().toIso8601String(),
        ...?metadata,
      };

      // 生成内容的嵌入向量
      final embedding = await _generateEmbedding(content);

      // 更新向量存储中的文档
      await vectorStoreRepository.updateDocument(
        documentId: documentId,
        content: content,
        embedding: embedding,
        collection: collection,
        metadata: documentMetadata,
      );

      // 更新知识库索引
      await knowledgeRepository.updateDocument(
        documentId: documentId,
        content: content,
        metadata: documentMetadata,
      );
    } catch (e, stackTrace) {
      logger.e('更新文档失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  @override
  Future<void> createCollection(String collection) async {
    try {
      await vectorStoreRepository.createCollection(collection);
    } catch (e, stackTrace) {
      logger.e('创建知识库集合失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  @override
  Future<void> deleteCollection(String collection) async {
    try {
      await vectorStoreRepository.deleteCollection(collection);
    } catch (e, stackTrace) {
      logger.e('删除知识库集合失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }

  @override
  Future<List<String>> listCollections() async {
    try {
      return await vectorStoreRepository.listCollections();
    } catch (e, stackTrace) {
      logger.e('列出知识库集合失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
}

/// 本地RAG服务实现 - 使用本地向量数据库
class LocalRAGService extends DefaultRAGService {
  LocalRAGService(
    KnowledgeRepository knowledgeRepository,
    VectorStoreRepository vectorStoreRepository,
    AutonomousLearningSystem learningSystem,
  ) : super(
        vectorStoreRepository: vectorStoreRepository,
        knowledgeRepository: knowledgeRepository,
      );

  // 可以添加本地特有的优化
}

/// 混合RAG服务实现 - 同时使用本地和远程知识库
class HybridRAGService implements RAGService {
  final RAGService _localService;
  final RAGService _remoteService;

  HybridRAGService(this._localService, this._remoteService);

  @override
  Future<List<RAGResult>> query(
    String query, {
    required String collection,
    int limit = 5,
    Map<String, dynamic>? filter,
  }) async {
    // 并行查询本地和远程知识库
    final results = await Future.wait([
      _localService.query(
        query,
        collection: collection,
        limit: limit,
        filter: filter,
      ),
      _remoteService.query(
        query,
        collection: collection,
        limit: limit,
        filter: filter,
      ),
    ]);

    // 合并结果
    final localResults = results[0];
    final remoteResults = results[1];

    // 合并并去重
    final combinedResults = <RAGResult>[];
    final documentIds = <String>{};

    // 先添加本地结果
    for (final result in localResults) {
      if (!documentIds.contains(result.documentId)) {
        combinedResults.add(result);
        documentIds.add(result.documentId);
      }
    }

    // 再添加远程结果
    for (final result in remoteResults) {
      if (!documentIds.contains(result.documentId)) {
        combinedResults.add(result);
        documentIds.add(result.documentId);
      }
    }

    // 按相关性排序并限制数量
    combinedResults.sort(
      (a, b) => b.relevanceScore!.compareTo(a.relevanceScore!),
    );

    return combinedResults.take(limit).toList();
  }

  @override
  Future<String> addDocument({
    required String content,
    required String collection,
    String? title,
    String? type,
    String? source,
    Map<String, dynamic>? metadata,
  }) async {
    // 先添加到本地，然后添加到远程
    final localDocumentId = await _localService.addDocument(
      content: content,
      collection: collection,
      title: title,
      type: type,
      source: source,
      metadata: metadata,
    );

    try {
      await _remoteService.addDocument(
        content: content,
        collection: collection,
        title: title,
        type: type,
        source: source,
        metadata: {...?metadata, 'localDocumentId': localDocumentId},
      );
    } catch (e) {
      logger.w('添加文档到远程知识库失败', error: e);
      // 继续返回本地文档ID，不阻塞操作
    }

    return localDocumentId;
  }

  @override
  Future<List<String>> addDocuments({
    required List<Map<String, dynamic>> documents,
    required String collection,
  }) async {
    // 添加到本地知识库
    final localDocumentIds = await _localService.addDocuments(
      documents: documents,
      collection: collection,
    );

    try {
      // 尝试添加到远程知识库
      await _remoteService.addDocuments(
        documents: documents,
        collection: collection,
      );
    } catch (e) {
      logger.w('添加文档到远程知识库失败', error: e);
      // 继续返回本地文档ID，不阻塞操作
    }

    return localDocumentIds;
  }

  @override
  Future<void> deleteDocument({
    required String documentId,
    required String collection,
  }) async {
    // 从本地和远程知识库中删除
    await Future.wait([
      _localService.deleteDocument(
        documentId: documentId,
        collection: collection,
      ),
      _remoteService.deleteDocument(
        documentId: documentId,
        collection: collection,
      ),
    ]);
  }

  @override
  Future<void> updateDocument({
    required String documentId,
    required String content,
    required String collection,
    String? title,
    String? type,
    String? source,
    Map<String, dynamic>? metadata,
  }) async {
    // 更新本地和远程知识库
    await Future.wait([
      _localService.updateDocument(
        documentId: documentId,
        content: content,
        collection: collection,
        title: title,
        type: type,
        source: source,
        metadata: metadata,
      ),
      _remoteService.updateDocument(
        documentId: documentId,
        content: content,
        collection: collection,
        title: title,
        type: type,
        source: source,
        metadata: metadata,
      ),
    ]);
  }

  @override
  Future<void> createCollection(String collection) async {
    // 在本地和远程知识库中创建集合
    await Future.wait([
      _localService.createCollection(collection),
      _remoteService.createCollection(collection),
    ]);
  }

  @override
  Future<void> deleteCollection(String collection) async {
    // 从本地和远程知识库中删除集合
    await Future.wait([
      _localService.deleteCollection(collection),
      _remoteService.deleteCollection(collection),
    ]);
  }

  @override
  Future<List<String>> listCollections() async {
    // 获取本地和远程知识库的集合列表
    final results = await Future.wait([
      _localService.listCollections(),
      _remoteService.listCollections(),
    ]);

    // 合并并去重
    final localCollections = results[0];
    final remoteCollections = results[1];
    final combinedCollections = <String>{};

    combinedCollections.addAll(localCollections);
    combinedCollections.addAll(remoteCollections);

    return combinedCollections.toList();
  }
}

// RAG Provider已移至lib/di/providers.dart
// 使用时请从providers.dart导入

/// 常用知识库集合名称
class RAGCollections {
  static const String tcmKnowledge = 'tcm_knowledge';
  static const String westernMedicalKnowledge = 'western_medical_knowledge';
  static const String nutritionKnowledge = 'nutrition_knowledge';
  static const String exerciseKnowledge = 'exercise_knowledge';
  static const String medicinalFoodKnowledge = 'medicinal_food_knowledge';
  static const String userHealthData = 'user_health_data';
  static const String userFeedback = 'user_feedback';
}
