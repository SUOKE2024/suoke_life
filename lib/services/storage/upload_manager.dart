import 'dart:io';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:convert';

class UploadTask {
  final String id;
  final String filePath;
  final String type;
  final Map<String, dynamic>? metadata;
  int progress;
  String? resumeToken;

  UploadTask({
    required this.id,
    required this.filePath,
    required this.type,
    this.metadata,
    this.progress = 0,
    this.resumeToken,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'filePath': filePath,
    'type': type,
    'metadata': metadata,
    'progress': progress,
    'resumeToken': resumeToken,
  };

  factory UploadTask.fromJson(Map<String, dynamic> json) => UploadTask(
    id: json['id'],
    filePath: json['filePath'],
    type: json['type'],
    metadata: json['metadata'],
    progress: json['progress'],
    resumeToken: json['resumeToken'],
  );
}

class UploadManager {
  final Dio _dio;
  final String _taskFilePath;
  final Map<String, UploadTask> _tasks = {};
  
  UploadManager(this._dio) : _taskFilePath = '';

  Future<void> init() async {
    final dir = await getApplicationDocumentsDirectory();
    _taskFilePath = '${dir.path}/upload_tasks.json';
    await _loadTasks();
  }

  Future<void> _loadTasks() async {
    try {
      final file = File(_taskFilePath);
      if (await file.exists()) {
        final content = await file.readAsString();
        final List<dynamic> tasks = json.decode(content);
        _tasks.clear();
        for (var task in tasks) {
          final uploadTask = UploadTask.fromJson(task);
          _tasks[uploadTask.id] = uploadTask;
        }
      }
    } catch (e) {
      print('Error loading tasks: $e');
    }
  }

  Future<void> _saveTasks() async {
    try {
      final file = File(_taskFilePath);
      await file.writeAsString(json.encode(_tasks.values.toList()));
    } catch (e) {
      print('Error saving tasks: $e');
    }
  }

  Future<String> startUpload(String filePath, String type, {
    Map<String, dynamic>? metadata,
  }) async {
    final task = UploadTask(
      id: DateTime.now().toString(),
      filePath: filePath,
      type: type,
      metadata: metadata,
    );

    _tasks[task.id] = task;
    await _saveTasks();

    _uploadFile(task);
    return task.id;
  }

  Future<void> _uploadFile(UploadTask task) async {
    try {
      final file = File(task.filePath);
      final fileSize = await file.length();

      final response = await _dio.post(
        '/upload',
        data: FormData.fromMap({
          'file': await MultipartFile.fromFile(
            task.filePath,
            filename: task.id,
          ),
          'type': task.type,
          'metadata': task.metadata,
          'resumeToken': task.resumeToken,
        }),
        onSendProgress: (sent, total) {
          task.progress = ((sent / total) * 100).round();
          _saveTasks();
        },
        options: Options(
          headers: {
            'Content-Length': fileSize,
            'Content-Type': 'multipart/form-data',
          },
        ),
      );

      if (response.statusCode == 200) {
        _tasks.remove(task.id);
        await _saveTasks();
      } else if (response.statusCode == 308) {
        // 断点续传
        task.resumeToken = response.headers.value('Upload-Token');
        task.progress = int.parse(response.headers.value('Upload-Progress') ?? '0');
        await _saveTasks();
        await _uploadFile(task); // 继续上传
      }
    } catch (e) {
      print('Error uploading file: $e');
      // 保存进度,稍后重试
      await _saveTasks();
    }
  }

  Future<void> retryUpload(String taskId) async {
    final task = _tasks[taskId];
    if (task != null) {
      await _uploadFile(task);
    }
  }

  Future<void> cancelUpload(String taskId) async {
    _tasks.remove(taskId);
    await _saveTasks();
  }

  Future<void> cancelAll() async {
    _tasks.clear();
    await _saveTasks();
  }

  List<UploadTask> getPendingTasks() {
    return _tasks.values.toList();
  }
} 