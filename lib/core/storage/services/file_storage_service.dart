import 'dart:io';
import 'package:dio/dio.dart';
import 'package:path/path.dart' as path;
import '../../network/http_client.dart';
import '../../error/app_error.dart';
import '../../logging/app_logger.dart';

class FileStorageService {
  static final FileStorageService _instance = FileStorageService._internal();
  static FileStorageService get instance => _instance;

  final _httpClient = HttpClient.instance;
  final _logger = AppLogger.instance;

  FileStorageService._internal();

  Future<String> uploadFile({
    required File file,
    required String type,
    void Function(int sent, int total)? onProgress,
  }) async {
    try {
      final fileName = path.basename(file.path);
      final extension = path.extension(fileName).toLowerCase();
      
      // 验证文件类型
      if (!_isValidFileType(type, extension)) {
        throw ValidationError(
          '不支持的文件类型',
          {'file': '文件类型 $extension 不支持'},
        );
      }

      // 验证文件大小
      final fileSize = await file.length();
      if (!_isValidFileSize(type, fileSize)) {
        throw ValidationError(
          '文件太大',
          {'file': '文件大小超过限制'},
        );
      }

      // 准备上传数据
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          file.path,
          filename: fileName,
        ),
        'type': type,
      });

      // 发起上传请求
      final response = await _httpClient.post<Map<String, dynamic>>(
        '/storage/upload',
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        ),
        onSendProgress: onProgress,
      );

      return response['url'] as String;
    } catch (e) {
      _logger.error('文件上传失败', error: e);
      rethrow;
    }
  }

  Future<String> uploadImage({
    required File file,
    void Function(int sent, int total)? onProgress,
  }) {
    return uploadFile(
      file: file,
      type: 'image',
      onProgress: onProgress,
    );
  }

  bool _isValidFileType(String type, String extension) {
    final allowedExtensions = _getAllowedExtensions(type);
    return allowedExtensions.contains(extension);
  }

  bool _isValidFileSize(String type, int size) {
    final maxSize = _getMaxFileSize(type);
    return size <= maxSize;
  }

  Set<String> _getAllowedExtensions(String type) {
    switch (type) {
      case 'image':
        return {'.jpg', '.jpeg', '.png', '.gif'};
      case 'document':
        return {'.pdf', '.doc', '.docx'};
      case 'video':
        return {'.mp4', '.mov', '.avi'};
      default:
        return {};
    }
  }

  int _getMaxFileSize(String type) {
    switch (type) {
      case 'image':
        return 5 * 1024 * 1024; // 5MB
      case 'document':
        return 10 * 1024 * 1024; // 10MB
      case 'video':
        return 50 * 1024 * 1024; // 50MB
      default:
        return 1024 * 1024; // 1MB
    }
  }

  Future<void> deleteFile(String url) async {
    try {
      await _httpClient.post(
        '/storage/delete',
        data: {'url': url},
      );
    } catch (e) {
      _logger.error('删除文件失败', error: e);
      rethrow;
    }
  }
} 