import 'dart:convert';
import 'dart:io';
import 'dart:async';
import 'package:path/path.dart' as path;
import '../../services/models/notification.dart';

class NotificationRepository {
  final String _storageDir;
  final String _filename = 'notifications.json';
  final _dataController = StreamController<List<NotificationMessage>>.broadcast();

  NotificationRepository(this._storageDir) {
    // 创建存储目录
    Directory(_storageDir).createSync(recursive: true);
    // 启动定期同步
    _startPeriodicSync();
  }

  Stream<List<NotificationMessage>> get dataStream => _dataController.stream;

  void _startPeriodicSync() {
    Timer.periodic(const Duration(minutes: 5), (_) => _syncData());
  }

  Future<void> _syncData() async {
    try {
      final notifications = await loadNotifications();
      _dataController.add(notifications);
    } catch (e) {
      print('数据同步错误: $e');
    }
  }

  Future<void> saveNotifications(List<NotificationMessage> notifications) async {
    try {
      final file = File(path.join(_storageDir, _filename));
      final data = notifications.map((n) => n.toJson()).toList();
      await file.writeAsString(jsonEncode(data));
      // 触发数据流更新
      _dataController.add(notifications);
    } catch (e) {
      print('保存通知错误: $e');
      rethrow;
    }
  }

  Future<List<NotificationMessage>> loadNotifications() async {
    try {
      final file = File(path.join(_storageDir, _filename));
      if (!await file.exists()) {
        return [];
      }
      
      final content = await file.readAsString();
      final List<dynamic> data = jsonDecode(content);
      
      return data.map((json) => NotificationMessage.fromJson(json)).toList();
    } catch (e) {
      print('加载通知错误: $e');
      return [];
    }
  }

  void dispose() {
    _dataController.close();
  }
} 