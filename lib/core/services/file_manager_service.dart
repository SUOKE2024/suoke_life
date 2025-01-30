import 'package:get/get.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class FileManagerService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final currentDirectory = Rx<Directory?>(null);
  final files = <FileSystemEntity>[].obs;
  final selectedFiles = <FileSystemEntity>[].obs;

  @override
  void onInit() {
    super.onInit();
    _initFileManager();
  }

  Future<void> _initFileManager() async {
    try {
      final appDir = await getApplicationDocumentsDirectory();
      await changeDirectory(appDir);
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize file manager', data: {'error': e.toString()});
    }
  }

  // 切换目录
  Future<void> changeDirectory(Directory directory) async {
    try {
      currentDirectory.value = directory;
      await _loadFiles();
    } catch (e) {
      await _loggingService.log('error', 'Failed to change directory', data: {'path': directory.path, 'error': e.toString()});
      rethrow;
    }
  }

  // 创建文件夹
  Future<void> createDirectory(String name) async {
    try {
      final newDir = Directory('${currentDirectory.value!.path}/$name');
      await newDir.create();
      await _loadFiles();
    } catch (e) {
      await _loggingService.log('error', 'Failed to create directory', data: {'name': name, 'error': e.toString()});
      rethrow;
    }
  }

  // 创建文件
  Future<void> createFile(String name, List<int> data) async {
    try {
      final file = File('${currentDirectory.value!.path}/$name');
      await file.writeAsBytes(data);
      await _loadFiles();
    } catch (e) {
      await _loggingService.log('error', 'Failed to create file', data: {'name': name, 'error': e.toString()});
      rethrow;
    }
  }

  // 删除文件/文件夹
  Future<void> delete(FileSystemEntity entity) async {
    try {
      await entity.delete(recursive: true);
      await _loadFiles();
    } catch (e) {
      await _loggingService.log('error', 'Failed to delete', data: {'path': entity.path, 'error': e.toString()});
      rethrow;
    }
  }

  // 重命名
  Future<void> rename(FileSystemEntity entity, String newName) async {
    try {
      final newPath = '${entity.parent.path}/$newName';
      await entity.rename(newPath);
      await _loadFiles();
    } catch (e) {
      await _loggingService.log('error', 'Failed to rename', data: {'path': entity.path, 'newName': newName, 'error': e.toString()});
      rethrow;
    }
  }

  // 移动文件/文件夹
  Future<void> move(FileSystemEntity entity, Directory destination) async {
    try {
      final newPath = '${destination.path}/${entity.path.split('/').last}';
      await entity.rename(newPath);
      await _loadFiles();
    } catch (e) {
      await _loggingService.log('error', 'Failed to move', data: {'path': entity.path, 'destination': destination.path, 'error': e.toString()});
      rethrow;
    }
  }

  // 复制文件/文件夹
  Future<void> copy(FileSystemEntity entity, Directory destination) async {
    try {
      if (entity is File) {
        await _copyFile(entity, destination);
      } else if (entity is Directory) {
        await _copyDirectory(entity, destination);
      }
      await _loadFiles();
    } catch (e) {
      await _loggingService.log('error', 'Failed to copy', data: {'path': entity.path, 'destination': destination.path, 'error': e.toString()});
      rethrow;
    }
  }

  Future<void> _loadFiles() async {
    try {
      if (currentDirectory.value == null) return;
      
      final entities = await currentDirectory.value!.list().toList();
      entities.sort((a, b) {
        if (a is Directory && b is File) return -1;
        if (a is File && b is Directory) return 1;
        return a.path.compareTo(b.path);
      });
      
      files.value = entities;
    } catch (e) {
      await _loggingService.log('error', 'Failed to load files', data: {'error': e.toString()});
      rethrow;
    }
  }

  Future<void> _copyFile(File file, Directory destination) async {
    try {
      final newPath = '${destination.path}/${file.path.split('/').last}';
      await file.copy(newPath);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _copyDirectory(Directory source, Directory destination) async {
    try {
      final newPath = '${destination.path}/${source.path.split('/').last}';
      final newDir = await Directory(newPath).create();
      
      await for (final entity in source.list(recursive: false)) {
        if (entity is File) {
          await _copyFile(entity, newDir);
        } else if (entity is Directory) {
          await _copyDirectory(entity, newDir);
        }
      }
    } catch (e) {
      rethrow;
    }
  }
} 