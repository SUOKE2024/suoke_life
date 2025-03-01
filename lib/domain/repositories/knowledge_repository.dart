import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../../ai_agents/models/embedding.dart';
import '../../core/utils/logger.dart';
import '../../data/datasources/local/database_service.dart';
import '../../data/datasources/remote/api_client.dart';

/// 知识库仓库接口
abstract class KnowledgeRepository {
  /// 生成文本嵌入向量
  Future<Embedding> generateEmbedding(String text);
  
  /// 索引文档（添加到检索系统）
  Future<void> indexDocument({
    required String documentId,
    required String content,
    Map<String, dynamic>? metadata,
  });
  
  /// 更新已索引的文档
  Future<void> updateDocument({
    required String documentId,
    required String content,
    Map<String, dynamic>? metadata,
  });
  
  /// 删除已索引的文档
  Future<void> deleteDocument(String documentId);
  
  /// 查询知识库
  Future<List<Map<String, dynamic>>> query(
    String query, {
    int limit = 5,
    Map<String, dynamic>? filter,
  });
  
  /// 获取相关段落
  Future<List<String>> getRelevantPassages(
    String query, {
    int limit = 3,
    double minScore = 0.7,
  });
  
  /// 添加知识条目
  Future<String> addKnowledgeItem({
    required String content,
    required String source,
    required String category,
    Map<String, dynamic>? metadata,
  });
}

/// 默认知识库仓库实现
class DefaultKnowledgeRepository implements KnowledgeRepository {
  final ApiClient _apiClient;
  final DatabaseService _databaseService;
  
  DefaultKnowledgeRepository(this._apiClient, this._databaseService);
  
  @override
  Future<Embedding> generateEmbedding(String text) async {
    try {
      // 尝试从API获取嵌入
      final response = await _apiClient.post(
        '/embeddings',
        body: {'text': text},
      );
      
      if (response != null && response['embedding'] != null) {
        final List<dynamic> rawVector = response['embedding'];
        final vector = rawVector.map((v) => (v as num).toDouble()).toList();
        
        return Embedding(
          vector: vector,
          text: text,
        );
      }
      
      // 如果API请求失败，回退到本地简单嵌入生成（非常简化的实现）
      return _generateSimpleEmbedding(text);
    } catch (e, stackTrace) {
      logger.e('生成嵌入失败', error: e, stackTrace: stackTrace);
      
      // 回退到本地简单嵌入生成
      return _generateSimpleEmbedding(text);
    }
  }
  
  /// 生成简单的嵌入（回退方案）
  Embedding _generateSimpleEmbedding(String text) {
    // 注意：这是一个非常简化的实现，实际应用中应使用更高质量的模型
    final random = Random(text.hashCode);
    final dimension = 384; // 常见嵌入维度
    
    // 创建与文本哈希相关的伪随机向量
    final vector = List<double>.generate(
      dimension,
      (i) => random.nextDouble() * 2 - 1,
    );
    
    // 归一化向量
    final double norm = sqrt(vector.fold(0.0, (sum, v) => sum + v * v));
    final normalizedVector = vector.map((v) => v / norm).toList();
    
    return Embedding(
      vector: normalizedVector,
      text: text,
    );
  }
  
  @override
  Future<void> indexDocument({
    required String documentId,
    required String content,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 确保知识表存在
      await _ensureKnowledgeTableExists();
      
      final now = DateTime.now().toIso8601String();
      
      // 存储到本地数据库
      await _databaseService.insert('knowledge_items', {
        'id': documentId,
        'content': content,
        'metadata': jsonEncode(metadata ?? {}),
        'source': metadata?['source'] ?? 'system',
        'category': metadata?['category'] ?? 'general',
        'created_at': now,
        'updated_at': now,
      });
      
      // 尝试将文档索引到远程服务
      try {
        await _apiClient.post('/index', body: {
          'document_id': documentId,
          'content': content,
          'metadata': metadata,
        });
      } catch (e) {
        logger.w('远程索引文档失败: $e');
        // 继续使用本地索引
      }
    } catch (e, stackTrace) {
      logger.e('索引文档失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<void> updateDocument({
    required String documentId,
    required String content,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 确保知识表存在
      await _ensureKnowledgeTableExists();
      
      final now = DateTime.now().toIso8601String();
      
      // 更新本地数据库
      await _databaseService.update(
        'knowledge_items',
        {
          'content': content,
          'metadata': jsonEncode(metadata ?? {}),
          'source': metadata?['source'] ?? 'system',
          'category': metadata?['category'] ?? 'general',
          'updated_at': now,
        },
        where: 'id = ?',
        whereArgs: [documentId],
      );
      
      // 尝试更新远程索引
      try {
        await _apiClient.put('/index/$documentId', body: {
          'content': content,
          'metadata': metadata,
        });
      } catch (e) {
        logger.w('更新远程索引失败: $e');
        // 继续使用本地索引
      }
    } catch (e, stackTrace) {
      logger.e('更新文档失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<void> deleteDocument(String documentId) async {
    try {
      // 从本地数据库删除
      await _databaseService.delete(
        'knowledge_items',
        where: 'id = ?',
        whereArgs: [documentId],
      );
      
      // 尝试从远程索引删除
      try {
        await _apiClient.delete('/index/$documentId');
      } catch (e) {
        logger.w('删除远程索引失败: $e');
        // 继续使用本地索引
      }
    } catch (e, stackTrace) {
      logger.e('删除文档失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<List<Map<String, dynamic>>> query(
    String query, {
    int limit = 5,
    Map<String, dynamic>? filter,
  }) async {
    try {
      final results = <Map<String, dynamic>>[];
      
      // 尝试从远程搜索
      try {
        final response = await _apiClient.get(
          '/search',
          queryParameters: {
            'q': query,
            'limit': limit.toString(),
            if (filter != null) 'filter': jsonEncode(filter),
          },
        );
        
        if (response != null && response['results'] != null) {
          final remoteResults = List<Map<String, dynamic>>.from(response['results']);
          results.addAll(remoteResults);
        }
      } catch (e) {
        logger.w('远程搜索失败: $e');
        // 回退到本地搜索
      }
      
      // 如果远程搜索失败或结果不足，从本地搜索补充
      if (results.length < limit) {
        final localResults = await _searchLocal(
          query,
          limit: limit - results.length,
          filter: filter,
        );
        
        // 合并结果，去重
        final existingIds = results.map((r) => r['id']).toSet();
        results.addAll(
          localResults.where((r) => !existingIds.contains(r['id'])),
        );
      }
      
      return results;
    } catch (e, stackTrace) {
      logger.e('查询知识库失败', error: e, stackTrace: stackTrace);
      
      // 回退到简单的本地搜索
      return _searchLocal(query, limit: limit, filter: filter);
    }
  }
  
  /// 本地搜索
  Future<List<Map<String, dynamic>>> _searchLocal(
    String query, {
    required int limit,
    Map<String, dynamic>? filter,
  }) async {
    try {
      // 确保知识表存在
      await _ensureKnowledgeTableExists();
      
      // 构建查询
      String whereClause = 'content LIKE ?';
      List<Object?> whereArgs = ['%$query%'];
      
      // 应用过滤器
      if (filter != null) {
        if (filter['category'] != null) {
          whereClause += ' AND category = ?';
          whereArgs.add(filter['category']);
        }
        
        if (filter['source'] != null) {
          whereClause += ' AND source = ?';
          whereArgs.add(filter['source']);
        }
      }
      
      // 执行查询
      final results = await _databaseService.query(
        'knowledge_items',
        where: whereClause,
        whereArgs: whereArgs,
        orderBy: 'created_at DESC',
        limit: limit,
      );
      
      // 转换结果格式
      return results.map((item) {
        return {
          'id': item['id'],
          'content': item['content'],
          'metadata': jsonDecode(item['metadata'] ?? '{}'),
          'score': 0.7, // 本地搜索的默认分数
        };
      }).toList();
    } catch (e) {
      logger.e('本地搜索失败: $e');
      return [];
    }
  }
  
  @override
  Future<List<String>> getRelevantPassages(
    String query, {
    int limit = 3,
    double minScore = 0.7,
  }) async {
    try {
      // 查询知识库
      final results = await this.query(
        query,
        limit: limit * 2, // 获取更多结果，然后筛选
      );
      
      // 筛选高分结果，仅返回内容
      final relevantPassages = results
          .where((result) => (result['score'] as num) >= minScore)
          .map((result) => result['content'] as String)
          .take(limit)
          .toList();
      
      return relevantPassages;
    } catch (e) {
      logger.e('获取相关段落失败: $e');
      return [];
    }
  }
  
  @override
  Future<String> addKnowledgeItem({
    required String content,
    required String source,
    required String category,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 生成ID
      final documentId = 'knowledge_${DateTime.now().millisecondsSinceEpoch}';
      
      // 添加元数据
      final fullMetadata = {
        'source': source,
        'category': category,
        ...?metadata,
      };
      
      // 索引文档
      await indexDocument(
        documentId: documentId,
        content: content,
        metadata: fullMetadata,
      );
      
      return documentId;
    } catch (e, stackTrace) {
      logger.e('添加知识条目失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  /// 确保知识表存在
  Future<void> _ensureKnowledgeTableExists() async {
    try {
      await _databaseService.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_items (
          id TEXT PRIMARY KEY,
          content TEXT NOT NULL,
          metadata TEXT,
          source TEXT,
          category TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT
        )
      ''');
    } catch (e) {
      logger.e('创建知识表失败: $e');
      rethrow;
    }
  }
} 