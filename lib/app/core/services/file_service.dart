import 'package:injectable/injectable.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import '../security/encryption_service.dart';

@injectable
class FileService {
  final EncryptionService _encryption;

  FileService(this._encryption);

  Future<String> get _localPath async {
    final directory = await getApplicationDocumentsDirectory();
    return directory.path;
  }

  Future<File> _localFile(String filename) async {
    final path = await _localPath;
    return File('$path/$filename');
  }

  Future<void> writeEncrypted(String filename, List<int> bytes) async {
    final file = await _localFile(filename);
    final encrypted = _encryption.encryptFile(bytes);
    await file.writeAsString(encrypted);
  }

  Future<List<int>> readEncrypted(String filename) async {
    final file = await _localFile(filename);
    final encrypted = await file.readAsString();
    return _encryption.decryptFile(encrypted);
  }

  Future<void> deleteFile(String filename) async {
    final file = await _localFile(filename);
    if (await file.exists()) {
      await file.delete();
    }
  }

  Future<bool> exists(String filename) async {
    final file = await _localFile(filename);
    return file.exists();
  }

  Future<int> getSize(String filename) async {
    final file = await _localFile(filename);
    return file.length();
  }
} 