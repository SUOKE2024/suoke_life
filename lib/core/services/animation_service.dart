import 'package:get/get.dart';
import 'package:flutter/material.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class AnimationService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final animations = <String, AnimationController>{}.obs;
  final animationConfigs = <String, Map<String, dynamic>>{}.obs;
  final isAnimating = false.obs;

  // 注册动画
  Future<void> registerAnimation(
    String name,
    AnimationController controller, [
    Map<String, dynamic>? config,
  ]) async {
    try {
      animations[name] = controller;
      if (config != null) {
        animationConfigs[name] = config;
        await _saveAnimationConfigs();
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to register animation', data: {'name': name, 'error': e.toString()});
      rethrow;
    }
  }

  // 播放动画
  Future<void> playAnimation(String name, {bool reverse = false}) async {
    if (isAnimating.value) return;

    try {
      isAnimating.value = true;
      final controller = animations[name];
      if (controller == null) {
        throw Exception('Animation not found: $name');
      }

      if (reverse) {
        await controller.reverse();
      } else {
        await controller.forward();
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to play animation', data: {'name': name, 'error': e.toString()});
      rethrow;
    } finally {
      isAnimating.value = false;
    }
  }

  // 停止动画
  void stopAnimation(String name) {
    try {
      final controller = animations[name];
      if (controller != null) {
        controller.stop();
      }
    } catch (e) {
      _loggingService.log('error', 'Failed to stop animation', data: {'name': name, 'error': e.toString()});
    }
  }

  // 重置动画
  void resetAnimation(String name) {
    try {
      final controller = animations[name];
      if (controller != null) {
        controller.reset();
      }
    } catch (e) {
      _loggingService.log('error', 'Failed to reset animation', data: {'name': name, 'error': e.toString()});
    }
  }

  // 更新动画配置
  Future<void> updateAnimationConfig(String name, Map<String, dynamic> config) async {
    try {
      if (!animations.containsKey(name)) {
        throw Exception('Animation not found: $name');
      }

      animationConfigs[name] = config;
      await _saveAnimationConfigs();
      
      // 如果动画正在播放,重新应用配置
      if (animations[name]!.isAnimating) {
        await _applyAnimationConfig(name);
      }
    } catch (e) {
      await _loggingService.log('error', 'Failed to update animation config', data: {'name': name, 'error': e.toString()});
      rethrow;
    }
  }

  // 获取动画配置
  Map<String, dynamic>? getAnimationConfig(String name) {
    try {
      return animationConfigs[name];
    } catch (e) {
      _loggingService.log('error', 'Failed to get animation config', data: {'name': name, 'error': e.toString()});
      return null;
    }
  }

  @override
  void onClose() {
    // 释放所有动画控制器
    for (final controller in animations.values) {
      controller.dispose();
    }
    animations.clear();
    super.onClose();
  }

  Future<void> _saveAnimationConfigs() async {
    try {
      await _storageService.saveLocal('animation_configs', animationConfigs.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _applyAnimationConfig(String name) async {
    try {
      final config = animationConfigs[name];
      if (config == null) return;

      final controller = animations[name];
      if (controller == null) return;

      // 应用动画配置
      if (config['duration'] != null) {
        controller.duration = Duration(milliseconds: config['duration']);
      }
      if (config['reverseDuration'] != null) {
        controller.reverseDuration = Duration(milliseconds: config['reverseDuration']);
      }
      if (config['lowerBound'] != null) {
        controller.lowerBound = config['lowerBound'];
      }
      if (config['upperBound'] != null) {
        controller.upperBound = config['upperBound'];
      }
    } catch (e) {
      rethrow;
    }
  }
} 