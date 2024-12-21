class ConfigMode {
  final bool encrypted;
  final bool cached;
  final bool syncEnabled;
  final Duration updateInterval;

  const ConfigMode({
    required this.encrypted,
    required this.cached,
    required this.syncEnabled,
    required this.updateInterval,
  });
} 