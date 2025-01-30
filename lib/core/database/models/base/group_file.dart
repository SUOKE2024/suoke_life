class GroupFile {
  final String id;
  final String name;
  final String type;
  final int size;
  final String url;
  final String uploaderId;
  final String uploaderName;
  final DateTime uploadTime;
  final int downloadCount;
  final String? thumbnail;
  final Map<String, dynamic>? metadata;

  const GroupFile({
    required this.id,
    required this.name,
    required this.type,
    required this.size,
    required this.url,
    required this.uploaderId,
    required this.uploaderName,
    required this.uploadTime,
    this.downloadCount = 0,
    this.thumbnail,
    this.metadata,
  });

  String get extension => name.split('.').last.toLowerCase();

  bool get isImage => type == 'image';
  bool get isVideo => type == 'video';
  bool get isAudio => type == 'audio';
  bool get isDocument => type == 'document';

  factory GroupFile.fromJson(Map<String, dynamic> json) => GroupFile(
    id: json['id'],
    name: json['name'],
    type: json['type'],
    size: json['size'],
    url: json['url'],
    uploaderId: json['uploaderId'],
    uploaderName: json['uploaderName'],
    uploadTime: DateTime.parse(json['uploadTime']),
    downloadCount: json['downloadCount'] ?? 0,
    thumbnail: json['thumbnail'],
    metadata: json['metadata'],
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'type': type,
    'size': size,
    'url': url,
    'uploaderId': uploaderId,
    'uploaderName': uploaderName,
    'uploadTime': uploadTime.toIso8601String(),
    'downloadCount': downloadCount,
    'thumbnail': thumbnail,
    'metadata': metadata,
  };
} 