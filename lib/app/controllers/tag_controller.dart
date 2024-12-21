import 'package:get/get.dart';
import 'package:uuid/uuid.dart';
import '../data/models/tag.dart';
import '../data/repositories/tag_repository.dart';
import 'package:flutter/material.dart';

class TagController extends GetxController {
  final TagRepository _repository;
  
  TagController(this._repository);

  final tags = <Tag>[].obs;
  final isLoading = false.obs;

  @override
  void onInit() {
    super.onInit();
    loadTags();
  }

  Future<void> loadTags() async {
    try {
      isLoading.value = true;
      final loadedTags = await _repository.getAllTags();
      tags.value = loadedTags;
    } catch (e) {
      Get.snackbar('错误', '加载标签失败：$e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> addTag(String name, Color color) async {
    try {
      final tag = Tag(
        id: const Uuid().v4(),
        name: name,
        color: color,
        createdAt: DateTime.now(),
      );
      await _repository.saveTag(tag);
      tags.add(tag);
      Get.back();
      Get.snackbar('成功', '标签已添加');
    } catch (e) {
      Get.snackbar('错误', '添加标签失���：$e');
    }
  }

  Future<void> updateTag(Tag tag, {String? name, Color? color}) async {
    try {
      final updatedTag = Tag(
        id: tag.id,
        name: name ?? tag.name,
        color: color ?? tag.color,
        createdAt: tag.createdAt,
      );
      await _repository.updateTag(updatedTag);
      final index = tags.indexWhere((t) => t.id == tag.id);
      if (index != -1) {
        tags[index] = updatedTag;
      }
      Get.back();
      Get.snackbar('成功', '标签已更新');
    } catch (e) {
      Get.snackbar('错误', '更新标签失败：$e');
    }
  }

  Future<void> deleteTag(String id) async {
    try {
      await _repository.deleteTag(id);
      tags.removeWhere((tag) => tag.id == id);
      Get.snackbar('成功', '标签已删除');
    } catch (e) {
      Get.snackbar('错误', '删除标签失败：$e');
    }
  }
} 