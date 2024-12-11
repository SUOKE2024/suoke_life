/// Service that handles message processing and formatting.
/// 
/// Features:
/// - Message formatting
/// - Content validation
/// - Attachment handling
class MessageService extends BaseService {
  final _attachmentTypes = <String>{'image', 'video', 'file'};
  final _maxContentLength = 5000;
  final _maxAttachmentSize = 10 * 1024 * 1024; // 10MB

  @override
  List<Type> get dependencies => [
    StorageService,
    NetworkService,
  ];

  @override
  Future<void> initialize() async {
    // Initialize message handlers
  }

  Future<String> formatMessage(String content) async {
    // Apply formatting rules
    content = content.trim();
    content = _sanitizeContent(content);
    content = await _processMarkdown(content);
    return content;
  }

  Future<bool> validateMessage(String content) async {
    if (content.isEmpty) {
      throw ValidationError('Message cannot be empty');
    }

    if (content.length > _maxContentLength) {
      throw ValidationError('Message too long');
    }

    return true;
  }

  Future<List<Attachment>> processAttachments(List<File> files) async {
    final attachments = <Attachment>[];

    for (final file in files) {
      // Validate file
      await _validateFile(file);

      // Process file
      final attachment = await _processFile(file);
      attachments.add(attachment);
    }

    return attachments;
  }

  String _sanitizeContent(String content) {
    // Remove dangerous content
    return content.replaceAll(RegExp(r'<[^>]*>'), '');
  }

  Future<String> _processMarkdown(String content) async {
    // Process markdown syntax
    return content;
  }

  Future<void> _validateFile(File file) async {
    final size = await file.length();
    if (size > _maxAttachmentSize) {
      throw ValidationError('File too large');
    }

    final type = _getFileType(file.path);
    if (!_attachmentTypes.contains(type)) {
      throw ValidationError('Unsupported file type');
    }
  }

  Future<Attachment> _processFile(File file) async {
    final type = _getFileType(file.path);
    final name = path.basename(file.path);
    final size = await file.length();

    return Attachment(
      id: const Uuid().v4(),
      name: name,
      type: type,
      size: size,
      url: await _uploadFile(file),
    );
  }

  String _getFileType(String path) {
    final extension = path.split('.').last.toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif'].contains(extension)) {
      return 'image';
    } else if (['mp4', 'mov', 'avi'].contains(extension)) {
      return 'video';
    }
    return 'file';
  }

  Future<String> _uploadFile(File file) async {
    final network = DependencyManager.instance.get<NetworkService>();
    final response = await network.uploadFile(
      '/api/attachments',
      file,
    );
    return response.data['url'] as String;
  }

  @override
  Future<void> dispose() async {
    // Cleanup resources
  }
}

/// Attachment model for message files
class Attachment {
  final String id;
  final String name;
  final String type;
  final int size;
  final String url;

  Attachment({
    required this.id,
    required this.name,
    required this.type,
    required this.size,
    required this.url,
  });

  factory Attachment.fromJson(Map<String, dynamic> json) => Attachment(
    id: json['id'] as String,
    name: json['name'] as String,
    type: json['type'] as String,
    size: json['size'] as int,
    url: json['url'] as String,
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'type': type,
    'size': size,
    'url': url,
  };
} 