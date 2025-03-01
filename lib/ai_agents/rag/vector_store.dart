import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import '../models/document.dart';
import '../models/embedding.dart';
import '../../core/error/exceptions.dart';
import 'embeddings.dart';

/// 向量存储接口
abstract class VectorStore {
  /// 通过相似度搜索文档
  Future<List<Document>> similaritySearch(
    String query, {
    int k = 4,
    Map<String, dynamic>? filter,
  });
  
  /// 添加文档
  Future<void> addDocuments(List<Document> documents);
  
  /// 更新文档
  Future<void> updateDocuments(List<Document> documents);
  
  /// 删除文档
  Future<void> deleteDocuments(List<String> ids);
}

/// 基于Pinecone的向量存储实现
class PineconeVectorStore implements VectorStore {
  final Embeddings _embeddings;
  final String _apiKey;
  final String _environment;
  final String _indexName;
  final String _namespace;
  final http.Client _client;
  
  PineconeVectorStore({
    required Embeddings embeddings,
    required String apiKey,
    required String environment,
    required String indexName,
    String namespace = '',
    http.Client? client,
  })  : _embeddings = embeddings,
        _apiKey = apiKey,
        _environment = environment,
        _indexName = indexName,
        _namespace = namespace,
        _client = client ?? http.Client();
  
  /// 获取API端点
  String get _apiEndpoint => 'https://$_indexName-$_environment.svc.pinecone.io';
  
  @override
  Future<List<Document>> similaritySearch(
    String query, {
    int k = 4,
    Map<String, dynamic>? filter,
  }) async {
    try {
      // 生成查询向量
      final embedding = await _embeddings.embedQuery(query);
      
      // 准备请求体
      final requestBody = {
        'vector': embedding.vector,
        'topK': k,
        'includeMetadata': true,
        'includeValues': false,
      };
      
      if (_namespace.isNotEmpty) {
        requestBody['namespace'] = _namespace;
      }
      
      if (filter != null) {
        requestBody['filter'] = filter;
      }
      
      // 发送请求
      final response = await _client.post(
        Uri.parse('$_apiEndpoint/query'),
        headers: {
          'Api-Key': _apiKey,
          'Content-Type': 'application/json',
        },
        body: jsonEncode(requestBody),
      );
      
      // 处理响应
      if (response.statusCode != 200) {
        throw ServerException(
          message: '向量检索失败: ${response.statusCode}',
          statusCode: response.statusCode,
        );
      }
      
      final responseData = jsonDecode(response.body);
      final List<dynamic> matches = responseData['matches'];
      
      // 转换为文档
      return matches.map((match) {
        final metadata = match['metadata'];
        final pageContent = metadata['text'];
        
        // 从metadata中移除text字段
        metadata.remove('text');
        
        return Document(
          id: match['id'],
          pageContent: pageContent,
          metadata: metadata,
          score: match['score'],
        );
      }).toList();
    } catch (e) {
      throw RAGException('向量检索失败: $e');
    }
  }
  
  @override
  Future<void> addDocuments(List<Document> documents) async {
    if (documents.isEmpty) return;
    
    try {
      // 批量处理，每次最多100个文档
    } catch (e) {
      throw RAGException('添加文档失败: $e');
    }
  }
  
  @override
  Future<void> updateDocuments(List<Document> documents) async {
    // Implementation needed
    throw UnimplementedError();
  }
  
  @override
  Future<void> deleteDocuments(List<String> ids) async {
    // Implementation needed
    throw UnimplementedError();
  }
}

/// 内存向量存储实现
class InMemoryVectorStore implements VectorStore {
  final List<Document> _documents = [];
  final EmbeddingService _embeddingService;
  
  InMemoryVectorStore(this._embeddingService);
  
  @override
  Future<List<Document>> similaritySearch(
    String query, {
    int k = 4,
    Map<String, dynamic>? filter,
  }) async {
    if (_documents.isEmpty) {
      return [];
    }
    
    // 获取查询的嵌入向量
    final queryEmbedding = await _embeddingService.embedQuery(query);
    
    // 计算相似度并排序
    final List<(Document, double)> docsAndScores = [];
    
    for (final doc in _documents) {
      // 跳过没有嵌入的文档
      if (doc.embedding == null) {
        continue;
      }
      
      // 应用过滤器
      if (filter != null && !_passesFilter(doc, filter)) {
        continue;
      }
      
      // 计算余弦相似度
      final similarity = _cosineSimilarity(
        queryEmbedding.vector,
        doc.embedding!.vector,
      );
      
      docsAndScores.add((doc, similarity));
    }
    
    // 按相似度排序
    docsAndScores.sort((a, b) => b.$2.compareTo(a.$2));
    
    // 返回前k个结果
    return docsAndScores
        .take(k)
        .map((entry) => entry.$1)
        .toList();
  }
  
  @override
  Future<void> addDocuments(List<Document> documents) async {
    for (final doc in documents) {
      if (doc.embedding == null && doc.pageContent.isNotEmpty) {
        // 生成嵌入向量
        final embedding = await _embeddingService.embedDocuments(
          [doc.pageContent],
        );
        if (embedding.isNotEmpty) {
          // 使用生成的嵌入向量更新文档
          _documents.add(
            doc.copyWith(embedding: embedding.first),
          );
        } else {
          // 无法生成嵌入向量
          _documents.add(doc);
        }
      } else {
        // 已有嵌入向量或空内容
        _documents.add(doc);
      }
    }
  }
  
  @override
  Future<void> updateDocuments(List<Document> documents) async {
    // Implementation needed
    throw UnimplementedError();
  }
  
  @override
  Future<void> deleteDocuments(List<String> ids) async {
    _documents.removeWhere((doc) => ids.contains(doc.id));
  }
  
  /// 计算余弦相似度
  double _cosineSimilarity(List<double> a, List<double> b) {
    if (a.isEmpty || b.isEmpty || a.length != b.length) {
      return 0.0;
    }
    
    double dotProduct = 0.0;
    double normA = 0.0;
    double normB = 0.0;
    
    for (int i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    
    if (normA == 0.0 || normB == 0.0) {
      return 0.0;
    }
    
    return dotProduct / (sqrt(normA) * sqrt(normB));
  }
  
  /// 检查文档是否通过过滤器
  bool _passesFilter(Document doc, Map<String, dynamic> filter) {
    // 简单实现: 检查元数据中的所有条件
    for (final entry in filter.entries) {
      final key = entry.key;
      final value = entry.value;
      
      if (!doc.metadata.containsKey(key) || doc.metadata[key] != value) {
        return false;
      }
    }
    
    return true;
  }
}

/// 远程API向量存储
class RemoteVectorStore implements VectorStore {
  final String apiUrl;
  final http.Client _client;
  final EmbeddingService _embeddingService;
  
  RemoteVectorStore(
    this.apiUrl,
    this._client,
    this._embeddingService,
  );
  
  @override
  Future<List<Document>> similaritySearch(
    String query, {
    int k = 4,
    Map<String, dynamic>? filter,
  }) async {
    try {
      // 获取查询的嵌入向量
      final queryEmbedding = await _embeddingService.embedQuery(query);
      
      // 准备请求体
      final requestBody = {
        'embedding': queryEmbedding.vector,
        'k': k,
        if (filter != null) 'filter': filter,
      };
      
      // 发送POST请求
      final response = await _client.post(
        Uri.parse('$apiUrl/similarity-search'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestBody),
      );
      
      if (response.statusCode != 200) {
        throw ServerException(
          message: '向量搜索失败: ${response.statusCode}',
          statusCode: response.statusCode,
        );
      }
      
      // 解析响应
      final responseData = jsonDecode(response.body);
      final List<dynamic> results = responseData['results'];
      
      // 转换为Document对象
      return results.map((item) {
        final embedding = item['embedding'] != null
            ? Embedding(
                vector: (item['embedding'] as List<dynamic>)
                    .map((e) => (e as num).toDouble())
                    .toList(),
              )
            : null;
        
        return Document(
          pageContent: item['pageContent'],
          metadata: Map<String, dynamic>.from(item['metadata'] ?? {}),
          id: item['id'],
          embedding: embedding,
        );
      }).toList();
    } catch (e) {
      throw ServerException(
        message: '向量搜索失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<void> addDocuments(List<Document> documents) async {
    try {
      // 为没有嵌入的文档生成嵌入
      final List<Document> processedDocs = [];
      
      for (final doc in documents) {
        if (doc.embedding == null && doc.pageContent.isNotEmpty) {
          // 生成嵌入向量
          final embeddings = await _embeddingService.embedDocuments(
            [doc.pageContent],
          );
          
          if (embeddings.isNotEmpty) {
            processedDocs.add(doc.copyWith(embedding: embeddings.first));
          } else {
            processedDocs.add(doc);
          }
        } else {
          processedDocs.add(doc);
        }
      }
      
      // 准备请求体
      final requestBody = {
        'documents': processedDocs.map((doc) => {
          'id': doc.id,
          'pageContent': doc.pageContent,
          'metadata': doc.metadata,
          if (doc.embedding != null)
            'embedding': doc.embedding!.vector,
        }).toList(),
      };
      
      // 发送POST请求
      final response = await _client.post(
        Uri.parse('$apiUrl/documents'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestBody),
      );
      
      if (response.statusCode != 200 && response.statusCode != 201) {
        throw ServerException(
          message: '添加文档失败: ${response.statusCode}',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      throw ServerException(
        message: '添加文档失败: $e',
        statusCode: 500,
      );
    }
  }
  
  @override
  Future<void> updateDocuments(List<Document> documents) async {
    // Implementation needed
    throw UnimplementedError();
  }
  
  @override
  Future<void> deleteDocuments(List<String> ids) async {
    try {
      // 准备请求体
      final requestBody = {'ids': ids};
      
      // 发送DELETE请求
      final response = await _client.delete(
        Uri.parse('$apiUrl/documents'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestBody),
      );
      
      if (response.statusCode != 200 && response.statusCode != 204) {
        throw ServerException(
          message: '删除文档失败: ${response.statusCode}',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      throw ServerException(
        message: '删除文档失败: $e',
        statusCode: 500,
      );
    }
  }
}

/// 向量存储提供者
final vectorStoreProvider = Provider<VectorStore>((ref) {
  // 获取嵌入服务
  final embeddingService = ref.watch(embeddingServiceProvider);
  
  // 这里可以根据配置选择不同的实现
  return InMemoryVectorStore(embeddingService);
});