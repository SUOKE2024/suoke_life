import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:flutter/foundation.dart';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path_provider/path_provider.dart';

import '../../ai_agents/models/embedding.dart';
import '../../core/utils/logger.dart';
import '../../data/datasources/local/database_service.dart';
import '../../data/datasources/local/secure_storage_service.dart';

/// 向量存储仓库接口
abstract class VectorStoreRepository {
  /// 添加文档到向量存储
  Future<String> addDocument({
    required String content,
    required Embedding embedding,
    required String collection,
    Map<String, dynamic>? metadata,
  });
  
  /// 更新向量存储中的文档
  Future<void> updateDocument({
    required String documentId,
    required String content,
    required Embedding embedding,
    required String collection,
    Map<String, dynamic>? metadata,
  });
  
  /// 删除向量存储中的文档
  Future<void> deleteDocument({
    required String documentId,
    required String collection,
  });
  
  /// 相似性搜索
  Future<List<SearchResult>> similaritySearch({
    required Embedding embedding,
    required String collection,
    int limit = 5,
    double minScore = 0.0,
    Map<String, dynamic>? filter,
  });
  
  /// 创建集合
  Future<void> createCollection(String collection);
  
  /// 删除集合
  Future<void> deleteCollection(String collection);
  
  /// 列出所有集合
  Future<List<String>> listCollections();
  
  /// 获取缓存的嵌入
  Future<Embedding?> getCachedEmbedding(String text);
  
  /// 缓存嵌入
  Future<void> cacheEmbedding(String text, Embedding embedding);
}

/// 本地向量存储仓库实现
class LocalVectorStoreRepository implements VectorStoreRepository {
  final DatabaseService _databaseService;
  final SecureStorageService _secureStorageService;
  
  // 嵌入缓存，避免重复计算
  final Map<String, Embedding> _embeddingCache = {};
  
  LocalVectorStoreRepository(this._databaseService, this._secureStorageService);
  
  @override
  Future<String> addDocument({
    required String content,
    required Embedding embedding,
    required String collection,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 确保向量表存在
      await _ensureVectorTablesExist();
      
      final now = DateTime.now().toIso8601String();
      final documentId = embedding.documentId ?? 'doc_${DateTime.now().millisecondsSinceEpoch}';
      
      // 存储文档内容
      await _databaseService.insert('vector_documents', {
        'id': documentId,
        'content': content,
        'collection': collection,
        'metadata': jsonEncode(metadata ?? {}),
        'created_at': now,
        'updated_at': now,
      });
      
      // 存储嵌入向量
      await _databaseService.insert('vector_embeddings', {
        'document_id': documentId,
        'collection': collection,
        'embedding': embedding.toBase64(),
        'dimension': embedding.dimension,
        'created_at': now,
      });
      
      return documentId;
    } catch (e, stackTrace) {
      logger.e('添加文档到向量存储失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<void> updateDocument({
    required String documentId,
    required String content,
    required Embedding embedding,
    required String collection,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 确保向量表存在
      await _ensureVectorTablesExist();
      
      final now = DateTime.now().toIso8601String();
      
      // 更新文档内容
      await _databaseService.update(
        'vector_documents',
        {
          'content': content,
          'collection': collection,
          'metadata': jsonEncode(metadata ?? {}),
          'updated_at': now,
        },
        where: 'id = ?',
        whereArgs: [documentId],
      );
      
      // 删除旧的嵌入
      await _databaseService.delete(
        'vector_embeddings',
        where: 'document_id = ?',
        whereArgs: [documentId],
      );
      
      // 添加新的嵌入
      await _databaseService.insert('vector_embeddings', {
        'document_id': documentId,
        'collection': collection,
        'embedding': embedding.toBase64(),
        'dimension': embedding.dimension,
        'created_at': now,
      });
    } catch (e, stackTrace) {
      logger.e('更新向量存储中的文档失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<void> deleteDocument({
    required String documentId,
    required String collection,
  }) async {
    try {
      // 删除文档
      await _databaseService.delete(
        'vector_documents',
        where: 'id = ? AND collection = ?',
        whereArgs: [documentId, collection],
      );
      
      // 删除嵌入
      await _databaseService.delete(
        'vector_embeddings',
        where: 'document_id = ? AND collection = ?',
        whereArgs: [documentId, collection],
      );
    } catch (e, stackTrace) {
      logger.e('删除向量存储中的文档失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<List<SearchResult>> similaritySearch({
    required Embedding embedding,
    required String collection,
    int limit = 5,
    double minScore = 0.0,
    Map<String, dynamic>? filter,
  }) async {
    try {
      // 确保向量表存在
      await _ensureVectorTablesExist();
      
      // 获取集合中的所有嵌入
      final embeddingsResult = await _databaseService.query(
        'vector_embeddings',
        where: 'collection = ?',
        whereArgs: [collection],
      );
      
      if (embeddingsResult.isEmpty) {
        return [];
      }
      
      // 计算相似度
      final similarities = <Map<String, dynamic>>[];
      
      for (final embeddingRow in embeddingsResult) {
        final documentId = embeddingRow['document_id'] as String;
        final embeddingBase64 = embeddingRow['embedding'] as String;
        
        try {
          // 解析嵌入
          final docEmbedding = Embedding.fromBase64(
            embeddingBase64,
            documentId: documentId,
          );
          
          // 计算余弦相似度
          final similarity = embedding.cosineSimilarity(docEmbedding);
          
          if (similarity >= minScore) {
            similarities.add({
              'document_id': documentId,
              'score': similarity,
            });
          }
        } catch (e) {
          logger.w('解析嵌入失败: $e');
          continue;
        }
      }
      
      // 按相似度排序
      similarities.sort((a, b) => (b['score'] as double).compareTo(a['score'] as double));
      
      // 如果没有结果，返回空列表
      if (similarities.isEmpty) {
        return [];
      }
      
      // 获取文档内容
      final results = <SearchResult>[];
      
      for (final similarity in similarities.take(limit)) {
        final documentId = similarity['document_id'] as String;
        
        // 构建查询
        String whereClause = 'id = ?';
        List<Object?> whereArgs = [documentId];
        
        // 应用过滤器
        if (filter != null) {
          // 需要动态构建过滤条件
          // 这里为简化实现，实际应该使用更复杂的过滤机制
        }
        
        final documentResult = await _databaseService.query(
          'vector_documents',
          where: whereClause,
          whereArgs: whereArgs,
          limit: 1,
        );
        
        if (documentResult.isNotEmpty) {
          final document = documentResult.first;
          
          results.add(SearchResult(
            content: document['content'] as String,
            documentId: documentId,
            score: similarity['score'] as double,
            metadata: jsonDecode(document['metadata'] as String? ?? '{}'),
          ));
        }
      }
      
      return results;
    } catch (e, stackTrace) {
      logger.e('相似性搜索失败', error: e, stackTrace: stackTrace);
      return [];
    }
  }
  
  @override
  Future<void> createCollection(String collection) async {
    try {
      // 确保向量表存在
      await _ensureVectorTablesExist();
      
      // 检查集合是否已存在
      final existingCollections = await _databaseService.query(
        'vector_collections',
        where: 'name = ?',
        whereArgs: [collection],
      );
      
      if (existingCollections.isEmpty) {
        // 创建新集合
        await _databaseService.insert('vector_collections', {
          'name': collection,
          'created_at': DateTime.now().toIso8601String(),
        });
      }
    } catch (e, stackTrace) {
      logger.e('创建集合失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<void> deleteCollection(String collection) async {
    try {
      // 删除集合中的所有文档
      await _databaseService.delete(
        'vector_documents',
        where: 'collection = ?',
        whereArgs: [collection],
      );
      
      // 删除集合中的所有嵌入
      await _databaseService.delete(
        'vector_embeddings',
        where: 'collection = ?',
        whereArgs: [collection],
      );
      
      // 删除集合记录
      await _databaseService.delete(
        'vector_collections',
        where: 'name = ?',
        whereArgs: [collection],
      );
    } catch (e, stackTrace) {
      logger.e('删除集合失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<List<String>> listCollections() async {
    try {
      // 确保向量表存在
      await _ensureVectorTablesExist();
      
      final collections = await _databaseService.query('vector_collections');
      
      return collections.map((row) => row['name'] as String).toList();
    } catch (e, stackTrace) {
      logger.e('列出集合失败', error: e, stackTrace: stackTrace);
      return [];
    }
  }
  
  @override
  Future<Embedding?> getCachedEmbedding(String text) async {
    // 首先检查内存缓存
    if (_embeddingCache.containsKey(text)) {
      return _embeddingCache[text];
    }
    
    try {
      // 计算文本的哈希作为缓存键
      final textHash = text.hashCode.toString();
      
      // 从安全存储中获取
      final cachedEmbeddingJson = await _secureStorageService.read(
        key: 'embedding_cache_$textHash',
      );
      
      if (cachedEmbeddingJson != null) {
        final embedding = Embedding.fromJson(cachedEmbeddingJson);
        
        // 添加到内存缓存
        _embeddingCache[text] = embedding;
        
        return embedding;
      }
      
      return null;
    } catch (e) {
      logger.w('获取缓存嵌入失败: $e');
      return null;
    }
  }
  
  @override
  Future<void> cacheEmbedding(String text, Embedding embedding) async {
    try {
      // 添加到内存缓存
      _embeddingCache[text] = embedding;
      
      // 计算文本的哈希作为缓存键
      final textHash = text.hashCode.toString();
      
      // 存储到安全存储
      await _secureStorageService.write(
        key: 'embedding_cache_$textHash',
        value: embedding.toJson(),
      );
      
      // 限制缓存大小
      if (_embeddingCache.length > 1000) {
        // 简单策略：移除最早添加的项
        final keyToRemove = _embeddingCache.keys.first;
        _embeddingCache.remove(keyToRemove);
      }
    } catch (e) {
      logger.w('缓存嵌入失败: $e');
    }
  }
  
  /// 确保向量表存在
  Future<void> _ensureVectorTablesExist() async {
    try {
      // 创建集合表
      await _databaseService.execute('''
        CREATE TABLE IF NOT EXISTS vector_collections (
          name TEXT PRIMARY KEY,
          created_at TEXT NOT NULL
        )
      ''');
      
      // 创建文档表
      await _databaseService.execute('''
        CREATE TABLE IF NOT EXISTS vector_documents (
          id TEXT PRIMARY KEY,
          content TEXT NOT NULL,
          collection TEXT NOT NULL,
          metadata TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT
        )
      ''');
      
      // 创建嵌入表
      await _databaseService.execute('''
        CREATE TABLE IF NOT EXISTS vector_embeddings (
          document_id TEXT PRIMARY KEY,
          collection TEXT NOT NULL,
          embedding TEXT NOT NULL,
          dimension INTEGER NOT NULL,
          created_at TEXT NOT NULL
        )
      ''');
      
      // 创建索引
      await _databaseService.execute(
        'CREATE INDEX IF NOT EXISTS idx_embeddings_collection ON vector_embeddings (collection)',
      );
      
      await _databaseService.execute(
        'CREATE INDEX IF NOT EXISTS idx_documents_collection ON vector_documents (collection)',
      );
    } catch (e) {
      logger.e('创建向量表失败: $e');
      rethrow;
    }
  }
}

/// 远程向量存储仓库实现
class RemoteVectorStoreRepository implements VectorStoreRepository {
  final http.Client _httpClient;
  final String baseUrl;
  final String apiKey;
  
  RemoteVectorStoreRepository({
    required this.baseUrl,
    required this.apiKey,
    http.Client? httpClient,
  }) : _httpClient = httpClient ?? http.Client();
  
  @override
  Future<String> addDocument({
    required String content,
    required Embedding embedding,
    required String collection,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final response = await _httpClient.post(
        Uri.parse('$baseUrl/vectors'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
        },
        body: jsonEncode({
          'content': content,
          'vector': embedding.vector,
          'collection': collection,
          'metadata': metadata,
        }),
      );
      
      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);
        return data['id'];
      } else {
        throw Exception('Failed to add document: ${response.statusCode}');
      }
    } catch (e, stackTrace) {
      logger.e('添加文档到远程向量存储失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<void> updateDocument({
    required String documentId,
    required String content,
    required Embedding embedding,
    required String collection,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final response = await _httpClient.put(
        Uri.parse('$baseUrl/vectors/$documentId'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
        },
        body: jsonEncode({
          'content': content,
          'vector': embedding.vector,
          'collection': collection,
          'metadata': metadata,
        }),
      );
      
      if (response.statusCode != 200) {
        throw Exception('Failed to update document: ${response.statusCode}');
      }
    } catch (e, stackTrace) {
      logger.e('更新远程向量存储中的文档失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<void> deleteDocument({
    required String documentId,
    required String collection,
  }) async {
    try {
      final response = await _httpClient.delete(
        Uri.parse('$baseUrl/vectors/$documentId?collection=$collection'),
        headers: {
          'Authorization': 'Bearer $apiKey',
        },
      );
      
      if (response.statusCode != 200 && response.statusCode != 204) {
        throw Exception('Failed to delete document: ${response.statusCode}');
      }
    } catch (e, stackTrace) {
      logger.e('删除远程向量存储中的文档失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<List<SearchResult>> similaritySearch({
    required Embedding embedding,
    required String collection,
    int limit = 5,
    double minScore = 0.0,
    Map<String, dynamic>? filter,
  }) async {
    try {
      final response = await _httpClient.post(
        Uri.parse('$baseUrl/search'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
        },
        body: jsonEncode({
          'vector': embedding.vector,
          'collection': collection,
          'limit': limit,
          'min_score': minScore,
          'filter': filter,
        }),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final results = <SearchResult>[];
        
        for (final result in data['results']) {
          results.add(SearchResult(
            content: result['content'],
            documentId: result['id'],
            score: result['score'],
            metadata: result['metadata'],
          ));
        }
        
        return results;
      } else {
        throw Exception('Failed to search: ${response.statusCode}');
      }
    } catch (e, stackTrace) {
      logger.e('远程相似性搜索失败', error: e, stackTrace: stackTrace);
      return [];
    }
  }
  
  @override
  Future<void> createCollection(String collection) async {
    try {
      final response = await _httpClient.post(
        Uri.parse('$baseUrl/collections'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
        },
        body: jsonEncode({
          'name': collection,
        }),
      );
      
      if (response.statusCode != 200 && response.statusCode != 201) {
        throw Exception('Failed to create collection: ${response.statusCode}');
      }
    } catch (e, stackTrace) {
      logger.e('创建远程集合失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<void> deleteCollection(String collection) async {
    try {
      final response = await _httpClient.delete(
        Uri.parse('$baseUrl/collections/$collection'),
        headers: {
          'Authorization': 'Bearer $apiKey',
        },
      );
      
      if (response.statusCode != 200 && response.statusCode != 204) {
        throw Exception('Failed to delete collection: ${response.statusCode}');
      }
    } catch (e, stackTrace) {
      logger.e('删除远程集合失败', error: e, stackTrace: stackTrace);
      rethrow;
    }
  }
  
  @override
  Future<List<String>> listCollections() async {
    try {
      final response = await _httpClient.get(
        Uri.parse('$baseUrl/collections'),
        headers: {
          'Authorization': 'Bearer $apiKey',
        },
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<String>.from(data['collections']);
      } else {
        throw Exception('Failed to list collections: ${response.statusCode}');
      }
    } catch (e, stackTrace) {
      logger.e('列出远程集合失败', error: e, stackTrace: stackTrace);
      return [];
    }
  }
  
  @override
  Future<Embedding?> getCachedEmbedding(String text) async {
    // 远程存储不实现本地缓存
    return null;
  }
  
  @override
  Future<void> cacheEmbedding(String text, Embedding embedding) async {
    // 远程存储不实现本地缓存
    return;
  }
} 