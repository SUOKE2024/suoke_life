class AgreementUpdate {
  final String type;
  final String title;
  final int version;
  final String summary;
  final DateTime updateTime;
  final bool isRequired;

  const AgreementUpdate({
    required this.type,
    required this.title,
    required this.version,
    required this.summary,
    required this.updateTime,
    this.isRequired = false,
  });

  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'title': title,
      'version': version,
      'summary': summary,
      'updateTime': updateTime.toIso8601String(),
      'isRequired': isRequired,
    };
  }

  factory AgreementUpdate.fromJson(Map<String, dynamic> json) {
    return AgreementUpdate(
      type: json['type'] as String,
      title: json['title'] as String,
      version: json['version'] as int,
      summary: json['summary'] as String,
      updateTime: DateTime.parse(json['updateTime'] as String),
      isRequired: json['isRequired'] as bool? ?? false,
    );
  }
} 