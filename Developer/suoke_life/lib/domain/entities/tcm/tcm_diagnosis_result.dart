class TcmDiagnosisResult {
  final String id;
  final String mainSyndrome;
  final String constitution;
  final String? description;
  final String? constitutionDescription;
  final List<String> herbs;
  final List<String> formulas;
  final String? tongueDetails;
  final String? faceDetails;
  final String? pulseDetails;
  final String? audioDetails;
  final String? lifestyle;
  final String? diet;
  final double? confidenceScore;
  final String timestamp;

  const TcmDiagnosisResult({
    required this.id,
    required this.mainSyndrome,
    required this.constitution,
    this.description,
    this.constitutionDescription,
    this.herbs = const [],
    this.formulas = const [],
    this.tongueDetails,
    this.faceDetails,
    this.pulseDetails,
    this.audioDetails,
    this.lifestyle,
    this.diet,
    this.confidenceScore,
    required this.timestamp,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'mainSyndrome': mainSyndrome,
      'constitution': constitution,
      'description': description,
      'constitutionDescription': constitutionDescription,
      'herbs': herbs,
      'formulas': formulas,
      'tongueDetails': tongueDetails,
      'faceDetails': faceDetails,
      'pulseDetails': pulseDetails,
      'audioDetails': audioDetails,
      'lifestyle': lifestyle,
      'diet': diet,
      'confidenceScore': confidenceScore,
      'timestamp': timestamp,
    };
  }

  factory TcmDiagnosisResult.fromJson(Map<String, dynamic> json) {
    return TcmDiagnosisResult(
      id: json['id'] ?? '',
      mainSyndrome: json['mainSyndrome'] ?? '',
      constitution: json['constitution'] ?? '',
      description: json['description'],
      constitutionDescription: json['constitutionDescription'],
      herbs: (json['herbs'] as List<dynamic>?)?.map((e) => e as String).toList() ?? [],
      formulas: (json['formulas'] as List<dynamic>?)?.map((e) => e as String).toList() ?? [],
      tongueDetails: json['tongueDetails'],
      faceDetails: json['faceDetails'],
      pulseDetails: json['pulseDetails'],
      audioDetails: json['audioDetails'],
      lifestyle: json['lifestyle'],
      diet: json['diet'],
      confidenceScore: json['confidenceScore'],
      timestamp: json['timestamp'] ?? DateTime.now().toIso8601String(),
    );
  }

  TcmDiagnosisResult copyWith({
    String? id,
    String? mainSyndrome,
    String? constitution,
    String? description,
    String? constitutionDescription,
    List<String>? herbs,
    List<String>? formulas,
    String? tongueDetails,
    String? faceDetails,
    String? pulseDetails,
    String? audioDetails,
    String? lifestyle,
    String? diet,
    double? confidenceScore,
    String? timestamp,
  }) {
    return TcmDiagnosisResult(
      id: id ?? this.id,
      mainSyndrome: mainSyndrome ?? this.mainSyndrome,
      constitution: constitution ?? this.constitution,
      description: description ?? this.description,
      constitutionDescription: constitutionDescription ?? this.constitutionDescription,
      herbs: herbs ?? this.herbs,
      formulas: formulas ?? this.formulas,
      tongueDetails: tongueDetails ?? this.tongueDetails,
      faceDetails: faceDetails ?? this.faceDetails,
      pulseDetails: pulseDetails ?? this.pulseDetails,
      audioDetails: audioDetails ?? this.audioDetails,
      lifestyle: lifestyle ?? this.lifestyle,
      diet: diet ?? this.diet,
      confidenceScore: confidenceScore ?? this.confidenceScore,
      timestamp: timestamp ?? this.timestamp,
    );
  }
}