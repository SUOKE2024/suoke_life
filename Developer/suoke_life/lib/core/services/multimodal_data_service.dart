import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:suoke_life/core/services/deepseek_service.dart';
import 'package:suoke_life/core/config/app_config.dart';
import 'package:suoke_life/core/widgets/tcm/tongue/tongue_image_processor.dart';
import 'package:image/image.dart' as img;
import 'package:uuid/uuid.dart';

/// 多模态数据服务提供者
final multimodalDataServiceProvider = Provider<MultimodalDataService>((ref) {
  final deepseekService = ref.watch(deepseekServiceProvider);
  return MultimodalDataService(deepseekService);
});

/// 多模态数据类型
enum MultimodalDataType {
  /// 文本数据
  text,

  /// 图像数据
  image,

  /// 音频数据
  audio,

  /// 视频数据
  video,
}

/// 图像内容类型
enum ImageContentType {
  /// 未知类型
  unknown,

  /// 舌头图片
  tongue,

  /// 脸部图片
  face,

  /// 食物图片
  food,

  /// 药材图片
  herb,

  /// 脉象图片
  pulse,

  /// 一般图片
  general,
}

/// 多模态数据收集服务
class MultimodalDataService {
  final DeepSeekService _deepseekService;

  /// 存储收集的数据
  final Map<String, Map<String, dynamic>> _collectedData = {};

  /// 图片选择器
  final ImagePicker _imagePicker = ImagePicker();

  /// 舌诊图像处理器
  final TongueImageProcessor _tongueProcessor = TongueImageProcessor();

  MultimodalDataService(this._deepseekService);

  /// 收集文本数据
  Future<void> collectTextData(String sessionId, String text,
      {String? label}) async {
    final dataItem = {
      'type': MultimodalDataType.text.name,
      'content': text,
      'timestamp': DateTime.now().toIso8601String(),
      'label': label,
    };

    _addToCollection(sessionId, dataItem);
  }

  /// 收集图像数据
  Future<String?> collectImageData(String sessionId,
      {String? label, bool fromCamera = false}) async {
    try {
      final XFile? image = fromCamera
          ? await _imagePicker.pickImage(source: ImageSource.camera)
          : await _imagePicker.pickImage(source: ImageSource.gallery);

      if (image == null) return null;

      // 读取图像数据
      final bytes = await image.readAsBytes();
      final base64Image = base64Encode(bytes);

      // 保存图像到本地存储
      final localPath = await _saveImageLocally(image);

      // 识别图像内容类型
      final imageContentType = await _detectImageContentType(image.path);

      final dataItem = {
        'type': MultimodalDataType.image.name,
        'content': base64Image,
        'localPath': localPath,
        'timestamp': DateTime.now().toIso8601String(),
        'label': label,
        'contentType': imageContentType.name,
      };

      _addToCollection(sessionId, dataItem);

      return localPath;
    } catch (e) {
      debugPrint('收集图像数据失败: $e');
      return null;
    }
  }

  /// 收集音频数据
  Future<String?> collectAudioData(String sessionId, String audioPath,
      {String? label}) async {
    try {
      final file = File(audioPath);
      if (!await file.exists()) return null;

      final bytes = await file.readAsBytes();
      final base64Audio = base64Encode(bytes);

      final dataItem = {
        'type': MultimodalDataType.audio.name,
        'content': base64Audio,
        'localPath': audioPath,
        'timestamp': DateTime.now().toIso8601String(),
        'label': label,
      };

      _addToCollection(sessionId, dataItem);

      return audioPath;
    } catch (e) {
      debugPrint('收集音频数据失败: $e');
      return null;
    }
  }

  /// 将收集的图像或音频数据与文本一起发送到LLM
  Future<String> processWithLLM({
    required String sessionId,
    required String prompt,
    String? imagePath,
    String? systemMessage,
  }) async {
    try {
      final messages = <ChatMessage>[];

      // 添加系统消息
      if (systemMessage != null && systemMessage.isNotEmpty) {
        messages.add(ChatMessage.system(systemMessage));
      }

      // 如果有图像，添加图像消息
      if (imagePath != null) {
        if (kIsWeb) {
          // Web环境下处理
          messages.add(ChatMessage.userImage(imagePath, caption: prompt));
        } else {
          // 非Web环境，转换为Base64
          final imageFile = File(imagePath);
          if (await imageFile.exists()) {
            final base64Image = await DeepSeekService.imageToBase64(imageFile);
            messages
                .add(ChatMessage.userImageBase64(base64Image, caption: prompt));
          } else {
            // 如果图像不存在，只发送文本
            messages.add(ChatMessage.userText(prompt));
          }
        }
      } else {
        // 无图像，只发送文本
        messages.add(ChatMessage.userText(prompt));
      }

      // 使用多模态模型处理请求
      final response =
          await _deepseekService.multimodalChat(messages: messages);

      // 收集回复文本
      collectTextData(sessionId, response, label: 'ai_response');

      return response;
    } catch (e) {
      debugPrint('LLM处理失败: $e');
      return '抱歉，我无法处理您的请求，请稍后再试。';
    }
  }

  /// 获取会话数据
  Map<String, dynamic>? getSessionData(String sessionId) {
    return _collectedData[sessionId];
  }

  /// 获取所有会话数据
  Map<String, Map<String, dynamic>> getAllCollectedData() {
    return _collectedData;
  }

  /// 清除会话数据
  void clearSessionData(String sessionId) {
    _collectedData.remove(sessionId);
  }

  /// 清除所有收集的数据
  void clearAllCollectedData() {
    _collectedData.clear();
  }

  /// 将数据添加到收集中
  void _addToCollection(String sessionId, Map<String, dynamic> dataItem) {
    if (!_collectedData.containsKey(sessionId)) {
      _collectedData[sessionId] = {
        'id': sessionId,
        'startTime': DateTime.now().toIso8601String(),
        'items': <Map<String, dynamic>>[],
      };
    }

    final items =
        _collectedData[sessionId]!['items'] as List<Map<String, dynamic>>;
    items.add(dataItem);

    // 更新最后修改时间
    _collectedData[sessionId]!['lastModified'] =
        DateTime.now().toIso8601String();
  }

  /// 保存图像到本地存储
  Future<String> _saveImageLocally(XFile image) async {
    try {
      // 生成唯一文件名
      final uuid = const Uuid().v4();
      final extension = image.path.split('.').last;
      final filename = 'image_$uuid.$extension';

      if (kIsWeb) {
        // Web平台直接返回原始路径
        return image.path;
      } else {
        // 非Web平台，保存到应用文档目录
        final appDir = await getApplicationDocumentsDirectory();
        final imageDir = Directory('${appDir.path}/multimodal_data/images');

        // 确保目录存在
        if (!await imageDir.exists()) {
          await imageDir.create(recursive: true);
        }

        // 复制文件
        final newPath = '${imageDir.path}/$filename';
        final bytes = await image.readAsBytes();
        final file = File(newPath);
        await file.writeAsBytes(bytes);

        return newPath;
      }
    } catch (e) {
      debugPrint('保存图像失败: $e');
      return image.path; // 失败时返回原始路径
    }
  }

  /// 创建新的会话ID
  static String createSessionId() {
    return const Uuid().v4();
  }

  /// 识别图像内容类型
  Future<ImageContentType> _detectImageContentType(String imagePath) async {
    try {
      final bytes = await File(imagePath).readAsBytes();
      final image = img.decodeImage(bytes);

      if (image == null) return ImageContentType.unknown;

      // 判断是否为舌头图片
      final isTongue = await _detectTongueImage(image);
      if (isTongue) return ImageContentType.tongue;

      // 判断是否为脸部图片
      final isFace = await _detectFaceImage(image);
      if (isFace) return ImageContentType.face;

      // 判断是否为食物图片
      final isFood = await _detectFoodImage(image);
      if (isFood) return ImageContentType.food;

      // 判断是否为药材图片
      final isHerb = await _detectHerbImage(image);
      if (isHerb) return ImageContentType.herb;

      // 默认为一般图片
      return ImageContentType.general;
    } catch (e) {
      debugPrint('检测图像内容类型失败: $e');
      return ImageContentType.unknown;
    }
  }

  /// 判断是否为舌头图片
  Future<bool> _detectTongueImage(img.Image image) async {
    try {
      // 使用舌诊处理器进行初步检测
      final result = _tongueProcessor.detectTongueFromImage(image);
      return result > 0.6; // 置信度大于0.6认为是舌头图片
    } catch (e) {
      debugPrint('检测舌头图片失败: $e');
      return false;
    }
  }

  /// 判断是否为脸部图片
  Future<bool> _detectFaceImage(img.Image image) async {
    // TODO: 实现脸部检测
    // 简单实现：红色区域占比判断是否可能是脸部
    return false;
  }

  /// 判断是否为食物图片
  Future<bool> _detectFoodImage(img.Image image) async {
    // TODO: 实现食物检测
    return false;
  }

  /// 判断是否为药材图片
  Future<bool> _detectHerbImage(img.Image image) async {
    // TODO: 实现药材检测
    return false;
  }

  /// 获取指定会话中特定类型的最后一个数据项
  Map<String, dynamic>? getLastItemOfType(String sessionId, String type) {
    try {
      if (!_collectedData.containsKey(sessionId)) return null;

      final sessionData = _collectedData[sessionId]!;

      // 按时间戳降序排序
      final items = sessionData.values
          .where((item) => item['type'] == type)
          .toList()
        ..sort((a, b) =>
            (b['timestamp'] as String).compareTo(a['timestamp'] as String));

      return items.isNotEmpty ? items.first : null;
    } catch (e) {
      debugPrint('获取最后一个$type数据项失败: $e');
      return null;
    }
  }
}
