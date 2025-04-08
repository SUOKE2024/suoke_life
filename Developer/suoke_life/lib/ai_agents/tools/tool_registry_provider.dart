// 工具注册表提供者
// 注册所有可用工具

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'file_search_tool.dart';
import 'web_search_tool.dart';
import 'tool_interface.dart';

/// 工具注册表提供者
final toolRegistryProvider = Provider<ToolRegistry>((ref) {
  // 创建工具注册表
  final registry = ToolRegistry();
  
  // 获取文件搜索工具
  final fileSearchTool = ref.watch(fileSearchToolProvider);
  
  // 获取网络搜索工具
  final webSearchTool = ref.watch(webSearchToolProvider);
  
  // 注册工具
  registry.registerTool(fileSearchTool);
  registry.registerTool(webSearchTool);
  
  // TODO: 注册更多工具
  
  return registry;
});

/// 工具定义列表提供者
final toolDefinitionsProvider = Provider<List<Map<String, dynamic>>>((ref) {
  final registry = ref.watch(toolRegistryProvider);
  return registry.getAllToolDefinitions();
}); 