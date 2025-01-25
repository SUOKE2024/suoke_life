import 'package:core/core.dart';

abstract class ContentModerationService {
  /// 审核内容
  /// [content] 需要审核的内容
  Future<List<dynamic>> moderateContent(List<dynamic> content);
}

class ContentModerationServiceImpl implements ContentModerationService {
  final AIService _aiService;

  ContentModerationServiceImpl(this._aiService);

  @override
  Future<List<dynamic>> moderateContent(List<dynamic> content) async {
    try {
      // 使用AI服务进行内容审核
      final result = await _aiService.moderate(content);
      
      // 过滤掉未通过审核的内容
      return result.where((item) => item['approved'] == true).toList();
    } catch (e) {
      throw ContentModerationException('Failed to moderate content: $e');
    }
  }
}

class ContentModerationException implements Exception {
  final String message;

  ContentModerationException(this.message);

  @override
  String toString() => 'ContentModerationException: $message';
}
