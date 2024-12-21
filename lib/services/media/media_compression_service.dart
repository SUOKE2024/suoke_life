import 'dart:io';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:video_compress/video_compress.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;

class MediaCompressionService {
  static final MediaCompressionService _instance = MediaCompressionService._();
  factory MediaCompressionService() => _instance;
  MediaCompressionService._();

  Future<File> compressImage(String imagePath, {
    int quality = 85,
    int? targetWidth,
    int? targetHeight,
  }) async {
    final dir = await getTemporaryDirectory();
    final targetPath = path.join(
      dir.path,
      'compressed_${path.basename(imagePath)}',
    );

    final result = await FlutterImageCompress.compressAndGetFile(
      imagePath,
      targetPath,
      quality: quality,
      minWidth: targetWidth ?? 1024,
      minHeight: targetHeight ?? 1024,
    );

    if (result == null) {
      throw Exception('图片压缩失败');
    }

    return File(result.path);
  }

  Future<File> compressVideo(String videoPath) async {
    try {
      final MediaInfo? mediaInfo = await VideoCompress.compressVideo(
        videoPath,
        quality: VideoQuality.MediumQuality,
        deleteOrigin: false,
        includeAudio: true,
      );

      if (mediaInfo?.file == null) {
        throw Exception('视频压缩失败');
      }

      return mediaInfo!.file!;
    } catch (e) {
      print('Error in compressVideo: $e');
      throw Exception('视频压缩失败');
    }
  }

  Future<void> cancelCompression() async {
    await VideoCompress.cancelCompression();
  }

  Future<void> deleteAllCache() async {
    await VideoCompress.deleteAllCache();
    // 清理图片缓存
    final dir = await getTemporaryDirectory();
    final files = dir.listSync();
    for (var file in files) {
      if (file is File && file.path.contains('compressed_')) {
        await file.delete();
      }
    }
  }
} 