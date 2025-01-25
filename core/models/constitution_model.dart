enum ConstitutionType {
  peace, // 平和质
  qiDeficiency, // 气虚质
  yangDeficiency, // 阳虚质
  yinDeficiency, // 阴虚质
  phlegmDampness, // 痰湿质
  dampHeat, // 湿热质
  bloodStasis, // 血瘀质
  qiStagnation, // 气郁质
  special, // 特禀质
}

class ConstitutionAnalysis {
  final ConstitutionType constitutionType;
  final String description;
  final String healthAdvice;
  final Map<String, double> scores;
  final TongueAnalysis? tongueAnalysis;
  final List<HealthData>? healthHistory;
  final GeneticProfile? geneticProfile;
  final String? comprehensiveAdvice;

  ConstitutionAnalysis({
    required this.constitutionType,
    required this.description,
    required this.healthAdvice,
    required this.scores,
    this.tongueAnalysis,
    this.healthHistory,
    this.geneticProfile,
    this.comprehensiveAdvice,
  });

  factory ConstitutionAnalysis.fromJson(Map<String, dynamic> json) {
    return ConstitutionAnalysis(
      constitutionType: ConstitutionType.values.firstWhere(
        (e) => e.toString() == 'ConstitutionType.${json['constitutionType']}',
      ),
      description: json['description'],
      healthAdvice: json['healthAdvice'],
      scores: Map<String, double>.from(json['scores']),
      tongueAnalysis: json['tongueAnalysis'] != null 
          ? TongueAnalysis.fromJson(json['tongueAnalysis']) 
          : null,
      healthHistory: json['healthHistory'] != null
          ? (json['healthHistory'] as List)
              .map((e) => HealthData.fromJson(e))
              .toList()
          : null,
      geneticProfile: json['geneticData'] != null
          ? GeneticProfile.fromJson(json['geneticData'])
          : null,
      comprehensiveAdvice: json['comprehensiveAdvice'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'constitutionType': constitutionType.toString().split('.').last,
      'description': description,
      'healthAdvice': healthAdvice,
      'scores': scores,
      'tongueAnalysis': tongueAnalysis?.toJson(),
      'healthHistory': healthHistory?.map((e) => e.toJson()).toList(),
      'geneticData': geneticProfile?.toJson(),
      'comprehensiveAdvice': comprehensiveAdvice,
    };
  }
}

class TongueAnalysis {
  final String tongueType;
  final Map<String, double> featureScores;
  final String imagePath;

  TongueAnalysis({
    required this.tongueType,
    required this.featureScores,
    required this.imagePath,
  });

  factory TongueAnalysis.fromJson(Map<String, dynamic> json) {
    return TongueAnalysis(
      tongueType: json['tongueType'],
      featureScores: Map<String, double>.from(json['featureScores']),
      imagePath: json['imagePath'],
    );
  }

  Map<String, dynamic> toJson() => {
    'tongueType': tongueType,
    'featureScores': featureScores,
    'imagePath': imagePath,
  };
}

class GeneticProfile {
  final Map<String, double> riskFactors;
  final List<String> metabolicMarkers;

  GeneticProfile({
    required this.riskFactors,
    required this.metabolicMarkers,
  });

  factory GeneticProfile.fromJson(Map<String, dynamic> json) {
    return GeneticProfile(
      riskFactors: Map<String, double>.from(json['riskFactors']),
      metabolicMarkers: List<String>.from(json['metabolicMarkers']),
    );
  }

  Map<String, dynamic> toJson() => {
    'riskFactors': riskFactors,
    'metabolicMarkers': metabolicMarkers,
  };
}
