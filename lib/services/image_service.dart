import 'package:image_picker/image_picker.dart';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';
import 'dart:io';

class ImageService {
  final ImagePicker _picker = ImagePicker();
  
  // 从相册选择图片
  Future<String?> pickImage() async {
    final XFile? image = await _picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 1080,
      maxHeight: 1080,
      imageQuality: 85,
    );
    
    if (image != null) {
      // 复制图片到应用目录
      return await _saveImageToLocal(File(image.path));
    }
    return null;
  }
  
  // 拍照
  Future<String?> takePhoto() async {
    final XFile? photo = await _picker.pickImage(
      source: ImageSource.camera,
      maxWidth: 1080,
      maxHeight: 1080,
      imageQuality: 85,
    );
    
    if (photo != null) {
      return await _saveImageToLocal(File(photo.path));
    }
    return null;
  }
  
  // 保存图片到本地
  Future<String> _saveImageToLocal(File image) async {
    final appDir = await getApplicationDocumentsDirectory();
    final fileName = '${DateTime.now().millisecondsSinceEpoch}${path.extension(image.path)}';
    final savedImage = await image.copy('${appDir.path}/images/$fileName');
    return savedImage.path;
  }
  
  // 删除本地图片
  Future<void> deleteImage(String imagePath) async {
    final file = File(imagePath);
    if (await file.exists()) {
      await file.delete();
    }
  }
} 