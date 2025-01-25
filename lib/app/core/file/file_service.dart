import 'package:injectable/injectable.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import '../security/encryption_service.dart';
import '../logger/logger.dart';

@singleton
class FileService {
  final EncryptionService _encryption;
  final AppLogger _logger;

  FileService(this._encryption, this._logger);

  Future<String> get _localPath async {
    final directory = await getApplicationDocumentsDirectory();
    return directory.path;
  }

  Future<File> _localFile(String filename) async {
    final path = await _localPath;
    return File('$path/$filename');
  }

  Future<void> writeSecureFile(String filename, String content) async {
    try {
      final file = await _localFile(filename);
      final encrypted = _encryption.encrypt(content);
      await file.writeAsString(encrypted);
    } catch (e, stack) {
      _logger.error('Error writing secure file', e, stack);
      rethrow;
    }
  }

  Future<String?> readSecureFile(String filename) async {
    try {
      final file = await _localFile(filename);
      if (!await file.exists()) return null;
      
      final encrypted = await file.readAsString();
      return _encryption.decrypt(encrypted);
    } catch (e, stack) {
      _logger.error('Error reading secure file', e, stack);
      return null;
    }
  }

  Future<void> deleteFile(String filename) async {
    try {
      final file = await _localFile(filename);
      if (await file.exists()) {
        await file.delete();
      }
    } catch (e, stack) {
      _logger.error('Error deleting file', e, stack);
      rethrow;
    }
  }

  Future<List<String>> listFiles() async {
    try {
      final path = await _localPath;
      final dir = Directory(path);
      return dir
          .listSync()
          .whereType<File>()
          .map((file) => file.path.split('/').last)
          .toList();
    } catch (e, stack) {
      _logger.error('Error listing files', e, stack);
      return [];
    }
  }
} 