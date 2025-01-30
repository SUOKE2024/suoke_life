import 'package:get/get.dart';
import '../core/network/api_client.dart';
import '../data/models/group_file.dart';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:open_file/open_file.dart';

class GroupFilesService extends GetxService {
  final ApiClient _apiClient;
  
  GroupFilesService({required ApiClient apiClient}) : _apiClient = apiClient;

  // 获取文件列表
  Future<List<GroupFile>> getFiles(String groupId, {String? type}) async {
    try {
      final response = await _apiClient.get(
        '/groups/$groupId/files',
        queryParameters: {
          if (type != null) 'type': type,
        },
      );
      return (response['files'] as List)
          .map((json) => GroupFile.fromJson(json))
          .toList();
    } catch (e) {
      rethrow;
    }
  }

  // 获取存储信息
  Future<Map<String, int>> getStorageInfo(String groupId) async {
    try {
      final response = await _apiClient.get('/groups/$groupId/storage');
      return {
        'used': response['used'],
        'remaining': response['remaining'],
        'total': response['total'],
      };
    } catch (e) {
      rethrow;
    }
  }

  // 上传文件
  Future<void> uploadFile(
    String groupId,
    File file, {
    Function(double)? onProgress,
  }) async {
    try {
      final formData = FormData({
        'file': MultipartFile(
          file.path,
          filename: file.path.split('/').last,
        ),
      });

      await _apiClient.post(
        '/groups/$groupId/files',
        data: formData,
        onUploadProgress: (sent, total) {
          if (onProgress != null) {
            onProgress(sent / total);
          }
        },
      );
    } catch (e) {
      rethrow;
    }
  }

  // 下载文件
  Future<void> downloadFile(
    GroupFile file, {
    Function(double)? onProgress,
  }) async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final savePath = '${dir.path}/${file.name}';

      await _apiClient.download(
        file.url,
        savePath,
        onDownloadProgress: (received, total) {
          if (onProgress != null) {
            onProgress(received / total);
          }
        },
      );
    } catch (e) {
      rethrow;
    }
  }

  // 删除文件
  Future<void> deleteFile(String groupId, String fileId) async {
    try {
      await _apiClient.delete('/groups/$groupId/files/$fileId');
    } catch (e) {
      rethrow;
    }
  }

  // 打开文件
  Future<void> openFile(GroupFile file) async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final filePath = '${dir.path}/${file.name}';
      final exists = await File(filePath).exists();

      if (!exists) {
        // 如果文件不存在，先下载
        await downloadFile(file);
      }

      final result = await OpenFile.open(filePath);
      if (result.type != ResultType.done) {
        throw Exception(result.message);
      }
    } catch (e) {
      rethrow;
    }
  }
} 