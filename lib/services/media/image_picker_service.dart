import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import '../storage/storage_quota_service.dart';

class ImagePickerService {
  final ImagePicker _picker;
  final StorageQuotaService _quotaService;

  ImagePickerService(this._quotaService) : _picker = ImagePicker();

  Future<File?> pickImage({
    ImageSource source = ImageSource.gallery,
    int maxWidth = 1920,
    int maxHeight = 1080,
    int imageQuality = 85,
  }) async {
    // 检查权限
    final permission = source == ImageSource.camera
        ? Permission.camera
        : Permission.photos;
    
    final status = await permission.request();
    if (status != PermissionStatus.granted) {
      throw Exception('需要${source == ImageSource.camera ? "相机" : "相册"}权限');
    }

    // 选择图片
    final image = await _picker.pickImage(
      source: source,
      maxWidth: maxWidth,
      maxHeight: maxHeight,
      imageQuality: imageQuality,
    );

    if (image != null) {
      // 检查存储配额
      final file = File(image.path);
      final size = await file.length();
      
      if (!await _quotaService.checkStorageAvailable(size)) {
        throw Exception('存储空间不足');
      }

      return file;
    }
    return null;
  }

  Future<List<File>> pickMultiImage({
    int maxImages = 9,
    int maxWidth = 1920,
    int maxHeight = 1080,
    int imageQuality = 85,
  }) async {
    final status = await Permission.photos.request();
    if (status != PermissionStatus.granted) {
      throw Exception('需要相册权限');
    }

    final images = await _picker.pickMultiImage(
      maxWidth: maxWidth,
      maxHeight: maxHeight,
      imageQuality: imageQuality,
    );

    if (images.isNotEmpty) {
      final files = images.map((image) => File(image.path)).toList();
      
      // 检查总大小
      int totalSize = 0;
      for (var file in files) {
        totalSize += await file.length();
      }
      
      if (!await _quotaService.checkStorageAvailable(totalSize)) {
        throw Exception('存储空间不足');
      }

      return files.take(maxImages).toList();
    }
    return [];
  }
} 