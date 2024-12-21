import 'dart:io';
import 'package:image/image.dart' as img;
import '../data/remote/oss/oss_storage.dart';

enum MediaProcessType {
  resize,     // 调整大小
  compress,   // 压缩
  watermark,  // 水印
  transcode,  // 转码
  thumbnail,  // 缩略图
}

class MediaService {
  final OssStorage _ossStorage;

  MediaService(this._ossStorage);

  // 处理图片
  Future<String> processImage(
    String imagePath,
    List<MediaProcessConfig> configs,
  ) async {
    var image = img.decodeImage(File(imagePath).readAsBytesSync())!;

    for (final config in configs) {
      switch (config.type) {
        case MediaProcessType.resize:
          image = _resizeImage(image, config.params);
          break;
        case MediaProcessType.compress:
          image = _compressImage(image, config.params);
          break;
        case MediaProcessType.watermark:
          image = await _addWatermark(image, config.params);
          break;
        case MediaProcessType.thumbnail:
          image = _createThumbnail(image, config.params);
          break;
        default:
          throw Exception('不支持的图片处理类���: ${config.type}');
      }
    }

    // 保存处理后的图片
    final tempPath = '${imagePath}_processed';
    File(tempPath).writeAsBytesSync(img.encodeJpg(image));

    // 上传到OSS
    return await _ossStorage.uploadMedia(tempPath, 'image/jpeg');
  }

  // 处理视频
  Future<String> processVideo(
    String videoPath,
    List<MediaProcessConfig> configs,
  ) async {
    // TODO: 实现视频处理
    return videoPath;
  }

  // 处理音频
  Future<String> processAudio(
    String audioPath,
    List<MediaProcessConfig> configs,
  ) async {
    // TODO: 实现音频处理
    return audioPath;
  }

  // 调整图片大小
  img.Image _resizeImage(img.Image image, Map<String, dynamic> params) {
    final width = params['width'] as int?;
    final height = params['height'] as int?;
    
    if (width != null && height != null) {
      return img.copyResize(image, width: width, height: height);
    } else if (width != null) {
      final ratio = width / image.width;
      return img.copyResize(
        image,
        width: width,
        height: (image.height * ratio).round(),
      );
    } else if (height != null) {
      final ratio = height / image.height;
      return img.copyResize(
        image,
        width: (image.width * ratio).round(),
        height: height,
      );
    }
    return image;
  }

  // 压缩图片
  img.Image _compressImage(img.Image image, Map<String, dynamic> params) {
    final quality = params['quality'] as int? ?? 85;
    return img.copyResize(
      image,
      width: (image.width * 0.8).round(),
      height: (image.height * 0.8).round(),
      interpolation: img.Interpolation.linear,
    );
  }

  // 添加水印
  Future<img.Image> _addWatermark(
    img.Image image,
    Map<String, dynamic> params,
  ) async {
    final watermarkPath = params['watermarkPath'] as String;
    final position = params['position'] as String? ?? 'bottomRight';
    
    final watermark = img.decodeImage(File(watermarkPath).readAsBytesSync())!;
    
    // 计算水印位置
    int x = 0, y = 0;
    switch (position) {
      case 'topLeft':
        x = 10;
        y = 10;
        break;
      case 'topRight':
        x = image.width - watermark.width - 10;
        y = 10;
        break;
      case 'bottomLeft':
        x = 10;
        y = image.height - watermark.height - 10;
        break;
      case 'bottomRight':
        x = image.width - watermark.width - 10;
        y = image.height - watermark.height - 10;
        break;
      case 'center':
        x = (image.width - watermark.width) ~/ 2;
        y = (image.height - watermark.height) ~/ 2;
        break;
    }

    // 合成水印
    img.compositeImage(image, watermark, dstX: x, dstY: y);
    return image;
  }

  // 创建缩略图
  img.Image _createThumbnail(img.Image image, Map<String, dynamic> params) {
    final size = params['size'] as int? ?? 200;
    final ratio = image.width / image.height;
    
    if (ratio > 1) {
      return img.copyResize(
        image,
        width: size,
        height: (size / ratio).round(),
      );
    } else {
      return img.copyResize(
        image,
        width: (size * ratio).round(),
        height: size,
      );
    }
  }
}

class MediaProcessConfig {
  final MediaProcessType type;
  final Map<String, dynamic> params;

  MediaProcessConfig({
    required this.type,
    required this.params,
  });
} 