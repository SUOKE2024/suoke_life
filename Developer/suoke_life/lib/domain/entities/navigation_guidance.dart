class NavigationGuidance {
  final String? environmentType;
  final List<String> objects;
  final List<String> tcmElements;
  final String? recommendation;
  final List<NavigationStep>? steps;
  final List<PointOfInterest>? pointsOfInterest;
  
  NavigationGuidance({
    this.environmentType,
    this.objects = const [],
    this.tcmElements = const [],
    this.recommendation,
    this.steps,
    this.pointsOfInterest,
  });
}

class NavigationStep {
  final String instruction;
  final List<String> landmarks;
  final List<String> hazards;
  final String? turnDirection;
  
  NavigationStep({
    required this.instruction,
    this.landmarks = const [],
    this.hazards = const [],
    this.turnDirection,
  });
}

class PointOfInterest {
  final String name;
  final String distance;
  final String category;
  final String? description;
  
  PointOfInterest({
    required this.name,
    required this.distance,
    required this.category,
    this.description,
  });
} 