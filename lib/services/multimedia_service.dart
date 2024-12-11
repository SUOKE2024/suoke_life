import 'dart:async';
import 'dart:io';
import 'package:camera/camera.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'package:path/path.dart' as path;
import '../core/network/http_client.dart';
import '../services/nas_storage_service.dart';

enum MediaType {
  image,
  video,
  document,
  medicalReport
}

class MediaData {
  final String id;
  final MediaType type;
  final File file;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  MediaData({
    required this.id,
    required this.type,
    required this.file,
    required this.timestamp,
    this.metadata,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'type': type.toString(),
    'path': file.path,
    'timestamp': timestamp.toIso8601String(),
    'metadata': metadata,
  };
}

class MultimediaService {
  final HttpClient _httpClient;
  final NasStorageService _nasService;
  final ImagePicker _imagePicker = ImagePicker();
  CameraController? _cameraController;
  bool _isInitialized = false;

  final StreamController<MediaData> _mediaStreamController = 
      StreamController<MediaData>.broadcast();

  MultimediaService({
    required HttpClient httpClient,
    required String nasBasePath,
  }) : _httpClient = httpClient,
       _nasService = NasStorageService(nasBasePath: nasBasePath);

  Future<void> initializeCamera() async {
    if (_isInitialized) return;

    final cameras = await availableCameras();
    if (cameras.isEmpty) {
      throw Exception('没有可用的摄像头');
    }

    _cameraController = CameraController(
      cameras.first,
      ResolutionPreset.high,
      enableAudio: false,
    );

    await _cameraController!.initialize();
    _isInitialized = true;
  }

  Future<MediaData> takePicture() async {
    if (!_isInitialized) {
      await initializeCamera();
    }

    final XFile image = await _cameraController!.takePicture();
    final file = File(image.path);
    
    final mediaData = MediaData(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      type: MediaType.image,
      file: file,
      timestamp: DateTime.now(),
      metadata: {
        'source': 'camera',
        'size': await file.length(),
        'extension': path.extension(file.path),
      },
    );

    _mediaStreamController.add(mediaData);
    await _saveMedia(mediaData);
    
    return mediaData;
  }

  Future<MediaData?> pickImage({bool fromCamera = false}) async {
    final XFile? image = await _imagePicker.pickImage(
      source: fromCamera ? ImageSource.camera : ImageSource.gallery,
      imageQuality: 85,
    );

    if (image == null) return null;

    final file = File(image.path);
    final mediaData = MediaData(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      type: MediaType.image,
      file: file,
      timestamp: DateTime.now(),
      metadata: {
        'source': fromCamera ? 'camera' : 'gallery',
        'size': await file.length(),
        'extension': path.extension(file.path),
      },
    );

    _mediaStreamController.add(mediaData);
    await _saveMedia(mediaData);
    
    return mediaData;
  }

  Future<MediaData?> pickVideo({bool fromCamera = false}) async {
    final XFile? video = await _imagePicker.pickVideo(
      source: fromCamera ? ImageSource.camera : ImageSource.gallery,
      maxDuration: const Duration(minutes: 10),
    );

    if (video == null) return null;

    final file = File(video.path);
    final mediaData = MediaData(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      type: MediaType.video,
      file: file,
      timestamp: DateTime.now(),
      metadata: {
        'source': fromCamera ? 'camera' : 'gallery',
        'size': await file.length(),
        'extension': path.extension(file.path),
      },
    );

    _mediaStreamController.add(mediaData);
    await _saveMedia(mediaData);
    
    return mediaData;
  }

  Future<MediaData?> pickFile({
    List<String>? allowedExtensions,
    MediaType type = MediaType.document,
  }) async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: allowedExtensions,
    );

    if (result == null) return null;

    final file = File(result.files.single.path!);
    final mediaData = MediaData(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      type: type,
      file: file,
      timestamp: DateTime.now(),
      metadata: {
        'size': await file.length(),
        'extension': path.extension(file.path),
        'name': path.basename(file.path),
      },
    );

    _mediaStreamController.add(mediaData);
    await _saveMedia(mediaData);
    
    return mediaData;
  }

  Future<void> _saveMedia(MediaData media) async {
    try {
      // 保存到本地存储
      await _nasService.saveVoiceRecord(
        content: media.toJson(),
        timestamp: media.timestamp,
        type: 'media_${media.type.toString().split('.').last}',
      );

      // 上传到服务器
      await _uploadMedia(media);
    } catch (e) {
      print('保存媒体文件失败: $e');
    }
  }

  Future<void> _uploadMedia(MediaData media) async {
    try {
      // 构建上传请求
      final uri = Uri.parse('YOUR_API_ENDPOINT');
      final request = await _httpClient.multipartRequest('POST', uri);
      
      // 添加文件
      request.files.add(
        await _httpClient.multipartFile(
          'file',
          media.file.readAsBytes().asStream(),
          await media.file.length(),
          filename: path.basename(media.file.path),
        ),
      );

      // 添加元数据
      request.fields['type'] = media.type.toString();
      request.fields['timestamp'] = media.timestamp.toIso8601String();
      if (media.metadata != null) {
        request.fields['metadata'] = media.metadata.toString();
      }

      // 发送请求
      final response = await request.send();
      if (response.statusCode != 200) {
        throw Exception('上传失败: ${response.statusCode}');
      }
    } catch (e) {
      print('上传媒体文件失败: $e');
      rethrow;
    }
  }

  Future<List<MediaData>> getMediaHistory({MediaType? type}) async {
    final records = await _nasService.getVoiceRecords();
    return records
        .where((record) => type == null || 
            record['type'] == 'media_${type.toString().split('.').last}')
        .map((record) {
          final Map<String, dynamic> data = record['content'];
          return MediaData(
            id: data['id'],
            type: MediaType.values.firstWhere(
              (e) => e.toString() == data['type'],
            ),
            file: File(data['path']),
            timestamp: DateTime.parse(data['timestamp']),
            metadata: data['metadata'],
          );
        })
        .toList();
  }

  void dispose() {
    _mediaStreamController.close();
    _cameraController?.dispose();
  }

  // Getters
  bool get isInitialized => _isInitialized;
  Stream<MediaData> get mediaStream => _mediaStreamController.stream;
  CameraController? get cameraController => _cameraController;
} 