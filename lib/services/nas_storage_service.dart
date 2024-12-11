import 'dart:io';
import 'package:path/path.dart' as path;
import '../models/voice_record.dart';

class NasStorageService {
  final String nasBasePath;
  
  NasStorageService({required this.nasBasePath});
  
  Future<void> saveVoiceRecord({
    required String content,
    required DateTime timestamp,
    required String type,
  }) async {
    try {
      final directory = Directory(path.join(nasBasePath, 'voice_records'));
      if (!await directory.exists()) {
        await directory.create(recursive: true);
      }
      
      final fileName = '${timestamp.toIso8601String()}_$type.txt';
      final file = File(path.join(directory.path, fileName));
      
      final record = VoiceRecord(
        content: content,
        timestamp: timestamp,
        type: type,
      );
      
      await file.writeAsString(record.toJson().toString());
    } catch (e) {
      print('Error saving voice record to NAS: $e');
      rethrow;
    }
  }
  
  Future<List<Map<String, dynamic>>> getVoiceRecords() async {
    try {
      final directory = Directory(path.join(nasBasePath, 'voice_records'));
      if (!await directory.exists()) {
        return [];
      }
      
      final List<Map<String, dynamic>> records = [];
      await for (final file in directory.list()) {
        if (file is File && file.path.endsWith('.txt')) {
          final content = await file.readAsString();
          records.add({
            'content': content,
            'fileName': path.basename(file.path),
          });
        }
      }
      
      return records;
    } catch (e) {
      print('Error reading voice records from NAS: $e');
      return [];
    }
  }
} 