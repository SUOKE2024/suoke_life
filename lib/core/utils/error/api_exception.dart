class ApiException implements Exception {
  final String message;
  final dynamic data;

  ApiException(this.message, [this.data]);

  @override
  String toString() => 'ApiException: $message';
} 