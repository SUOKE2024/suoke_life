import 'package:flutter/material.dart';

class Record {
  final String id;
  final String title;
  final String content;
  final RecordType type;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final List<String> tags;
  final List<String>? attachments;

  const Record({
    required this.id,
    required this.title,
    required this.content,
    required this.type,
    required this.createdAt,
    this.updatedAt,
    this.tags = const [],
    this.attachments,
  });

  Record copyWith({
    String? title,
    String? content,
    RecordType? type,
    List<String>? tags,
    List<String>? attachments,
  }) {
    return Record(
      id: id,
      title: title ?? this.title,
      content: content ?? this.content,
      type: type ?? this.type,
      createdAt: createdAt,
      updatedAt: DateTime.now(),
      tags: tags ?? this.tags,
      attachments: attachments ?? this.attachments,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'type': type.name,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
      'tags': tags,
      'attachments': attachments,
    };
  }

  factory Record.fromJson(Map<String, dynamic> json) {
    return Record(
      id: json['id'],
      title: json['title'],
      content: json['content'],
      type: RecordType.values.byName(json['type']),
      createdAt: DateTime.parse(json['createdAt']),
      updatedAt: json['updatedAt'] != null 
          ? DateTime.parse(json['updatedAt']) 
          : null,
      tags: List<String>.from(json['tags'] ?? []),
      attachments: json['attachments'] != null 
          ? List<String>.from(json['attachments'])
          : null,
    );
  }
}

enum RecordType {
  note(
    name: '笔记',
    icon: Icons.note,
    color: Colors.blue,
  ),
  task(
    name: '任务',
    icon: Icons.task,
    color: Colors.orange,
  ),
  diary(
    name: '日记',
    icon: Icons.book,
    color: Colors.green,
  ),
  health(
    name: '健康',
    icon: Icons.favorite,
    color: Colors.red,
  );

  final String name;
  final IconData icon;
  final Color color;

  const RecordType({
    required this.name,
    required this.icon,
    required this.color,
  });
}

extension DateTimeFormat on DateTime {
  String format() {
    final now = DateTime.now();
    final difference = now.difference(this);

    if (difference.inDays > 0) {
      return '${difference.inDays}天前';
    } else if (difference.inHours > 0) {
      return '${difference.inHours}小时前';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes}分钟前';
    } else {
      return '刚刚';
    }
  }
} 