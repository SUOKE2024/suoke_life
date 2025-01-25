import 'package:get/get.dart';
import '../core/storage/storage_service.dart';

class LoggingService extends GetxService {
  final _logs = <Map<String, dynamic>>[].obs;
  
  Future<void> log(String level, String message, {Map<String, dynamic>? data}) async {
    final logEntry = {
      'timestamp': DateTime.now().toIso8601String(),
      'level': level,
      'message': message,
      'data': data,
    };
    
    _logs.add(logEntry);
    
    // 可以在这里添加其他日志处理逻辑
    // 比如写入文件、发送到服务器等
  }

  List<Map<String, dynamic>> getLogs() {
    return _logs.toList();
  }

  void clearLogs() {
    _logs.clear();
  }
} 