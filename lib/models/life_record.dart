class LifeRecord {
  final String id;
  final String content;
  final String time;
  final String? location;
  final List<String> images;

  LifeRecord({
    required this.id,
    required this.content, 
    required this.time,
    this.location,
    this.images = const [],
  });

  factory LifeRecord.fromMap(Map<String, dynamic> map) {
    return LifeRecord(
      id: map['id'],
      content: map['content'],
      time: map['time'],
      location: map['location'],
      images: map['images']?.split(',') ?? [],
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'content': content,
      'time': time,
      'location': location,
      'images': images.join(','),
    };
  }
} 