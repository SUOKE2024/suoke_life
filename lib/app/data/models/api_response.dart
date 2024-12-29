class ApiResponse<T> {
  final bool success;
  final String? message;
  final T? data;
  final Map<String, dynamic>? metadata;

  ApiResponse({
    required this.success,
    this.message,
    this.data,
    this.metadata,
  });

  factory ApiResponse.fromMap(Map<String, dynamic> map, T Function(Map<String, dynamic>) fromMap) => ApiResponse(
    success: map['success'] ?? false,
    message: map['message'],
    data: map['data'] != null ? fromMap(map['data']) : null,
    metadata: map['metadata'],
  );

  factory ApiResponse.success(T data, {String? message, Map<String, dynamic>? metadata}) => ApiResponse(
    success: true,
    message: message,
    data: data,
    metadata: metadata,
  );

  factory ApiResponse.error(String message, {Map<String, dynamic>? metadata}) => ApiResponse(
    success: false,
    message: message,
    metadata: metadata,
  );
} 