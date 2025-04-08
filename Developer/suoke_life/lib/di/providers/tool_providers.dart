// 工具提供者文件
// 用于注册和管理工具

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/ai_agents/tools/file_search_tool.dart';
import 'package:suoke_life/ai_agents/tools/tool_interface.dart';
import 'package:suoke_life/ai_agents/tools/web_search_tool.dart';
import 'package:suoke_life/di/providers/core_providers.dart';
import 'package:suoke_life/ai_agents/tools/tool_proxy.dart';

/// 工具注册表提供者
final toolRegistryProvider = Provider<ToolRegistry>((ref) {
  final registry = ToolRegistry();
  final apiClient = ref.watch(apiClientProvider);
  
  // 注册文件搜索工具代理
  final fileSearchToolProxy = ToolProxy(
    name: 'file_search',
    description: '搜索本地知识库中的文档，支持关键词搜索和语义搜索。',
    parameters: [
      ToolParameterDefinition(
        name: 'query',
        description: '搜索查询文本',
        type: ToolParameterType.string,
        required: true,
      ),
      ToolParameterDefinition(
        name: 'max_results',
        description: '最大返回结果数',
        type: ToolParameterType.integer,
        required: false,
        defaultValue: 5,
      ),
      ToolParameterDefinition(
        name: 'use_semantic_search',
        description: '是否使用语义搜索',
        type: ToolParameterType.boolean,
        required: false,
        defaultValue: true,
      ),
    ],
    apiClient: apiClient,
    requiresAuthentication: false,
  );
  
  registry.registerTool(fileSearchToolProxy);
  
  // 注册网络搜索工具代理
  final webSearchToolProxy = ToolProxy(
    name: 'web_search',
    description: '搜索网络获取最新健康资讯和医学信息',
    parameters: [
      ToolParameterDefinition(
        name: 'query',
        description: '搜索查询',
        type: ToolParameterType.string,
        required: true,
      ),
      ToolParameterDefinition(
        name: 'max_results',
        description: '最大结果数',
        type: ToolParameterType.integer,
        required: false,
        defaultValue: 5,
      ),
    ],
    apiClient: apiClient,
    requiresAuthentication: false,
  );
  
  registry.registerTool(webSearchToolProxy);
  
  return registry;
});

/// 工具定义列表提供者
final toolDefinitionsProvider = Provider<List<Map<String, dynamic>>>((ref) {
  final registry = ref.watch(toolRegistryProvider);
  return registry.toolDefinitions;
});

/// 网络搜索工具提供者
final webSearchToolProvider = Provider<WebSearchTool>((ref) {
  final configService = ref.watch(configServiceProvider);
  return WebSearchTool(
    configService: configService,
  );
}); 