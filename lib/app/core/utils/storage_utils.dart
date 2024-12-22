import 'dart:io';
import 'package:path_provider/path_provider.dart';

class StorageUtils {
  static Future<String> get localPath async {
    final directory = await getApplicationDocumentsDirectory();
    return directory.path;
  }

  static Future<Directory> get tempDirectory async {
    return await getTemporaryDirectory();
  }

  static Future<int> getDirectorySize(Directory dir) async {
    int size = 0;
    try {
      if (dir.existsSync()) {
        dir.listSync(recursive: true, followLinks: false)
            .forEach((FileSystemEntity entity) {
          if (entity is File) {
            size += entity.lengthSync();
          }
        });
      }
    } catch (e) {
      print('Error calculating directory size: $e');
    }
    return size;
  }

  static Future<void> clearDirectory(Directory dir) async {
    try {
      if (dir.existsSync()) {
        await dir.delete(recursive: true);
        await dir.create();
      }
    } catch (e) {
      print('Error clearing directory: $e');
    }
  }
} 