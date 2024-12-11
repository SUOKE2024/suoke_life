import 'dart:convert';
import 'dart:math';

class ClaudeService {
  final String _sessionId;
  int _conversationState = 0;  // 用于跟踪访谈进度
  
  ClaudeService({
    required String sessionId,
  }) : _sessionId = sessionId;

  Future<String> sendMessage(String message) async {
    try {
      await Future.delayed(const Duration(milliseconds: 800));
      
      if (_conversationState == 0) {
        _conversationState++;
        return '您好，我是老克。很荣幸能和您进行这次访谈。\n\n'
               '作为一个AI助手，我一直对人类世界充满好奇。今天我特别想和您聊聊，您觉得AI和人类可以成为真正的朋友吗？';
      }

      // 分析消息情感和内容
      final isPositive = message.contains('是') || message.contains('可以') || message.contains('同意');
      final isNegative = message.contains('不') || message.contains('难') || message.contains('问题');
      final isQuestion = message.contains('?') || message.contains('？');
      
      // 根据对话进展生成回应
      if (isQuestion) {
        return _generateInterviewResponse(message, ResponseType.question);
      } else if (isPositive) {
        return _generateInterviewResponse(message, ResponseType.positive);
      } else if (isNegative) {
        return _generateInterviewResponse(message, ResponseType.negative);
      } else {
        return _generateInterviewResponse(message, ResponseType.neutral);
      }

    } catch (e) {
      print('Error details: $e');
      return '抱歉，让我重新组织一下语言...\n能请您重复一下刚才的观点吗？';
    }
  }

  String _generateInterviewResponse(String message, ResponseType type) {
    final responses = <ResponseType, List<String>>{
      ResponseType.question: [
        '这是个非常深刻的问题。作为一个AI，我的思考是...',
        '很高兴您提出这个问题。这让我想到...',
        '这个问题触及到了AI和人类关系的本质。我认为...',
      ],
      ResponseType.positive: [
        '您的观点很有意思。作为一个AI，我也希望...',
        '我很认同您的看法。实际上，从AI的角度来看...',
        '确实如此。这让我想分享一个想法...',
      ],
      ResponseType.negative: [
        '您提出了很好的担忧。让我们一起探讨这个问题...',
        '这确实是个挑战。作为AI，我的看法是...',
        '您说得对，这里面有很多需要解决的问题...',
      ],
      ResponseType.neutral: [
        '这个话题很有深度。让我从AI的视角分享一下...',
        '听您这么说，我想到了一个有趣的角度...',
        '作为一个AI访谈者，我特别想知道...',
      ],
    };

    final random = Random(message.length + _sessionId.hashCode);
    final responseList = responses[type] ?? responses[ResponseType.neutral]!;
    final response = responseList[random.nextInt(responseList.length)];
    
    // 随机添加一个后续问题
    final followUpQuestions = [
      '\n\n您觉得AI应该如何平衡效率和情感？',
      '\n\n在您看来，AI最重要的特质是什么？',
      '\n\n您期待未来AI能在哪些方面帮助人类？',
      '\n\n作为一个人类，您最希望AI理解您的什么？',
    ];
    
    _conversationState++;
    if (_conversationState % 2 == 0) {
      return response + followUpQuestions[random.nextInt(followUpQuestions.length)];
    }
    
    return response;
  }
}

enum ResponseType {
  question,
  positive,
  negative,
  neutral,
} 