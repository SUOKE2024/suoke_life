import 'package:injectable/injectable.dart';
import 'package:image/image.dart' as img;
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import '../logger/logger.dart';

@singleton
class ImageService {
  final AppLogger _logger;

  ImageService(this._logger);

  Future<File?> compressImage(File file, {int quality = 85}) async {
    try {
      final bytes = await file.readAsBytes();
      final image = img.decodeImage(bytes);
      
      if (image == null) return null;

      final compressed = img.encodeJpg(image, quality: quality);
      final dir = await getTemporaryDirectory();
      final compressedFile = File(
        '${dir.path}/compressed_${DateTime.now().millisecondsSinceEpoch}.jpg',
      );
      
      await compressedFile.writeAsBytes(compressed);
      return compressedFile;
    } catch (e, stack) {
      _logger.error('Error compressing image', e, stack);
      return null;
    }
  }

  Future<File?> resizeImage(
    File file, {
    required int maxWidth,
    required int maxHeight,
  }) async {
    try {
      final bytes = await file.readAsBytes();
      final image = img.decodeImage(bytes);
      
      if (image == null) return null;

      final resized = img.copyResize(
        image,
        width: maxWidth,
        height: maxHeight,
        interpolation: img.Interpolation.linear,
      );

      final dir = await getTemporaryDirectory();
      final resizedFile = File(
        '${dir.path}/resized_${DateTime.now().millisecondsSinceEpoch}.jpg',
      );
      
      await resizedFile.writeAsBytes(img.encodeJpg(resized));
      return resizedFile;
    } catch (e, stack) {
      _logger.error('Error resizing image', e, stack);
      return null;
    }
  }

  Future<Map<String, int>?> getImageDimensions(File file) async {
    try {
      final bytes = await file.readAsBytes();
      final image = img.decodeImage(bytes);
      
      if (image == null) return null;

      return {
        'width': image.width,
        'height': image.height,
      };
    } catch (e, stack) {
      _logger.error('Error getting image dimensions', e, stack);
      return null;
    }
  }
} 