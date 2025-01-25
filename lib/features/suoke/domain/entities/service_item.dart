class ServiceItem {
  final String id;
  final String title;
  final String imagePath;
  final String routePath;
  final bool isVerified;

  const ServiceItem({
    required this.id,
    required this.title,
    required this.imagePath,
    required this.routePath,
    required this.isVerified,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ServiceItem &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;
}
