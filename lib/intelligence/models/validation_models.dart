class ValidationRule {
  final String type;
  final bool required;
  final int? minLength;
  final int? maxLength;
  final List<String> patterns;
  final List<String>? whitelist;
  final List<String>? blacklist;
  final bool sanitize;
  final bool? contentSafety;
  final Map<String, dynamic>? options;

  const ValidationRule({
    required this.type,
    this.required = false,
    this.minLength,
    this.maxLength,
    this.patterns = const [],
    this.whitelist,
    this.blacklist,
    this.sanitize = false,
    this.contentSafety,
    this.options,
  });
}

class ValidationResult {
  final bool isValid;
  final List<String> errors;
  final String sanitizedData;

  const ValidationResult({
    required this.isValid,
    this.errors = const [],
    required this.sanitizedData,
  });

  Map<String, dynamic> toMap() => {
    'is_valid': isValid,
    'errors': errors,
    'sanitized_data': sanitizedData,
  };
} 