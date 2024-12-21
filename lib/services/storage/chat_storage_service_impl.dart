import 'dart:io';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:video_thumbnail/video_thumbnail.dart';
import 'package:hive/hive.dart';
import '../../models/message.dart';
import 'chat_storage_service.dart';

class ChatStorageServiceImpl implements ChatStorageService {
  final Box<Message> _messageBox;
  final Dio _dio;
  
  ChatStorageServiceImpl(this._messageBox) : _dio = Dio(BaseOptions(
    baseUrl: 'https://api.suoke.life/v1/storage',
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
  ));

  @override
  Future<List<Message>> getMessages() async {
    return _messageBox.values.toList();
  }

  @override
  Future<void> saveMessage(Message message) async {
    await _messageBox.put(message.id, message);
  }

  @override
  Future<String> uploadVoice(String path) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(path),
        'type': 'voice',
      });

      final response = await _dio.post(
        '/upload',
        data: formData,
      );

      if (response.statusCode == 200) {
        return response.data['url'];
      }
      throw Exception('上传失败');
    } catch (e) {
      print('Error in uploadVoice: $e');
      throw Exception('语音上传失败');
    }
  }

  @override
  Future<String> uploadImage(String path) async {
    try {
      // 1. 压缩图片
      final compressedImage = await compressImage(path);
      
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(compressedImage.path),
        'type': 'image',
      });

      final response = await _dio.post(
        '/upload',
        data: formData,
      );

      if (response.statusCode == 200) {
        return response.data['url'];
      }
      throw Exception('上传失败');
    } catch (e) {
      print('Error in uploadImage: $e');
      throw Exception('图片上传失败');
    }
  }

  @override
  Future<String> uploadVideo(String path) async {
    try {
      // 1. 压缩视频
      final compressedVideo = await compressVideo(path);
      
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(compressedVideo.path),
        'type': 'video',
      });

      final response = await _dio.post(
        '/upload',
        data: formData,
      );

      if (response.statusCode == 200) {
        return response.data['url'];
      }
      throw Exception('上传失败');
    } catch (e) {
      print('Error in uploadVideo: $e');
      throw Exception('视频上传失败');
    }
  }

  @override
  Future<String> generateThumbnail(String videoPath) async {
    try {
      final thumbnailPath = await VideoThumbnail.thumbnailFile(
        video: videoPath,
        thumbnailPath: (await getTemporaryDirectory()).path,
        imageFormat: ImageFormat.JPEG,
        quality: 75,
      );

      if (thumbnailPath == null) {
        throw Exception('生成缩略图失败');
      }

      // 上传缩略图
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(thumbnailPath),
        'type': 'thumbnail',
      });

      final response = await _dio.post(
        '/upload',
        data: formData,
      );

      if (response.statusCode == 200) {
        return response.data['url'];
      }
      throw Exception('上传失败');
    } catch (e) {
      print('Error in generateThumbnail: $e');
      throw Exception('缩略图生成失败');
    }
  }

  // 辅助方法
  Future<File> compressImage(String path) async {
    // 实现图片压缩
    return File(path);
  }

  Future<File> compressVideo(String path) async {
    // 实现视频压缩
    return File(path);
  }
} 