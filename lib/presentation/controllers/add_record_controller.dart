import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:suoke_life/services/life_record_service.dart';
import 'package:suoke_life/services/location_service.dart';

class AddRecordController extends GetxController {
  final LifeRecordService _recordService = Get.find();
  final LocationService _locationService = Get.find();
  
  final contentController = TextEditingController();
  final selectedTags = <String>[].obs;
  final images = <File>[].obs;
  final location = Rx<String?>(null);

  @override
  void onInit() {
    super.onInit();
    _getCurrentLocation();
  }

  @override
  void onClose() {
    contentController.dispose();
    super.onClose();
  }

  void toggleTag(String tag) {
    if (selectedTags.contains(tag)) {
      selectedTags.remove(tag);
    } else {
      selectedTags.add(tag);
    }
  }

  Future<void> pickImage() async {
    try {
      final picker = ImagePicker();
      final pickedFile = await picker.pickImage(source: ImageSource.gallery);
      
      if (pickedFile != null) {
        images.add(File(pickedFile.path));
      }
    } catch (e) {
      Get.snackbar('错误', '选择图片失败: $e');
    }
  }

  void removeImage(File image) {
    images.remove(image);
  }

  Future<void> _getCurrentLocation() async {
    try {
      final currentLocation = await _locationService.getCurrentLocation();
      location.value = currentLocation;
    } catch (e) {
      print('获取位置失败: $e');
    }
  }

  Future<void> saveRecord() async {
    if (contentController.text.isEmpty) {
      Get.snackbar('提示', '请输入内容');
      return;
    }

    try {
      await _recordService.addRecord(
        content: contentController.text,
        tags: selectedTags,
        images: images,
        location: location.value,
      );
      
      Get.back(result: true);
      Get.snackbar('成功', '记录已保存');
    } catch (e) {
      Get.snackbar('错误', '保存失败: $e');
    }
  }
} 