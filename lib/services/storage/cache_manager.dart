import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;

class CacheManager {
  static const Duration defaultMaxAge = Duration(days: 7);
  
  Future<String> getCachePath() async {
    final dir = await getTemporaryDirectory();
    return dir.path;
  }

  Future<int> getCacheSize() async {
    int totalSize = 0;
    final dir = Directory(await getCachePath());
    
    await for (var entity in dir.list(recursive: true)) {
      if (entity is File) {
        totalSize += await entity.length();
      }
    }
    
    return totalSize;
  }

  Future<void> clearCache() async {
    final dir = Directory(await getCachePath());
    if (await dir.exists()) {
      await dir.delete(recursive: true);
      await dir.create();
    }
  }

  Future<void> cleanupOldCache({Duration? maxAge}) async {
    maxAge ??= defaultMaxAge;
    final dir = Directory(await getCachePath());
    
    await for (var entity in dir.list(recursive: true)) {
      if (entity is File) {
        final stat = await entity.stat();
        final age = DateTime.now().difference(stat.modified);
        
        if (age > maxAge) {
          await entity.delete();
        }
      }
    }
  }

  Future<File> getCachedFile(String url) async {
    final filename = path.basename(url);
    final cacheDir = await getCachePath();
    return File('$cacheDir/$filename');
  }

  Future<bool> isCached(String url) async {
    final file = await getCachedFile(url);
    return file.exists();
  }

  Future<File> cacheFile(String url, List<int> bytes) async {
    final file = await getCachedFile(url);
    return file.writeAsBytes(bytes);
  }
} 