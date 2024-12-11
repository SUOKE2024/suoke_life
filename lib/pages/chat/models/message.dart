enum MessageType {
  text,
  voice,
  image,
  video,
  file,
}

class Message {
  final String id;
  final String content;
  final bool isUser;
  final MessageType type;
  final DateTime timestamp;
  final Duration? duration; // 语音消息的时长
  final String? fileName; // 文件名称

  Message({
    required this.id,
    required this.content,
    required this.isUser,
    required this.type,
    required this.timestamp,
    this.duration,
    this.fileName,
  });

  factory Message.text({
    required String content,
    required bool isUser,
  }) {
    return Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      isUser: isUser,
      type: MessageType.text,
      timestamp: DateTime.now(),
    );
  }

  factory Message.voice({
    required String audioUrl,
    required Duration duration,
    required bool isUser,
  }) {
    return Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: audioUrl,
      isUser: isUser,
      type: MessageType.voice,
      timestamp: DateTime.now(),
      duration: duration,
    );
  }

  factory Message.image({
    required String imageUrl,
    required bool isUser,
  }) {
    return Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: imageUrl,
      isUser: isUser,
      type: MessageType.image,
      timestamp: DateTime.now(),
    );
  }

  factory Message.video({
    required String videoUrl,
    required bool isUser,
  }) {
    return Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: videoUrl,
      isUser: isUser,
      type: MessageType.video,
      timestamp: DateTime.now(),
    );
  }

  factory Message.file({
    required String filePath,
    required String fileName,
    required bool isUser,
  }) {
    return Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: filePath,
      isUser: isUser,
      type: MessageType.file,
      timestamp: DateTime.now(),
      fileName: fileName,
    );
  }
} 