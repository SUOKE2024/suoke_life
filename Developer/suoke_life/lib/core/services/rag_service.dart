// RAG服务接口
// 用于提供检索增强生成功能

import 'dart:async';
import 'dart:convert';

import 'package:logging/logging.dart';
import 'package:suoke_life/ai_agents/tools/file_search_tool.dart';
import 'package:suoke_life/core/services/config_service.dart';
import 'package:suoke_life/core/services/model_service.dart';

/// RAG检索结果
class RagResult {
  /// 检索到的文档ID
  final String documentId;
  
  /// 检索到的文档标题
  final String title;
  
  /// 检索到的文档内容
  final String content;
  
  /// 相关度分数
  final double score;
  
  /// 源文档路径
  final String? source;
  
  /// 元数据
  final Map<String, dynamic>? metadata;
  
  /// 构造函数
  RagResult({
    required this.documentId,
    required this.title,
    required this.content,
    required this.score,
    this.source,
    this.metadata,
  });
  
  /// 从JSON创建
  factory RagResult.fromJson(Map<String, dynamic> json) {
    return RagResult(
      documentId: json['document_id'],
      title: json['title'],
      content: json['content'],
      score: json['score'] is double 
        ? json['score'] 
        : double.parse(json['score'].toString()),
      source: json['source'],
      metadata: json['metadata'],
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'document_id': documentId,
      'title': title,
      'content': content,
      'score': score,
      if (source != null) 'source': source,
      if (metadata != null) 'metadata': metadata,
    };
  }
}

/// RAG检索选项
class RagOptions {
  /// 最大检索数量
  final int maxResults;
  
  /// 相关度阈值
  final double threshold;
  
  /// 是否启用重排序
  final bool enableReranking;
  
  /// 检索类型 (semantic, keyword, hybrid)
  final String retrievalType;
  
  /// 过滤条件
  final Map<String, dynamic>? filters;
  
  /// 构造函数
  RagOptions({
    this.maxResults = 5,
    this.threshold = 0.7,
    this.enableReranking = true,
    this.retrievalType = 'hybrid',
    this.filters,
  });
  
  /// 从JSON创建
  factory RagOptions.fromJson(Map<String, dynamic> json) {
    return RagOptions(
      maxResults: json['max_results'] ?? 5,
      threshold: json['threshold'] is double 
        ? json['threshold'] 
        : double.parse(json['threshold'].toString()),
      enableReranking: json['enable_reranking'] ?? true,
      retrievalType: json['retrieval_type'] ?? 'hybrid',
      filters: json['filters'],
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'max_results': maxResults,
      'threshold': threshold,
      'enable_reranking': enableReranking,
      'retrieval_type': retrievalType,
      if (filters != null) 'filters': filters,
    };
  }
}

/// RAG服务接口
abstract class RagService {
  /// 基于查询检索相关文档
  Future<List<RagResult>> retrieveDocuments(String query, {RagOptions? options});
  
  /// 对用户查询进行增强处理
  Future<String> enhanceQueryWithContext(
    String query, 
    List<String> previousMessages
  );
  
  /// 使用检索结果增强生成响应
  Future<String> generateEnhancedResponse(
    String query,
    List<RagResult> retrievedDocuments,
    List<String> previousMessages
  );
  
  /// 执行完整的RAG流程
  Future<String> processRagQuery(
    String query,
    List<String> previousMessages, 
    {RagOptions? options}
  );
  
  /// 评估RAG结果质量
  Future<Map<String, dynamic>> evaluateResponse(
    String query,
    String response,
    List<RagResult> retrievedDocuments
  );
}

/// 基本RAG服务实现
class BasicRagService implements RagService {
  static final Logger _logger = Logger('BasicRagService');
  
  /// 配置服务
  final ConfigService _configService;
  
  /// 模型服务
  final ModelService _modelService;
  
  /// 文件搜索工具
  final FileSearchTool _fileSearchTool;
  
  /// 构造函数
  BasicRagService({
    required ConfigService configService,
    required ModelService modelService,
    required FileSearchTool fileSearchTool,
  }) : 
    _configService = configService,
    _modelService = modelService,
    _fileSearchTool = fileSearchTool;
  
  @override
  Future<List<RagResult>> retrieveDocuments(String query, {RagOptions? options}) async {
    final opts = options ?? RagOptions();
    try {
      // 通过文件搜索工具获取结果
      final searchResults = await _fileSearchTool.executeSearchQuery(
        query,
        maxResults: opts.maxResults,
        useSemanticSearch: opts.retrievalType == 'semantic' || opts.retrievalType == 'hybrid',
        threshold: opts.threshold,
      );
      
      // 转换为RAG结果
      final ragResults = searchResults.map((result) {
        return RagResult(
          documentId: result.id,
          title: result.title,
          content: result.content,
          score: result.score,
          source: result.source,
          metadata: result.metadata,
        );
      }).toList();
      
      // 重排序（如果启用）
      if (opts.enableReranking && ragResults.length > 1) {
        // TODO: 实现重排序逻辑
        // 这里简化处理，仅按得分排序
        ragResults.sort((a, b) => b.score.compareTo(a.score));
      }
      
      return ragResults;
    } catch (e) {
      _logger.severe('检索文档失败: $e');
      return [];
    }
  }
  
  @override
  Future<String> enhanceQueryWithContext(String query, List<String> previousMessages) async {
    if (previousMessages.isEmpty) {
      return query;
    }
    
    try {
      // 构建提示
      final prompt = '''
你是一个查询增强助手。我将给你一个用户的查询和之前的对话历史，请帮助改写查询，使其更容易找到相关的信息。
请保持查询的本质，但添加必要的上下文信息。返回增强后的查询，不要添加任何解释。

对话历史:
${previousMessages.join('\n')}

原始查询: $query

增强查询:''';

      // 使用模型生成增强查询
      final response = await _modelService.chat([
        {'role': 'system', 'content': '你是一个专业的查询增强助手，擅长理解上下文并改进搜索查询。'},
        {'role': 'user', 'content': prompt}
      ]);
      
      return response.content.trim();
    } catch (e) {
      _logger.warning('增强查询失败: $e，使用原始查询');
      return query;
    }
  }
  
  @override
  Future<String> generateEnhancedResponse(
    String query,
    List<RagResult> retrievedDocuments,
    List<String> previousMessages
  ) async {
    try {
      // 准备上下文信息
      final contextBuilder = StringBuffer();
      if (retrievedDocuments.isNotEmpty) {
        contextBuilder.writeln('以下是关于你的查询的一些相关信息:');
        for (int i = 0; i < retrievedDocuments.length; i++) {
          final doc = retrievedDocuments[i];
          contextBuilder.writeln('【信息 ${i+1}】');
          contextBuilder.writeln('标题: ${doc.title}');
          contextBuilder.writeln('内容: ${doc.content}');
          contextBuilder.writeln('');
        }
      }
      
      // 构建消息历史
      final messages = <Map<String, dynamic>>[];
      
      // 系统消息
      messages.add({
        'role': 'system',
        'content': '''你是索克生活健康助手，一个专注于中医健康和生活方式指导的专业顾问。
请根据用户的查询和提供的参考信息，生成全面、准确、有帮助的回答。
如果参考信息不足，请基于中医理论和最佳实践提供合理建议，但不要编造信息。
回答要专业且容易理解，适合普通用户阅读。
'''
      });
      
      // 添加对话历史
      if (previousMessages.isNotEmpty) {
        bool isUserMessage = true; // 交替用户和助手消息
        for (final message in previousMessages) {
          messages.add({
            'role': isUserMessage ? 'user' : 'assistant',
            'content': message
          });
          isUserMessage = !isUserMessage;
        }
      }
      
      // 最后加入当前查询和上下文
      final userMessage = contextBuilder.toString().isNotEmpty
          ? '${query}\n\n参考信息:\n${contextBuilder.toString()}'
          : query;
      
      messages.add({
        'role': 'user',
        'content': userMessage
      });
      
      // 调用模型生成回答
      final response = await _modelService.chat(messages);
      return response.content;
    } catch (e) {
      _logger.severe('生成增强响应失败: $e');
      return '抱歉，我现在无法提供完整回答。请稍后再试。';
    }
  }
  
  @override
  Future<String> processRagQuery(
    String query,
    List<String> previousMessages, 
    {RagOptions? options}
  ) async {
    try {
      // 1. 增强查询
      final enhancedQuery = await enhanceQueryWithContext(query, previousMessages);
      _logger.info('原始查询: "$query", 增强查询: "$enhancedQuery"');
      
      // 2. 检索文档
      final retrievedDocs = await retrieveDocuments(enhancedQuery, options: options);
      _logger.info('检索到 ${retrievedDocs.length} 个文档');
      
      // 3. 生成增强响应
      final response = await generateEnhancedResponse(query, retrievedDocs, previousMessages);
      
      // 4. (可选) 评估响应质量
      if ((options?.enableReranking ?? true) && retrievedDocs.isNotEmpty) {
        _evaluateResponseAsync(query, response, retrievedDocs);
      }
      
      return response;
    } catch (e) {
      _logger.severe('处理RAG查询失败: $e');
      return '抱歉，我在处理您的问题时遇到困难。请稍后再试，或换一种方式提问。';
    }
  }
  
  /// 异步评估响应质量
  Future<void> _evaluateResponseAsync(
    String query,
    String response,
    List<RagResult> retrievedDocuments
  ) async {
    try {
      final metrics = await evaluateResponse(query, response, retrievedDocuments);
      _logger.info('响应质量评估: $metrics');
    } catch (e) {
      _logger.warning('评估响应质量失败: $e');
    }
  }
  
  @override
  Future<Map<String, dynamic>> evaluateResponse(
    String query,
    String response,
    List<RagResult> retrievedDocuments
  ) async {
    try {
      // 构建评估提示
      final docsText = retrievedDocuments.map((doc) => doc.content).join('\n\n');
      final prompt = '''
请评估以下回答的质量。评估指标如下:
1. 相关性 (0-10): 回答与用户查询的相关程度
2. 准确性 (0-10): 回答与提供的参考文档的一致性
3. 完整性 (0-10): 回答是否涵盖了查询的所有方面
4. 有用性 (0-10): 回答对用户的实际帮助程度
5. 幻觉问题 (0-10): 回答中包含不在参考文档中且可能不准确的信息的程度 (0表示无幻觉,10表示严重幻觉)

用户查询: ${query}

参考文档: 
${docsText}

生成的回答:
${response}

请以JSON格式返回评分，只返回JSON，不要有其他文本:
''';

      // 使用模型评估
      final evalResponse = await _modelService.chat([
        {'role': 'system', 'content': '你是一个专业的响应质量评估助手，请客观公正地评估回答质量。'},
        {'role': 'user', 'content': prompt}
      ]);
      
      // 解析评估结果
      final responseText = evalResponse.content.trim();
      final jsonStart = responseText.indexOf('{');
      final jsonEnd = responseText.lastIndexOf('}');
      
      if (jsonStart >= 0 && jsonEnd > jsonStart) {
        final jsonStr = responseText.substring(jsonStart, jsonEnd + 1);
        try {
          final Map<String, dynamic> metrics = Map<String, dynamic>.from(
            Map<String, dynamic>.from(jsonDecode(jsonStr))
          );
          
          // 计算总分
          double totalScore = 0;
          int count = 0;
          
          metrics.forEach((key, value) {
            if (value is num && key != 'hallucination') {
              totalScore += value.toDouble();
              count++;
            } else if (key == 'hallucination' && value is num) {
              // 幻觉分数是反向的，10分表示没有幻觉
              totalScore += (10 - value.toDouble());
              count++;
            }
          });
          
          // 添加平均分
          if (count > 0) {
            metrics['average_score'] = totalScore / count;
          }
          
          return metrics;
        } catch (e) {
          _logger.warning('解析评估JSON失败: $e');
        }
      }
      
      return {'error': 'Failed to parse evaluation results'};
    } catch (e) {
      _logger.warning('评估响应失败: $e');
      return {'error': e.toString()};
    }
  }
}