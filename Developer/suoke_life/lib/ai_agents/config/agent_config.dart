// 索克生活APP智能体配置文件
// 定义全局配置项

import 'package:flutter/foundation.dart';
import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:logging/logging.dart';
import 'package:suoke_life/core/services/config_service.dart';

/// 智能体配置管理类
class AgentConfig {
  static final Logger _logger = Logger('AgentConfig');
  
  /// 配置服务
  final ConfigService _configService;
  
  /// 智能体配置缓存
  final Map<String, Map<String, dynamic>> _agentConfigs = {};
  
  /// 构造函数
  AgentConfig(this._configService) {
    _loadAgentConfigs();
  }
  
  /// 加载所有智能体配置
  Future<void> _loadAgentConfigs() async {
    try {
      // 尝试从本地加载配置
      await _loadLocalAgentConfigs();
      
      // 尝试从远程加载配置
      await _loadRemoteAgentConfigs();
    } catch (e) {
      _logger.severe('加载智能体配置失败: $e');
    }
  }
  
  /// 从本地资源加载配置
  Future<void> _loadLocalAgentConfigs() async {
    try {
      // 加载预定义的智能体配置
      final manifestContent = await rootBundle.loadString('AssetManifest.json');
      final Map<String, dynamic> manifestMap = json.decode(manifestContent);
      
      final configPaths = manifestMap.keys
          .where((String key) => key.startsWith('assets/agents/') && key.endsWith('.json'))
          .toList();
      
      for (var path in configPaths) {
        try {
          final configContent = await rootBundle.loadString(path);
          final Map<String, dynamic> config = json.decode(configContent);
          final String agentId = config['id'] as String? ?? path.split('/').last.split('.').first;
          _agentConfigs[agentId] = config;
          _logger.info('已加载智能体配置: $agentId');
        } catch (e) {
          _logger.warning('加载配置文件失败: $path, 错误: $e');
        }
      }
    } catch (e) {
      _logger.warning('加载本地智能体配置失败: $e');
    }
  }
  
  /// 从远程加载配置
  Future<void> _loadRemoteAgentConfigs() async {
    try {
      final remoteConfigs = await _configService.getAgentConfigs();
      if (remoteConfigs != null) {
        for (var entry in remoteConfigs.entries) {
          // 远程配置优先级高于本地配置
          _agentConfigs[entry.key] = entry.value;
          _logger.info('已加载远程智能体配置: ${entry.key}');
        }
      }
    } catch (e) {
      _logger.warning('加载远程智能体配置失败: $e');
    }
  }
  
  /// 获取所有可用的智能体ID
  List<String> getAvailableAgentIds() {
    return _agentConfigs.keys.toList();
  }
  
  /// 获取指定智能体的配置
  Map<String, dynamic> getAgentConfig(String agentId) {
    if (!_agentConfigs.containsKey(agentId)) {
      throw ArgumentError('未找到智能体配置: $agentId');
    }
    return Map.from(_agentConfigs[agentId]!);
  }
  
  /// 获取智能体的名称
  String getAgentName(String agentId) {
    final config = getAgentConfig(agentId);
    return config['name'] as String? ?? agentId;
  }
  
  /// 获取智能体的描述
  String getAgentDescription(String agentId) {
    final config = getAgentConfig(agentId);
    return config['description'] as String? ?? '';
  }
  
  /// 获取智能体的图标路径
  String? getAgentIconPath(String agentId) {
    final config = getAgentConfig(agentId);
    return config['icon_path'] as String?;
  }
  
  /// 获取智能体的颜色
  int? getAgentColor(String agentId) {
    final config = getAgentConfig(agentId);
    final colorStr = config['color'] as String?;
    if (colorStr == null) {
      return null;
    }
    
    try {
      return int.parse(colorStr.replaceFirst('#', '0xFF'));
    } catch (e) {
      _logger.warning('解析智能体颜色失败: $colorStr, 错误: $e');
      return null;
    }
  }
  
  /// 获取智能体的系统提示词
  String getAgentSystemPrompt(String agentId) {
    final config = getAgentConfig(agentId);
    return config['system_prompt'] as String? ?? '';
  }
  
  /// 获取智能体的模型配置
  Map<String, dynamic>? getAgentModelConfig(String agentId) {
    final config = getAgentConfig(agentId);
    return config['model_config'] as Map<String, dynamic>?;
  }
  
  /// 获取智能体的工具配置
  List<Map<String, dynamic>>? getAgentToolsConfig(String agentId) {
    final config = getAgentConfig(agentId);
    final toolsConfig = config['tools'];
    if (toolsConfig == null) {
      return null;
    }
    
    if (toolsConfig is List) {
      return toolsConfig.cast<Map<String, dynamic>>();
    }
    
    return null;
  }
  
  /// 判断智能体是否启用了特定工具
  bool isToolEnabled(String agentId, String toolName) {
    final toolsConfig = getAgentToolsConfig(agentId);
    if (toolsConfig == null) {
      return false;
    }
    
    return toolsConfig.any((tool) => tool['name'] == toolName && (tool['enabled'] == true));
  }
  
  /// 获取智能体的RAG配置
  Map<String, dynamic>? getAgentRagConfig(String agentId) {
    final config = getAgentConfig(agentId);
    return config['rag_config'] as Map<String, dynamic>?;
  }
  
  /// 更新智能体配置
  Future<void> updateAgentConfig(String agentId, Map<String, dynamic> newConfig) async {
    _agentConfigs[agentId] = newConfig;
    await _configService.saveAgentConfig(agentId, newConfig);
    _logger.info('已更新智能体配置: $agentId');
  }
} 