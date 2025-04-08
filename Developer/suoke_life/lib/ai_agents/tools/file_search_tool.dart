// 文件搜索工具
// 用于搜索知识库中的文件

import 'dart:convert';
import 'dart:io';
import 'dart:math' as math;

import 'package:flutter/foundation.dart';
import 'package:logging/logging.dart' as logging;
import 'package:path/path.dart' as path;
import 'package:suoke_life/ai_agents/tools/tool_interface.dart';
import 'package:suoke_life/core/services/config_service.dart';
import 'package:suoke_life/core/services/model_service.dart';
import 'package:suoke_life/core/services/vector_db_service.dart';
import 'package:http/http.dart' as http;

/// 搜索结果项
class SearchResultItem {
  /// 结果ID
  final String id;
  
  /// 标题
  final String title;
  
  /// 内容
  final String content;
  
  /// 来源
  final String source;
  
  /// 相关性得分
  final double score;
  
  /// 元数据
  final Map<String, dynamic> metadata;
  
  /// 构造函数
  SearchResultItem({
    required this.id,
    required this.title,
    required this.content,
    required this.source,
    required this.score,
    this.metadata = const {},
  });
  
  @override
  String toString() {
    return '来源: $source\n标题: $title\n内容: $content';
  }
  
  /// 从JSON创建
  factory SearchResultItem.fromJson(Map<String, dynamic> json) {
    return SearchResultItem(
      id: json['id'] as String,
      title: json['title'] as String,
      content: json['content'] as String,
      source: json['source'] as String,
      score: json['score'] is double 
          ? json['score'] 
          : double.parse(json['score'].toString()),
      metadata: json['metadata'] as Map<String, dynamic> ?? {},
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'source': source,
      'score': score,
      'metadata': metadata,
    };
  }
}

/// 文件搜索工具 - 升级为OpenAI文件搜索API风格
class FileSearchTool implements Tool {
  static final logging.Logger _logger = logging.Logger('FileSearchTool');
  
  /// 工具名称
  static const String toolName = 'file_search';
  
  /// 配置服务
  final ConfigService _configService;
  
  /// 模型服务
  final ModelService _modelService;
  
  /// 向量数据库服务
  final VectorDBService? _vectorDBService;
  
  /// 本地知识库路径
  final String _localKnowledgeBasePath;
  
  /// 是否使用OpenAI文件搜索API
  final bool _useOpenAIFileSearch;
  
  /// OpenAI API密钥
  final String? _openAIApiKey;
  
  /// 向量存储ID
  final String? _vectorStoreId;
  
  /// 构造函数
  FileSearchTool({
    required ConfigService configService,
    required ModelService modelService,
    VectorDBService? vectorDBService,
    String? localKnowledgeBasePath,
    bool useOpenAIFileSearch = false,
    String? openAIApiKey,
    String? vectorStoreId,
  })  : _configService = configService,
        _modelService = modelService,
        _vectorDBService = vectorDBService,
        _localKnowledgeBasePath = localKnowledgeBasePath ?? 'assets/knowledge_base',
        _useOpenAIFileSearch = useOpenAIFileSearch,
        _openAIApiKey = openAIApiKey,
        _vectorStoreId = vectorStoreId;
  
  @override
  String getName() => toolName;
  
  @override
  String getDescription() => '搜索本地或云端知识库，查找与中医养生、健康管理相关的文档和资料。';
  
  @override
  Map<String, ToolParameterDefinition> getParameters() => {
    'query': ToolParameterDefinition(
      name: 'query',
      description: '要搜索的查询语句',
      type: ToolParameterType.string,
      required: true,
    ),
    'max_results': ToolParameterDefinition(
      name: 'max_results',
      description: '返回的最大结果数量',
      type: ToolParameterType.integer,
      required: false,
      defaultValue: 5,
    ),
    'search_type': ToolParameterDefinition(
      name: 'search_type',
      description: '搜索类型: semantic（语义搜索）或 keyword（关键词搜索）',
      type: ToolParameterType.string,
      required: false,
      defaultValue: 'semantic',
      enumValues: ['semantic', 'keyword'],
    ),
    'filters': ToolParameterDefinition(
      name: 'filters',
      description: '可选的过滤条件，如来源、类型等',
      type: ToolParameterType.object,
      required: false,
    ),
  };
  
  @override
  bool requiresAuthentication() => false;
  
  @override
  bool validateParameters(Map<String, dynamic> params) {
    // 检查所有必需的参数是否存在
    for (final param in getParameters().values.where((p) => p.required)) {
      if (!params.containsKey(param.name) && param.defaultValue == null) {
        _logger.warning('缺少必需参数: ${param.name}');
        return false;
      }
    }
    
    // 检查特定参数的有效性
    if (params.containsKey('search_type')) {
      final searchType = params['search_type'].toString();
      if (searchType != 'semantic' && searchType != 'keyword') {
        _logger.warning('无效的搜索类型: $searchType');
        return false;
      }
    }
    
    if (params.containsKey('max_results')) {
      final maxResults = params['max_results'];
      if (maxResults is! int || maxResults <= 0) {
        _logger.warning('无效的最大结果数: $maxResults');
        return false;
      }
    }
    
    return true;
  }
  
  @override
  Map<String, dynamic> getDefinition() {
    return {
      'type': 'function',
      'function': {
        'name': getName(),
        'description': getDescription(),
        'parameters': {
          'type': 'object',
          'properties': getParameters().map((key, value) => MapEntry(
                key,
                {
                  'type': _parameterTypeToJsonSchema(value.type),
                  'description': value.description,
                  if (value.enumValues != null) 'enum': value.enumValues,
                },
              )),
          'required': getParameters()
              .entries
              .where((entry) => entry.value.required)
              .map((entry) => entry.key)
              .toList(),
        },
      },
    };
  }
  
  String _parameterTypeToJsonSchema(ToolParameterType type) {
    switch (type) {
      case ToolParameterType.string:
        return 'string';
      case ToolParameterType.integer:
        return 'integer';
      case ToolParameterType.number:
        return 'number';
      case ToolParameterType.boolean:
        return 'boolean';
      case ToolParameterType.object:
        return 'object';
      case ToolParameterType.array:
        return 'array';
      default:
        return 'string';
    }
  }
  
  @override
  Future<ToolCallResult> execute(Map<String, dynamic> parameters) async {
    try {
      _logger.info('执行文件搜索工具, 参数: $parameters');

      final query = parameters['query'] as String;
      final maxResults = parameters['max_results'] as int? ?? 5;
      final searchType = parameters['search_type'] as String? ?? 'semantic';
      final filters = parameters['filters'] as Map<String, dynamic>? ?? {};

      List<SearchResultItem> results = [];
      
      // 根据配置使用不同的搜索方法
      if (_useOpenAIFileSearch && _openAIApiKey != null && _vectorStoreId != null) {
        // 使用OpenAI文件搜索API
        results = await _searchWithOpenAI(query, maxResults, filters);
      } else if (_vectorDBService != null) {
        // 使用向量数据库服务
        results = await _searchWithVectorDB(query, maxResults, filters);
      } else {
        // 使用本地文件搜索
        if (searchType == 'semantic') {
          results = await _semanticSearch(query, maxResults, filters);
        } else {
          results = await _keywordSearch(query, maxResults, filters);
        }
      }

      if (results.isEmpty) {
        return ToolCallResult.success(
          '未找到与"$query"相关的文档。请尝试使用不同的关键词或更宽泛的搜索条件。');
      }

      // 格式化结果
      final formattedResults = _formatSearchResults(results);
      
      return ToolCallResult.success(formattedResults);
    } catch (e, stackTrace) {
      _logger.severe('文件搜索出错: $e\n$stackTrace');
      return ToolCallResult.failure('搜索过程中出错: $e');
    }
  }
  
  // OpenAI文件搜索API实现
  Future<List<SearchResultItem>> _searchWithOpenAI(
    String query, 
    int maxResults, 
    Map<String, dynamic> filters
  ) async {
    try {
      final uri = Uri.parse('https://api.openai.com/v1/vector-stores/${_vectorStoreId}/query');
      
      final headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${_openAIApiKey}',
      };
      
      final body = jsonEncode({
        'query': query,
        'max_results': maxResults,
        'metadata_filters': filters.isEmpty ? null : filters,
      });
      
      final response = await http.post(uri, headers: headers, body: body);
      
      if (response.statusCode != 200) {
        throw Exception('OpenAI API错误: ${response.statusCode} ${response.body}');
      }
      
      final data = jsonDecode(response.body);
      
      return (data['results'] as List).map((result) {
        return SearchResultItem(
          id: result['id'] ?? '',
          title: result['metadata']['title'] ?? '未知标题',
          content: result['text'] ?? '',
          source: result['metadata']['source'] ?? '未知来源',
          score: (result['score'] as num).toDouble(),
          metadata: result['metadata'] ?? {},
        );
      }).toList();
    } catch (e) {
      _logger.severe('OpenAI文件搜索失败: $e');
      return [];
    }
  }
  
  // 使用向量数据库服务实现搜索
  Future<List<SearchResultItem>> _searchWithVectorDB(
    String query,
    int maxResults,
    Map<String, dynamic> filters
  ) async {
    try {
      final embeddings = await _modelService.generateEmbeddings(query);
      
      final results = await _vectorDBService!.search(
        embeddings: embeddings,
        maxResults: maxResults,
        filters: filters,
      );
      
      return results.map((item) => SearchResultItem(
        id: item.id,
        title: item.metadata['title'] ?? '未知标题',
        content: item.content,
        source: item.metadata['source'] ?? '未知来源',
        score: item.score,
        metadata: item.metadata,
      )).toList();
      
    } catch (e) {
      _logger.severe('向量数据库搜索失败: $e');
      return [];
    }
  }

  // 语义搜索实现
  Future<List<SearchResultItem>> _semanticSearch(
    String query,
    int maxResults,
    Map<String, dynamic> filters
  ) async {
    try {
      // 获取查询的嵌入向量
      final queryEmbedding = await _modelService.generateEmbeddings(query);
      
      // 获取知识库文件列表
      final files = await _getKnowledgeBaseFiles();
      
      // 对每个文件计算相似度分数
      final results = <SearchResultItem>[];
      
      for (final file in files) {
        if (!_matchesFilters(file, filters)) continue;
        
        final content = await _readFileContent(file);
        final chunks = _chunkContent(content, 1000, 200); // 块大小1000字符，重叠200字符
        
        for (var i = 0; i < chunks.length; i++) {
          final chunk = chunks[i];
          
          // 获取文本块的嵌入向量
          final chunkEmbedding = await _modelService.generateEmbeddings(chunk);
          
          // 计算余弦相似度
          final similarity = _calculateCosineSimilarity(queryEmbedding, chunkEmbedding);
          
          if (similarity > 0.6) { // 相似度阈值
            results.add(SearchResultItem(
              id: '${path.basename(file.path)}_$i',
              title: _extractTitle(file.path),
              content: chunk,
              source: path.basename(file.path),
              score: similarity,
              metadata: {
                'path': file.path,
                'chunk_index': i,
              },
            ));
          }
        }
      }
      
      // 按相似度排序并限制数量
      results.sort((a, b) => b.score.compareTo(a.score));
      return results.take(maxResults).toList();
    } catch (e) {
      _logger.severe('语义搜索出错: $e');
      return [];
    }
  }
  
  // 关键词搜索实现
  Future<List<SearchResultItem>> _keywordSearch(
    String query,
    int maxResults,
    Map<String, dynamic> filters
  ) async {
    try {
      // 获取知识库文件列表
      final files = await _getKnowledgeBaseFiles();
      
      // 准备关键词查询
      final keywords = query.toLowerCase().split(' ')
          .where((k) => k.trim().isNotEmpty)
          .toList();
      
      // 对每个文件进行关键词匹配
      final results = <SearchResultItem>[];
      
      for (final file in files) {
        if (!_matchesFilters(file, filters)) continue;
        
        final content = await _readFileContent(file);
        final chunks = _chunkContent(content, 1000, 200);
        
        for (var i = 0; i < chunks.length; i++) {
          final chunk = chunks[i];
          final chunkLower = chunk.toLowerCase();
          
          // 计算关键词匹配得分
          int matchCount = 0;
          for (final keyword in keywords) {
            if (chunkLower.contains(keyword)) {
              matchCount++;
            }
          }
          
          // 计算匹配得分
          final score = keywords.isEmpty ? 0.0 : matchCount / keywords.length;
          
          if (score > 0.3) { // 匹配度阈值
            results.add(SearchResultItem(
              id: '${path.basename(file.path)}_$i',
              title: _extractTitle(file.path),
              content: chunk,
              source: path.basename(file.path),
              score: score,
              metadata: {
                'path': file.path,
                'chunk_index': i,
              },
            ));
          }
        }
      }
      
      // 按匹配得分排序并限制数量
      results.sort((a, b) => b.score.compareTo(a.score));
      return results.take(maxResults).toList();
    } catch (e) {
      _logger.severe('关键词搜索出错: $e');
      return [];
    }
  }
  
  // 文件过滤逻辑
  bool _matchesFilters(File file, Map<String, dynamic> filters) {
    if (filters.isEmpty) return true;
    
    final fileName = path.basename(file.path).toLowerCase();
    final filePath = file.path.toLowerCase();
    
    if (filters.containsKey('type')) {
      final type = filters['type'].toString().toLowerCase();
      final extension = path.extension(fileName).toLowerCase();
      
      if (type == 'pdf' && extension != '.pdf') return false;
      if (type == 'text' && extension != '.txt' && extension != '.md') return false;
    }
    
    if (filters.containsKey('category')) {
      final category = filters['category'].toString().toLowerCase();
      
      if (!filePath.contains('/${category}/') && !filePath.contains('\\${category}\\')) {
        return false;
      }
    }
    
    return true;
  }
  
  // 计算余弦相似度
  double _calculateCosineSimilarity(List<double> vec1, List<double> vec2) {
    if (vec1.length != vec2.length) {
      throw ArgumentError('向量维度不匹配: ${vec1.length} != ${vec2.length}');
    }
    
    double dotProduct = 0.0;
    double norm1 = 0.0;
    double norm2 = 0.0;
    
    for (int i = 0; i < vec1.length; i++) {
      dotProduct += vec1[i] * vec2[i];
      norm1 += vec1[i] * vec1[i];
      norm2 += vec2[i] * vec2[i];
    }
    
    norm1 = math.sqrt(norm1);
    norm2 = math.sqrt(norm2);
    
    if (norm1 == 0.0 || norm2 == 0.0) return 0.0;
    
    return dotProduct / (norm1 * norm2);
  }
  
  // 获取知识库文件
  Future<List<File>> _getKnowledgeBaseFiles() async {
    try {
      final directory = Directory(_localKnowledgeBasePath);
      
      if (!await directory.exists()) {
        _logger.warning('本地知识库目录不存在: $_localKnowledgeBasePath');
        return [];
      }
      
      final files = <File>[];
      
      await for (final entity in directory.list(recursive: true)) {
        if (entity is File) {
          // 只包含文本类型的文件
          final extension = path.extension(entity.path).toLowerCase();
          if (['.txt', '.md', '.json', '.pdf'].contains(extension)) {
            files.add(entity);
          }
        }
      }
      
      return files;
    } catch (e) {
      _logger.severe('获取知识库文件列表失败: $e');
      return [];
    }
  }
  
  // 读取文件内容
  Future<String> _readFileContent(File file) async {
    try {
      return await file.readAsString();
    } catch (e) {
      _logger.severe('读取文件内容失败: ${file.path}, $e');
      return '';
    }
  }
  
  // 从文件路径提取标题
  String _extractTitle(String filePath) {
    final fileName = path.basenameWithoutExtension(filePath);
    
    // 移除路径中的时间戳或ID等模式
    final cleanName = fileName.replaceAllMapped(
      RegExp(r'^\d+_|^\d{8}_|^id\d+_'), 
      (match) => '',
    );
    
    // 将下划线或连字符替换为空格
    return cleanName.replaceAll(RegExp(r'[_-]'), ' ');
  }
  
  // 将内容分块
  List<String> _chunkContent(String content, int chunkSize, int overlap) {
    final chunks = <String>[];
    
    if (content.isEmpty) return chunks;
    
    int startIndex = 0;
    while (startIndex < content.length) {
      final endIndex = startIndex + chunkSize <= content.length
          ? startIndex + chunkSize
          : content.length;
      
      chunks.add(content.substring(startIndex, endIndex));
      startIndex += chunkSize - overlap;
    }
    
    return chunks;
  }
  
  // 格式化搜索结果为可读文本
  String _formatSearchResults(List<SearchResultItem> results) {
    if (results.isEmpty) return '未找到相关文档。';
    
    final buffer = StringBuffer();
    buffer.writeln('找到了 ${results.length} 个相关文档：\n');
    
    for (var i = 0; i < results.length; i++) {
      final result = results[i];
      buffer.writeln('文档 ${i + 1}: ${result.title}');
      buffer.writeln('来源: ${result.source}');
      buffer.writeln('相关度: ${(result.score * 100).toStringAsFixed(1)}%');
      buffer.writeln('内容: ${result.content}');
      buffer.writeln('---');
    }
    
    return buffer.toString();
  }
}

/// 创建文件搜索工具参数
Map<String, dynamic> createFileSearchParameters({
  required String query,
  int? maxResults,
  bool? useSemanticSearch,
  List<String>? fileTypes,
  String? category,
}) {
  return {
    'query': query,
    if (maxResults != null) 'max_results': maxResults,
    if (useSemanticSearch != null) 'use_semantic_search': useSemanticSearch,
    if (fileTypes != null && fileTypes.isNotEmpty) 
      'file_types': fileTypes.join(','),
    if (category != null) 'category': category,
  };
} 