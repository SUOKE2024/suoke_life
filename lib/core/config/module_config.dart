class ModuleConfig {
  final String name;
  final String version;
  final Map<String, dynamic> settings;
  final List<String> dependencies;

  const ModuleConfig({
    required this.name,
    required this.version,
    this.settings = const {},
    this.dependencies = const [],
  });

  factory ModuleConfig.fromJson(Map<String, dynamic> json) {
    return ModuleConfig(
      name: json['name'] as String,
      version: json['version'] as String,
      settings: json['settings'] as Map<String, dynamic>? ?? {},
      dependencies: (json['dependencies'] as List?)
          ?.map((e) => e as String)
          .toList() ?? [],
    );
  }
} 