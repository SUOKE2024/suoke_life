import 'dart:async';
import 'package:suoke_life/core/mcp/mcp_service.dart';
import 'package:suoke_life/core/mcp/mcp_message.dart';
import '../local/base_storage.dart';

/// MCP存储适配器
class MCPStorageAdapter {
  final MCPService _mcpService;
  final StorageManager _storageManager;
  
  MCPStorageAdapter(this._mcpService, this._storageManager);
  
  /// 数据同步
  Future<void> syncData(StorageType type, {bool force = false}) async {
    final storage = _storageManager.getStorage(type);
    
    // 构建MCP消息
    final message = MCPMessage(
      type: 'storage.sync',
      data: {
        'storageType': type.toString(),
        'force': force,
      },
    );
    
    try {
      // 发送同步请求
      final response = await _mcpService.sendMessage(message);
      
      // 处理同步数据
      if (response.success) {
        final syncData = response.data['syncData'];
        for (final item in syncData) {
          await storage.write(item['key'], item['value']);
        }
      }
    } catch (e) {
      throw StorageException('Failed to sync with MCP', e);
    }
  }
  
  /// 备份数据
  Future<void> backupData(StorageType type) async {
    final storage = _storageManager.getStorage(type);
    
    try {
      // 获取所有数据
      final allData = await _getAllData(storage);
      
      // 构建MCP消息
      final message = MCPMessage(
        type: 'storage.backup',
        data: {
          'storageType': type.toString(),
          'data': allData,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
      
      // 发送备份请求
      await _mcpService.sendMessage(message);
    } catch (e) {
      throw StorageException('Failed to backup to MCP', e);
    }
  }
  
  /// 恢复数据
  Future<void> restoreData(StorageType type, String backupId) async {
    final storage = _storageManager.getStorage(type);
    
    // 构建MCP消息
    final message = MCPMessage(
      type: 'storage.restore',
      data: {
        'storageType': type.toString(),
        'backupId': backupId,
      },
    );
    
    try {
      // 发送恢复请求
      final response = await _mcpService.sendMessage(message);
      
      // 清除现有数据
      await storage.clear();
      
      // 恢复数据
      if (response.success) {
        final restoreData = response.data['restoreData'];
        for (final item in restoreData) {
          await storage.write(item['key'], item['value']);
        }
      }
    } catch (e) {
      throw StorageException('Failed to restore from MCP', e);
    }
  }
  
  /// 获取备份列表
  Future<List<Map<String, dynamic>>> getBackupList(StorageType type) async {
    final message = MCPMessage(
      type: 'storage.listBackups',
      data: {
        'storageType': type.toString(),
      },
    );
    
    try {
      final response = await _mcpService.sendMessage(message);
      return List<Map<String, dynamic>>.from(response.data['backups']);
    } catch (e) {
      throw StorageException('Failed to get backup list from MCP', e);
    }
  }
  
  /// 获取存储的所有数据
  Future<Map<String, dynamic>> _getAllData(BaseStorage storage) async {
    // TODO: 实现获取所有数据的逻辑
    return {};
  }
  
  /// 监听MCP存储事件
  Stream<MCPMessage> watchStorageEvents() {
    return _mcpService.messageStream.where(
      (message) => message.type.startsWith('storage.'),
    );
  }
} 