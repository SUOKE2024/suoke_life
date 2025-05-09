import 'package:flutter/material.dart';
import 'package:suoke_life/domain/models/agent_model.dart';

/// 消息气泡组件
class MessageBubble extends StatelessWidget {
  /// 消息数据
  final AgentMessage message;
  
  /// 发送者头像URL（用户或智能体）
  final String senderAvatarUrl;
  
  /// 是否是用户发送的消息
  final bool isUserMessage;
  
  /// 智能体主题色
  final Color? agentThemeColor;

  /// 构造函数
  const MessageBubble({
    Key? key,
    required this.message,
    required this.senderAvatarUrl,
    required this.isUserMessage,
    this.agentThemeColor,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // 根据消息类型选择不同的布局
    if (message.messageType == MessageType.system) {
      return _buildSystemMessage(context);
    } else {
      return _buildUserOrAgentMessage(context);
    }
  }

  /// 构建系统消息
  Widget _buildSystemMessage(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: Center(
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surfaceVariant,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Text(
            message.content,
            style: TextStyle(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
              fontSize: 14,
            ),
            textAlign: TextAlign.center,
          ),
        ),
      ),
    );
  }

  /// 构建用户或智能体消息
  Widget _buildUserOrAgentMessage(BuildContext context) {
    final messageTime = _formatTime(message.createdAt);
    
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: Row(
        mainAxisAlignment: isUserMessage ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUserMessage) _buildAvatar(),
          const SizedBox(width: 8),
          Flexible(
            child: Column(
              crossAxisAlignment: isUserMessage ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: _getBubbleColor(context),
                    borderRadius: BorderRadius.circular(16).copyWith(
                      bottomLeft: isUserMessage ? const Radius.circular(16) : const Radius.circular(0),
                      bottomRight: !isUserMessage ? const Radius.circular(16) : const Radius.circular(0),
                    ),
                  ),
                  child: _buildMessageContent(context),
                ),
                const SizedBox(height: 4),
                Text(
                  messageTime,
                  style: TextStyle(
                    fontSize: 12,
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          if (isUserMessage) _buildAvatar(),
        ],
      ),
    );
  }

  /// 构建头像
  Widget _buildAvatar() {
    return CircleAvatar(
      radius: 18,
      backgroundImage: AssetImage(senderAvatarUrl),
    );
  }

  /// 构建消息内容
  Widget _buildMessageContent(BuildContext context) {
    switch (message.contentType) {
      case ContentType.text:
        return Text(
          message.content,
          style: TextStyle(
            color: _getTextColor(context),
            fontSize: 16,
          ),
        );
      
      case ContentType.image:
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(
                message.content,
                fit: BoxFit.cover,
                width: 200,
                loadingBuilder: (context, child, loadingProgress) {
                  if (loadingProgress == null) return child;
                  return Center(
                    child: CircularProgressIndicator(
                      value: loadingProgress.expectedTotalBytes != null
                          ? loadingProgress.cumulativeBytesLoaded / loadingProgress.expectedTotalBytes!
                          : null,
                    ),
                  );
                },
                errorBuilder: (context, error, stackTrace) {
                  return Container(
                    width: 200,
                    height: 150,
                    color: Colors.grey[300],
                    child: const Icon(Icons.error),
                  );
                },
              ),
            ),
            if (message.extraData != null && message.extraData!.containsKey('caption'))
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  message.extraData!['caption'],
                  style: TextStyle(
                    color: _getTextColor(context),
                    fontSize: 14,
                  ),
                ),
              ),
          ],
        );
      
      case ContentType.voice:
        // 简单的语音消息UI
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.play_circle_fill,
              color: _getTextColor(context),
            ),
            const SizedBox(width: 8),
            Container(
              width: 150,
              height: 30,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(4),
                color: _getTextColor(context).withOpacity(0.1),
              ),
              child: Center(
                child: Text(
                  '语音消息 ${message.extraData?['duration'] ?? '0:00'}',
                  style: TextStyle(
                    color: _getTextColor(context),
                    fontSize: 14,
                  ),
                ),
              ),
            ),
          ],
        );
      
      case ContentType.diagnosis:
        // 简单的诊断结果UI
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '诊断结果',
              style: TextStyle(
                color: _getTextColor(context),
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              message.content,
              style: TextStyle(
                color: _getTextColor(context),
                fontSize: 16,
              ),
            ),
          ],
        );
    }
  }

  /// 获取气泡颜色
  Color _getBubbleColor(BuildContext context) {
    if (isUserMessage) {
      return Theme.of(context).colorScheme.primary;
    } else if (message.messageType == MessageType.agent && agentThemeColor != null) {
      return agentThemeColor!.withOpacity(0.2);
    } else {
      return Theme.of(context).colorScheme.surfaceVariant;
    }
  }

  /// 获取文字颜色
  Color _getTextColor(BuildContext context) {
    if (isUserMessage) {
      return Theme.of(context).colorScheme.onPrimary;
    } else if (message.messageType == MessageType.agent && agentThemeColor != null) {
      return agentThemeColor!;
    } else {
      return Theme.of(context).colorScheme.onSurfaceVariant;
    }
  }

  /// 格式化时间
  String _formatTime(DateTime dateTime) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final messageDate = DateTime(dateTime.year, dateTime.month, dateTime.day);
    
    String timeStr = '${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    
    if (messageDate == today) {
      return timeStr;
    } else if (messageDate == today.subtract(const Duration(days: 1))) {
      return '昨天 $timeStr';
    } else {
      return '${dateTime.month}月${dateTime.day}日 $timeStr';
    }
  }
} 