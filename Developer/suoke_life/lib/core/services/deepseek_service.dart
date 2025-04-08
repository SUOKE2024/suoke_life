import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/config/env_config.dart';

/// DeepSeek服务提供者
final deepseekServiceProvider = Provider<DeepSeekService>((ref) {
  return DeepSeekService();
});

/// DeepSeek模型类型
enum DeepSeekModelType {
  /// 纯文本模型
  chatV2("deepseek-chat"),

  /// 多模态模型
  vision("deepseek-vision"),

  /// 编码模型
  coder("deepseek-coder");

  final String value;

  const DeepSeekModelType(this.value);
}

/// 消息角色
enum MessageRole {
  user("user"),
  assistant("assistant"),
  system("system");

  final String value;

  const MessageRole(this.value);
}

/// 消息内容类型
enum ContentType {
  text("text"),
  imageUrl("image_url");

  final String value;

  const ContentType(this.value);
}

/// 消息内容
class MessageContent {
  final ContentType type;
  final String content;
  final String? imageUrl;
  final String? imageBase64;

  MessageContent.text(this.content)
      : type = ContentType.text,
        imageUrl = null,
        imageBase64 = null;

  MessageContent.imageUrl(this.imageUrl)
      : type = ContentType.imageUrl,
        content = "",
        imageBase64 = null;

  MessageContent.imageBase64(this.imageBase64)
      : type = ContentType.imageUrl,
        content = "",
        imageUrl = null;

  Map<String, dynamic> toJson() {
    if (type == ContentType.text) {
      return {
        'type': type.value,
        'text': content,
      };
    } else if (type == ContentType.imageUrl) {
      if (imageUrl != null) {
        return {
          'type': type.value,
          'image_url': {'url': imageUrl},
        };
      } else if (imageBase64 != null) {
        return {
          'type': type.value,
          'image_url': {
            'url': 'data:image/jpeg;base64,$imageBase64',
          },
        };
      }
    }
    // 默认返回文本类型
    return {
      'type': ContentType.text.value,
      'text': "",
    };
  }
}

/// 聊天消息
class ChatMessage {
  final MessageRole role;
  final List<MessageContent> content;

  ChatMessage({
    required this.role,
    required this.content,
  });

  Map<String, dynamic> toJson() {
    return {
      'role': role.value,
      'content': content.length == 1 && content.first.type == ContentType.text
          ? content.first.content
          : content.map((c) => c.toJson()).toList(),
    };
  }

  /// 创建用户文本消息
  static ChatMessage userText(String text) {
    return ChatMessage(
      role: MessageRole.user,
      content: [MessageContent.text(text)],
    );
  }

  /// 创建用户图片消息
  static ChatMessage userImage(String imageUrl, {String? caption}) {
    final contents = <MessageContent>[
      MessageContent.imageUrl(imageUrl),
    ];

    if (caption != null && caption.isNotEmpty) {
      contents.add(MessageContent.text(caption));
    }

    return ChatMessage(
      role: MessageRole.user,
      content: contents,
    );
  }

  /// 创建用户图片消息（Base64编码）
  static ChatMessage userImageBase64(String base64Image, {String? caption}) {
    final contents = <MessageContent>[
      MessageContent.imageBase64(base64Image),
    ];

    if (caption != null && caption.isNotEmpty) {
      contents.add(MessageContent.text(caption));
    }

    return ChatMessage(
      role: MessageRole.user,
      content: contents,
    );
  }

  /// 创建系统消息
  static ChatMessage system(String text) {
    return ChatMessage(
      role: MessageRole.system,
      content: [MessageContent.text(text)],
    );
  }

  /// 创建助手消息
  static ChatMessage assistant(String text) {
    return ChatMessage(
      role: MessageRole.assistant,
      content: [MessageContent.text(text)],
    );
  }
}

/// DeepSeek API 服务
class DeepSeekService {
  late final Dio _dio;
  late final String _apiKey;

  DeepSeekService() {
    _dio = Dio(BaseOptions(
      baseUrl: EnvConfig().deepseekApiUrl,
      headers: {
        'Content-Type': 'application/json',
      },
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
    ));

    _apiKey = EnvConfig().deepseekApiKey;

    // 添加请求拦截器
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        options.headers['Authorization'] = 'Bearer $_apiKey';
        return handler.next(options);
      },
      onError: (error, handler) {
        debugPrint('DeepSeek API 错误: ${error.message}');
        return handler.next(error);
      },
    ));
  }

  /// 发送聊天请求
  Future<String> chat({
    required List<ChatMessage> messages,
    DeepSeekModelType model = DeepSeekModelType.chatV2,
    double temperature = 0.7,
    int maxTokens = 2000,
  }) async {
    try {
      final response = await _dio.post(
        '/chat/completions',
        data: {
          'model': model.value,
          'messages': messages.map((m) => m.toJson()).toList(),
          'temperature': temperature,
          'max_tokens': maxTokens,
        },
      );

      final data = response.data;
      final content = data['choices'][0]['message']['content'];
      return content;
    } catch (e) {
      debugPrint('DeepSeek聊天请求失败: $e');
      if (e is DioException) {
        debugPrint('DeepSeek API响应: ${e.response?.data}');
      }
      return '抱歉，我遇到了一些问题，无法正常回应。请稍后再试。';
    }
  }

  /// 发送多模态聊天请求
  Future<String> multimodalChat({
    required List<ChatMessage> messages,
    double temperature = 0.7,
    int maxTokens = 2000,
  }) async {
    // 使用 vision 模型
    return chat(
      messages: messages,
      model: DeepSeekModelType.vision,
      temperature: temperature,
      maxTokens: maxTokens,
    );
  }

  /// 将图片转换为Base64编码
  static Future<String> imageToBase64(File imageFile) async {
    final bytes = await imageFile.readAsBytes();
    return base64Encode(bytes);
  }
}
