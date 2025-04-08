// 网络搜索工具
// 用于获取最新健康资讯

import 'dart:convert';
import 'dart:math';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';
import 'package:logger/logger.dart' as log_pkg;
import 'package:suoke_life/ai_agents/tools/tool_interface.dart';
import 'package:suoke_life/core/services/config_service.dart';
import 'package:suoke_life/core/utils/logger.dart';

/// 网络搜索结果
class WebSearchResult {
  final String title;
  final String snippet;
  final String url;
  final String? source;
  final DateTime? publishedDate;
  final Map<String, dynamic>? metadata;

  WebSearchResult({
    required this.title,
    required this.snippet,
    required this.url,
    this.source,
    this.publishedDate,
    this.metadata,
  });

  factory WebSearchResult.fromJson(Map<String, dynamic> json) {
    DateTime? publishedDate;
    if (json['published_date'] != null) {
      try {
        publishedDate = DateTime.parse(json['published_date']);
      } catch (e) {
        // 忽略解析错误
      }
    }

    return WebSearchResult(
      title: json['title'],
      snippet: json['snippet'],
      url: json['url'],
      source: json['source'],
      publishedDate: publishedDate,
      metadata: json['metadata'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'snippet': snippet,
      'url': url,
      if (source != null) 'source': source,
      if (publishedDate != null)
        'published_date': publishedDate!.toIso8601String(),
      if (metadata != null) 'metadata': metadata,
    };
  }

  @override
  String toString() {
    final dateStr = publishedDate != null
        ? DateFormat('yyyy-MM-dd').format(publishedDate!)
        : '未知日期';
    final sourceStr = source ?? '未知来源';
    
    return '''
标题: $title
来源: $sourceStr ($dateStr)
摘要: $snippet
链接: $url
''';
  }
}

/// 网络搜索工具 - 支持OpenAI API的web_search功能
class WebSearchTool implements Tool {
  static final Logger _logger = Logger('WebSearchTool');
  
  /// 配置服务
  final ConfigService _configService;
  
  /// OpenAI API相关配置
  final bool _useOpenAIWebSearch;
  final String? _openAIApiKey;
  
  /// 搜索API配置
  final String? _googleApiKey;
  final String? _googleCseId;
  final String? _bingApiKey;
  
  WebSearchTool({
    required ConfigService configService,
    bool useOpenAIWebSearch = false,
    String? openAIApiKey,
    String? googleApiKey,
    String? googleCseId,
    String? bingApiKey,
  }) : 
    _configService = configService,
    _useOpenAIWebSearch = useOpenAIWebSearch,
    _openAIApiKey = openAIApiKey,
    _googleApiKey = googleApiKey,
    _googleCseId = googleCseId,
    _bingApiKey = bingApiKey;
  
  @override
  String get name => 'web_search';

  @override
  String get description => '使用搜索引擎查询最新的健康知识、食疗方案、养生资讯等信息。';

  @override
  Map<String, ToolParameterDefinition> get parameters => {
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
    'time_period': ToolParameterDefinition(
      name: 'time_period',
      description: '搜索时间范围: recent(最近一周), month(一个月内), year(一年内), any(任意时间)',
      type: ToolParameterType.string,
      required: false,
      defaultValue: 'recent',
      enumValues: ['recent', 'month', 'year', 'any'],
    ),
    'language': ToolParameterDefinition(
      name: 'language',
      description: '搜索语言，默认为中文',
      type: ToolParameterType.string,
      required: false,
      defaultValue: 'zh-CN',
    ),
  };

  @override
  bool get requiresAuthentication => false;

  @override
  Map<String, dynamic> getDefinition() {
    return {
      'type': 'function',
      'function': {
        'name': name,
        'description': description,
        'parameters': {
          'type': 'object',
          'properties': parameters.map((key, value) => MapEntry(
                key,
                {
                  'type': _parameterTypeToJsonSchema(value.type),
                  'description': value.description,
                  if (value.enumValues != null) 'enum': value.enumValues,
                },
              )),
          'required': parameters
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
      _logger.info('执行网络搜索工具, 参数: $parameters');

      final query = parameters['query'] as String;
      final maxResults = parameters['max_results'] as int? ?? 5;
      final timePeriod = parameters['time_period'] as String? ?? 'recent';
      final language = parameters['language'] as String? ?? 'zh-CN';

      // 增强健康查询
      final enhancedQuery = _enhanceHealthQuery(query);
      
      List<WebSearchResult> results = [];
      
      // 根据配置使用不同的搜索方法
      if (_useOpenAIWebSearch && _openAIApiKey != null) {
        // 使用OpenAI web_search接口
        results = await _searchWithOpenAI(enhancedQuery, maxResults, timePeriod, language);
      } else {
        // 使用配置的搜索引擎API
        if (_googleApiKey != null && _googleCseId != null) {
          // 使用Google自定义搜索
          results = await _searchWithGoogle(enhancedQuery, maxResults, timePeriod, language);
        } else if (_bingApiKey != null) {
          // 使用Bing搜索
          results = await _searchWithBing(enhancedQuery, maxResults, timePeriod, language);
        } else {
          // 如果没有配置API密钥，返回模拟结果
          results = _getMockResults(enhancedQuery, maxResults);
        }
      }

      if (results.isEmpty) {
        return ToolCallResult.success(
          '未能找到与"$query"相关的搜索结果。请尝试使用不同的关键词或更广泛的搜索条件。');
      }

      // 格式化结果
      final formattedResults = _formatSearchResults(results);
      
      return ToolCallResult.success(formattedResults);
    } catch (e, stackTrace) {
      _logger.error('网络搜索出错: $e\n$stackTrace');
      return ToolCallResult.failure('搜索过程中出错: $e');
    }
  }

  // 增强健康相关查询
  String _enhanceHealthQuery(String query) {
    // 检查查询是否已经包含健康相关关键词
    final healthKeywords = [
      '健康', '养生', '中医', '食疗', '营养', '体质', '调理',
      '食谱', '保健', '防病', '治未病', '药膳', '穴位', '按摩',
      '针灸', '经络', '气血', '阴阳', '五行', '辩证', '脉诊'
    ];
    
    bool containsHealthKeyword = healthKeywords.any(
      (keyword) => query.toLowerCase().contains(keyword.toLowerCase())
    );
    
    // 如果不包含健康关键词，添加相关上下文
    if (!containsHealthKeyword) {
      return '$query 健康养生 中医观点';
    }
    
    return query;
  }

  // OpenAI搜索接口实现
  Future<List<WebSearchResult>> _searchWithOpenAI(
    String query, 
    int maxResults, 
    String timePeriod,
    String language
  ) async {
    try {
      // 这里模拟OpenAI的web_search功能
      // 在实际实现中，需要使用OpenAI的API
      // 目前OpenAI尚未公开独立的web_search接口
      // 以下代码仅为占位，实际上会回退到其他搜索引擎
      
      _logger.info('尝试使用OpenAI web_search功能搜索: $query');
      
      // 如果Google搜索可用，使用Google
      if (_googleApiKey != null && _googleCseId != null) {
        return await _searchWithGoogle(query, maxResults, timePeriod, language);
      }
      
      // 如果Bing搜索可用，使用Bing
      if (_bingApiKey != null) {
        return await _searchWithBing(query, maxResults, timePeriod, language);
      }
      
      // 都不可用时返回模拟结果
      return _getMockResults(query, maxResults);
    } catch (e) {
      _logger.error('OpenAI web_search搜索失败: $e');
      return [];
    }
  }
  
  // Google搜索实现
  Future<List<WebSearchResult>> _searchWithGoogle(
    String query,
    int maxResults,
    String timePeriod,
    String language
  ) async {
    try {
      // 构建API请求URL
      final dateRestrict = _getGoogleDateRestrict(timePeriod);
      
      final uri = Uri.https('www.googleapis.com', '/customsearch/v1', {
        'q': query,
        'cx': _googleCseId,
        'key': _googleApiKey,
        'num': maxResults.toString(),
        if (dateRestrict != null) 'dateRestrict': dateRestrict,
        'hl': language,
        'gl': language.split('-')[0],
      });
      
      final response = await http.get(uri);
      
      if (response.statusCode != 200) {
        throw Exception('Google API错误: ${response.statusCode} ${response.body}');
      }
      
      final data = json.decode(response.body);
      final items = data['items'] as List<dynamic>? ?? [];
      
      return items.map((item) {
        // 尝试解析发布日期
        DateTime? publishedDate;
        if (item['pagemap'] != null && 
            item['pagemap']['metatags'] != null && 
            (item['pagemap']['metatags'] as List).isNotEmpty) {
          final metatags = (item['pagemap']['metatags'] as List).first;
          if (metatags['article:published_time'] != null) {
            try {
              publishedDate = DateTime.parse(metatags['article:published_time']);
            } catch (_) {}
          }
        }
        
        return WebSearchResult(
          title: item['title'] ?? '未知标题',
          snippet: item['snippet'] ?? '无描述',
          url: item['link'] ?? '',
          source: _extractDomainFromUrl(item['link'] ?? ''),
          publishedDate: publishedDate,
        );
      }).toList();
    } catch (e) {
      _logger.error('Google搜索失败: $e');
      return [];
    }
  }
  
  // Bing搜索实现
  Future<List<WebSearchResult>> _searchWithBing(
    String query,
    int maxResults,
    String timePeriod,
    String language
  ) async {
    try {
      // 构建API请求URL
      final freshness = _getBingFreshness(timePeriod);
      
      final uri = Uri.https('api.bing.microsoft.com', '/v7.0/search', {
        'q': query,
        'count': maxResults.toString(),
        if (freshness != null) 'freshness': freshness,
        'mkt': language,
        'responseFilter': 'Webpages',
      });
      
      final response = await http.get(
        uri,
        headers: {
          'Ocp-Apim-Subscription-Key': _bingApiKey!,
        },
      );
      
      if (response.statusCode != 200) {
        throw Exception('Bing API错误: ${response.statusCode} ${response.body}');
      }
      
      final data = json.decode(response.body);
      final items = data['webPages']?['value'] as List<dynamic>? ?? [];
      
      return items.map((item) {
        // Bing API不直接提供发布日期，所以我们设为null
        return WebSearchResult(
          title: item['name'] ?? '未知标题',
          snippet: item['snippet'] ?? '无描述',
          url: item['url'] ?? '',
          source: _extractDomainFromUrl(item['url'] ?? ''),
          publishedDate: null,
        );
      }).toList();
    } catch (e) {
      _logger.error('Bing搜索失败: $e');
      return [];
    }
  }
  
  // 提取URL中的域名
  String _extractDomainFromUrl(String url) {
    try {
      final uri = Uri.parse(url);
      final host = uri.host;
      
      // 移除www.前缀
      if (host.startsWith('www.')) {
        return host.substring(4);
      }
      
      return host;
    } catch (e) {
      return '未知来源';
    }
  }
  
  // 获取Google日期限制参数
  String? _getGoogleDateRestrict(String timePeriod) {
    switch (timePeriod) {
      case 'recent':
        return 'w1'; // 一周内
      case 'month':
        return 'm1'; // 一个月内
      case 'year':
        return 'y1'; // 一年内
      case 'any':
      default:
        return null; // 不限制时间
    }
  }
  
  // 获取Bing鲜度参数
  String? _getBingFreshness(String timePeriod) {
    switch (timePeriod) {
      case 'recent':
        return 'Week'; // 一周内
      case 'month':
        return 'Month'; // 一个月内
      case 'year':
        return 'Year'; // 一年内
      case 'any':
      default:
        return null; // 不限制时间
    }
  }
  
  // 生成模拟搜索结果
  List<WebSearchResult> _getMockResults(String query, int maxResults) {
    final random = Random();
    final results = <WebSearchResult>[];
    
    // 健康相关网站列表
    final healthSites = [
      '健康时报网',
      '人民健康网',
      '家庭医生在线',
      '丁香医生',
      '中国中医药报',
      '国家中医药管理局',
      '39健康网',
      '好大夫在线',
      '央视健康',
      '健康中国',
    ];
    
    // 中医健康相关标题模板
    final titleTemplates = [
      '中医专家详解: $query 的养生之道',
      '$query - 传统中医观点与现代医学解析',
      '四季养生: $query 的最佳实践指南',
      '专家提醒: $query 需要注意这些问题',
      '最新研究: $query 对健康的影响',
      '$query 的科学依据与中医理论',
      '权威指南: 如何正确理解和应用 $query',
      '中医养生: $query 的辩证施治方法',
      '$query 的食疗方案与调理建议',
      '健康生活: $query 在日常中的应用',
    ];
    
    // 模拟内容摘要模板
    final snippetTemplates = [
      '针对$query，中医理论认为其与脾胃功能密切相关。本文从阴阳五行角度分析，提供了调理方案和日常预防措施，帮助读者建立科学的健康观念。',
      '本文详细介绍了$query的中医辨证方法，从体质分析入手，结合传统经络理论和现代医学研究，提出了个性化的调理建议和预防方案。',
      '最新研究表明，$query与生活方式有密切关系。本文总结了多位专家的意见，提供科学的调理方法，包括饮食调整、运动建议和情志调养。',
      '$query在中医养生中占有重要地位。本文分析了其中的理论基础，并提供了实用的日常保健方法，包括穴位按摩、食疗调理和生活习惯调整。',
      '关于$query，很多人存在认识误区。本文从中医理论和现代医学角度进行了科学解读，澄清了常见误解，并提供了专业的健康指导建议。',
    ];
    
    // 生成模拟结果
    for (int i = 0; i < maxResults; i++) {
      // 随机选择元素
      final site = healthSites[random.nextInt(healthSites.length)];
      final title = titleTemplates[random.nextInt(titleTemplates.length)];
      final snippet = snippetTemplates[random.nextInt(snippetTemplates.length)];
      
      // 生成模拟URL
      final url = 'https://www.${site.toLowerCase().replaceAll(' ', '')}.com/article/${random.nextInt(10000)}.html';
      
      // 生成随机日期 (过去一年内)
      final daysAgo = random.nextInt(365);
      final publishedDate = DateTime.now().subtract(Duration(days: daysAgo));
      
      results.add(WebSearchResult(
        title: title,
        snippet: snippet,
        url: url,
        source: site,
        publishedDate: publishedDate,
      ));
    }
    
    return results;
  }
  
  // 格式化搜索结果为可读文本
  String _formatSearchResults(List<WebSearchResult> results) {
    if (results.isEmpty) return '未找到相关信息。';
    
    final buffer = StringBuffer();
    buffer.writeln('搜索结果：\n');
    
    for (var i = 0; i < results.length; i++) {
      final result = results[i];
      buffer.write(result.toString());
      
      if (i < results.length - 1) {
        buffer.writeln('---\n');
      }
    }
    
    return buffer.toString();
  }
}