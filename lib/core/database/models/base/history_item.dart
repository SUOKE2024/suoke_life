class HistoryItem {
  final String id;
  final String title;
  final String type;
  final String time;
  final String? lastMessage;
  final String? status;
  final String? imageUrl;
  final IconData? icon;

  HistoryItem({
    required this.id,
    required this.title,
    required this.type,
    required this.time,
    this.lastMessage,
    this.status,
    this.imageUrl,
    this.icon,
  });

  factory HistoryItem.fromMap(Map<String, dynamic> map) {
    return HistoryItem(
      id: map['id'] as String,
      title: map['title'] as String,
      type: map['type'] as String,
      time: map['time'] as String,
      lastMessage: map['last_message'] as String?,
      status: map['status'] as String?,
      imageUrl: map['image_url'] as String?,
      icon: map['icon'] as IconData?,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'type': type,
      'time': time,
      'last_message': lastMessage,
      'status': status,
      'image_url': imageUrl,
      'icon': icon,
    };
  }
} 