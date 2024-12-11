import 'dart:convert';
import 'dart:io';

import 'package:path/path.dart' as path;
import '../models/message.dart';

class MessageStorageService {
  static const String _messageDir = 'messages';
  static const String _fileExtension = '.json';
  
  Future<String> get _baseDir async {
    final appDir = await getApplicationDocumentsDirectory();
    final messageDir = Directory(path.join(appDir.path, _messageDir));
    if (!await messageDir.exists()) {
      await messageDir.create(recursive: true);
    }
    return messageDir.path;
  }

  String _getFileName(String assistantType) {
    return '${assistantType}_messages$_fileExtension';
  }

  Future<void> saveMessages(String assistantType, List<Message> messages) async {
    try {
      final baseDir = await _baseDir;
      final file = File(path.join(baseDir, _getFileName(assistantType)));
      
      final data = messages.map((m) => m.toJson()).toList();
      await file.writeAsString(jsonEncode(data));
    } catch (e) {
      print('Error saving messages: $e');
      rethrow;
    }
  }

  Future<List<Message>> loadMessages(String assistantType) async {
    try {
      final baseDir = await _baseDir;
      final file = File(path.join(baseDir, _getFileName(assistantType)));
      
      if (!await file.exists()) {
        return [];
      }

      final content = await file.readAsString();
      final List<dynamic> data = jsonDecode(content);
      
      return data
          .map((json) => Message.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      print('Error loading messages: $e');
      return [];
    }
  }

  Future<void> clearMessages(String assistantType) async {
    try {
      final baseDir = await _baseDir;
      final file = File(path.join(baseDir, _getFileName(assistantType)));
      
      if (await file.exists()) {
        await file.delete();
      }
    } catch (e) {
      print('Error clearing messages: $e');
      rethrow;
    }
  }

  Future<void> deleteAllMessages() async {
    try {
      final baseDir = await _baseDir;
      final dir = Directory(baseDir);
      
      if (await dir.exists()) {
        await dir.delete(recursive: true);
      }
    } catch (e) {
      print('Error deleting all messages: $e');
      rethrow;
    }
  }

  Future<Map<String, int>> getMessageStats() async {
    try {
      final baseDir = await _baseDir;
      final dir = Directory(baseDir);
      
      if (!await dir.exists()) {
        return {};
      }

      final Map<String, int> stats = {};
      await for (final file in dir.list()) {
        if (file is File && file.path.endsWith(_fileExtension)) {
          final content = await file.readAsString();
          final List<dynamic> data = jsonDecode(content);
          final assistantType = path.basenameWithoutExtension(file.path)
              .replaceAll('_messages', '');
          stats[assistantType] = data.length;
        }
      }
      
      return stats;
    } catch (e) {
      print('Error getting message stats: $e');
      return {};
    }
  }
} 