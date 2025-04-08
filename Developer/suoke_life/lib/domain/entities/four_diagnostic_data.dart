import 'dart:convert';

/// 四诊数据实体
///
/// 表示中医四诊（望诊、闻诊、问诊、切诊）合参的诊断数据
class FourDiagnosticData {
  /// 诊断ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 诊断时间
  final DateTime diagnosisTime;
  
  /// 望诊数据
  final InspectionData inspection;
  
  /// 闻诊数据
  final AuscultationData auscultation;
  
  /// 问诊数据
  final InquiryData inquiry;
  
  /// 切诊数据
  final PalpationData palpation;
  
  /// 诊断结论
  final String conclusion;
  
  /// 诊断医师ID
  final String? doctorId;
  
  /// 诊断医师姓名
  final String? doctorName;
  
  /// 创建四诊数据实体
  FourDiagnosticData({
    required this.id,
    required this.userId,
    required this.diagnosisTime,
    required this.inspection,
    required this.auscultation,
    required this.inquiry,
    required this.palpation,
    required this.conclusion,
    this.doctorId,
    this.doctorName,
  });
  
  /// 从JSON创建实例
  factory FourDiagnosticData.fromJson(Map<String, dynamic> json) {
    return FourDiagnosticData(
      id: json['id'] as String,
      userId: json['userId'] as String,
      diagnosisTime: DateTime.parse(json['diagnosisTime'] as String),
      inspection: InspectionData.fromJson(json['inspection'] as Map<String, dynamic>),
      auscultation: AuscultationData.fromJson(json['auscultation'] as Map<String, dynamic>),
      inquiry: InquiryData.fromJson(json['inquiry'] as Map<String, dynamic>),
      palpation: PalpationData.fromJson(json['palpation'] as Map<String, dynamic>),
      conclusion: json['conclusion'] as String,
      doctorId: json['doctorId'] as String?,
      doctorName: json['doctorName'] as String?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'diagnosisTime': diagnosisTime.toIso8601String(),
      'inspection': inspection.toJson(),
      'auscultation': auscultation.toJson(),
      'inquiry': inquiry.toJson(),
      'palpation': palpation.toJson(),
      'conclusion': conclusion,
      if (doctorId != null) 'doctorId': doctorId,
      if (doctorName != null) 'doctorName': doctorName,
    };
  }
  
  @override
  String toString() {
    return jsonEncode(toJson());
  }
}

/// 望诊数据
///
/// 包含对患者的望诊（视诊）观察记录
class InspectionData {
  /// 面部表现
  final FacialData facial;
  
  /// 舌象
  final TongueData tongue;
  
  /// 体态
  final BodyFormData bodyForm;
  
  /// 皮肤
  final SkinData skin;
  
  /// 排泄物
  final ExcretionData? excretion;
  
  /// 其他望诊数据
  final Map<String, dynamic>? extraData;
  
  /// 创建望诊数据
  InspectionData({
    required this.facial,
    required this.tongue,
    required this.bodyForm,
    required this.skin,
    this.excretion,
    this.extraData,
  });
  
  /// 从JSON创建实例
  factory InspectionData.fromJson(Map<String, dynamic> json) {
    return InspectionData(
      facial: FacialData.fromJson(json['facial'] as Map<String, dynamic>),
      tongue: TongueData.fromJson(json['tongue'] as Map<String, dynamic>),
      bodyForm: BodyFormData.fromJson(json['bodyForm'] as Map<String, dynamic>),
      skin: SkinData.fromJson(json['skin'] as Map<String, dynamic>),
      excretion: json['excretion'] != null
          ? ExcretionData.fromJson(json['excretion'] as Map<String, dynamic>)
          : null,
      extraData: json['extraData'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'facial': facial.toJson(),
      'tongue': tongue.toJson(),
      'bodyForm': bodyForm.toJson(),
      'skin': skin.toJson(),
      if (excretion != null) 'excretion': excretion!.toJson(),
      if (extraData != null) 'extraData': extraData,
    };
  }
}

/// 面部表现数据
class FacialData {
  /// 面色
  final String complexion;
  
  /// 面色特征描述
  final List<String> complexionFeatures;
  
  /// 精神状态
  final String spirit;
  
  /// 眼睛状态
  final String eyes;
  
  /// 嘴唇状态
  final String lips;
  
  /// 面部其他特征
  final Map<String, dynamic>? extraFeatures;
  
  /// 创建面部表现数据
  FacialData({
    required this.complexion,
    required this.complexionFeatures,
    required this.spirit,
    required this.eyes,
    required this.lips,
    this.extraFeatures,
  });
  
  /// 从JSON创建实例
  factory FacialData.fromJson(Map<String, dynamic> json) {
    return FacialData(
      complexion: json['complexion'] as String,
      complexionFeatures: (json['complexionFeatures'] as List).cast<String>(),
      spirit: json['spirit'] as String,
      eyes: json['eyes'] as String,
      lips: json['lips'] as String,
      extraFeatures: json['extraFeatures'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'complexion': complexion,
      'complexionFeatures': complexionFeatures,
      'spirit': spirit,
      'eyes': eyes,
      'lips': lips,
      if (extraFeatures != null) 'extraFeatures': extraFeatures,
    };
  }
}

/// 舌象数据
class TongueData {
  /// 舌质颜色
  final String tongueColor;
  
  /// 舌体形态特征
  final List<String> tongueForm;
  
  /// 舌体胖瘦程度
  final String tongueBody;
  
  /// 舌面湿润度
  final String tongueMoisture;
  
  /// 舌苔颜色
  final String coatingColor;
  
  /// 舌苔厚度
  final String coatingThickness;
  
  /// 舌苔分布
  final String coatingDistribution;
  
  /// 舌下络脉
  final String? sublingualVeins;
  
  /// 舌象图片URL
  final List<String>? tongueImages;
  
  /// 其他舌象特征
  final Map<String, dynamic>? extraFeatures;
  
  /// 创建舌象数据
  TongueData({
    required this.tongueColor,
    required this.tongueForm,
    required this.tongueBody,
    required this.tongueMoisture,
    required this.coatingColor,
    required this.coatingThickness,
    required this.coatingDistribution,
    this.sublingualVeins,
    this.tongueImages,
    this.extraFeatures,
  });
  
  /// 从JSON创建实例
  factory TongueData.fromJson(Map<String, dynamic> json) {
    return TongueData(
      tongueColor: json['tongueColor'] as String,
      tongueForm: (json['tongueForm'] as List).cast<String>(),
      tongueBody: json['tongueBody'] as String,
      tongueMoisture: json['tongueMoisture'] as String,
      coatingColor: json['coatingColor'] as String,
      coatingThickness: json['coatingThickness'] as String,
      coatingDistribution: json['coatingDistribution'] as String,
      sublingualVeins: json['sublingualVeins'] as String?,
      tongueImages: (json['tongueImages'] as List?)?.cast<String>(),
      extraFeatures: json['extraFeatures'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'tongueColor': tongueColor,
      'tongueForm': tongueForm,
      'tongueBody': tongueBody,
      'tongueMoisture': tongueMoisture,
      'coatingColor': coatingColor,
      'coatingThickness': coatingThickness,
      'coatingDistribution': coatingDistribution,
      if (sublingualVeins != null) 'sublingualVeins': sublingualVeins,
      if (tongueImages != null) 'tongueImages': tongueImages,
      if (extraFeatures != null) 'extraFeatures': extraFeatures,
    };
  }
}

/// 体态数据
class BodyFormData {
  /// 体型
  final String bodyType;
  
  /// 身材
  final String bodyShape;
  
  /// 姿态
  final String posture;
  
  /// 动作特征
  final List<String> movementFeatures;
  
  /// 体态其他特征
  final Map<String, dynamic>? extraFeatures;
  
  /// 创建体态数据
  BodyFormData({
    required this.bodyType,
    required this.bodyShape,
    required this.posture,
    required this.movementFeatures,
    this.extraFeatures,
  });
  
  /// 从JSON创建实例
  factory BodyFormData.fromJson(Map<String, dynamic> json) {
    return BodyFormData(
      bodyType: json['bodyType'] as String,
      bodyShape: json['bodyShape'] as String,
      posture: json['posture'] as String,
      movementFeatures: (json['movementFeatures'] as List).cast<String>(),
      extraFeatures: json['extraFeatures'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'bodyType': bodyType,
      'bodyShape': bodyShape,
      'posture': posture,
      'movementFeatures': movementFeatures,
      if (extraFeatures != null) 'extraFeatures': extraFeatures,
    };
  }
}

/// 皮肤数据
class SkinData {
  /// 肤色
  final String skinColor;
  
  /// 肤质
  final String skinTexture;
  
  /// 皮肤湿润度
  final String skinMoisture;
  
  /// 皮肤特征
  final List<String> skinFeatures;
  
  /// 皮肤其他特征
  final Map<String, dynamic>? extraFeatures;
  
  /// 创建皮肤数据
  SkinData({
    required this.skinColor,
    required this.skinTexture,
    required this.skinMoisture,
    required this.skinFeatures,
    this.extraFeatures,
  });
  
  /// 从JSON创建实例
  factory SkinData.fromJson(Map<String, dynamic> json) {
    return SkinData(
      skinColor: json['skinColor'] as String,
      skinTexture: json['skinTexture'] as String,
      skinMoisture: json['skinMoisture'] as String,
      skinFeatures: (json['skinFeatures'] as List).cast<String>(),
      extraFeatures: json['extraFeatures'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'skinColor': skinColor,
      'skinTexture': skinTexture,
      'skinMoisture': skinMoisture,
      'skinFeatures': skinFeatures,
      if (extraFeatures != null) 'extraFeatures': extraFeatures,
    };
  }
}

/// 排泄物数据
class ExcretionData {
  /// 大便性状
  final String? stool;
  
  /// 大便特征
  final List<String>? stoolFeatures;
  
  /// 小便性状
  final String? urine;
  
  /// 小便特征
  final List<String>? urineFeatures;
  
  /// 其他排泄物特征
  final Map<String, dynamic>? extraFeatures;
  
  /// 创建排泄物数据
  ExcretionData({
    this.stool,
    this.stoolFeatures,
    this.urine,
    this.urineFeatures,
    this.extraFeatures,
  });
  
  /// 从JSON创建实例
  factory ExcretionData.fromJson(Map<String, dynamic> json) {
    return ExcretionData(
      stool: json['stool'] as String?,
      stoolFeatures: (json['stoolFeatures'] as List?)?.cast<String>(),
      urine: json['urine'] as String?,
      urineFeatures: (json['urineFeatures'] as List?)?.cast<String>(),
      extraFeatures: json['extraFeatures'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      if (stool != null) 'stool': stool,
      if (stoolFeatures != null) 'stoolFeatures': stoolFeatures,
      if (urine != null) 'urine': urine,
      if (urineFeatures != null) 'urineFeatures': urineFeatures,
      if (extraFeatures != null) 'extraFeatures': extraFeatures,
    };
  }
}

/// 闻诊数据
///
/// 包含对患者的闻诊（嗅诊和听诊）观察记录
class AuscultationData {
  /// 语言声音
  final VoiceData voice;
  
  /// 呼吸声
  final String breathing;
  
  /// 咳嗽声
  final String? cough;
  
  /// 气味
  final OdorData odor;
  
  /// 其他闻诊数据
  final Map<String, dynamic>? extraData;
  
  /// 创建闻诊数据
  AuscultationData({
    required this.voice,
    required this.breathing,
    this.cough,
    required this.odor,
    this.extraData,
  });
  
  /// 从JSON创建实例
  factory AuscultationData.fromJson(Map<String, dynamic> json) {
    return AuscultationData(
      voice: VoiceData.fromJson(json['voice'] as Map<String, dynamic>),
      breathing: json['breathing'] as String,
      cough: json['cough'] as String?,
      odor: OdorData.fromJson(json['odor'] as Map<String, dynamic>),
      extraData: json['extraData'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'voice': voice.toJson(),
      'breathing': breathing,
      if (cough != null) 'cough': cough,
      'odor': odor.toJson(),
      if (extraData != null) 'extraData': extraData,
    };
  }
}

/// 语言声音数据
class VoiceData {
  /// 声音特质
  final String voiceQuality;
  
  /// 语速
  final String speechRate;
  
  /// 语音特征
  final List<String> voiceFeatures;
  
  /// 其他语音特征
  final Map<String, dynamic>? extraFeatures;
  
  /// 创建语言声音数据
  VoiceData({
    required this.voiceQuality,
    required this.speechRate,
    required this.voiceFeatures,
    this.extraFeatures,
  });
  
  /// 从JSON创建实例
  factory VoiceData.fromJson(Map<String, dynamic> json) {
    return VoiceData(
      voiceQuality: json['voiceQuality'] as String,
      speechRate: json['speechRate'] as String,
      voiceFeatures: (json['voiceFeatures'] as List).cast<String>(),
      extraFeatures: json['extraFeatures'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'voiceQuality': voiceQuality,
      'speechRate': speechRate,
      'voiceFeatures': voiceFeatures,
      if (extraFeatures != null) 'extraFeatures': extraFeatures,
    };
  }
}

/// 气味数据
class OdorData {
  /// 口气
  final String breath;
  
  /// 体味
  final String body;
  
  /// 排泄物气味
  final Map<String, String>? excretionOdors;
  
  /// 其他气味特征
  final Map<String, dynamic>? extraFeatures;
  
  /// 创建气味数据
  OdorData({
    required this.breath,
    required this.body,
    this.excretionOdors,
    this.extraFeatures,
  });
  
  /// 从JSON创建实例
  factory OdorData.fromJson(Map<String, dynamic> json) {
    return OdorData(
      breath: json['breath'] as String,
      body: json['body'] as String,
      excretionOdors: json['excretionOdors'] != null
          ? Map<String, String>.from(json['excretionOdors'] as Map)
          : null,
      extraFeatures: json['extraFeatures'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'breath': breath,
      'body': body,
      if (excretionOdors != null) 'excretionOdors': excretionOdors,
      if (extraFeatures != null) 'extraFeatures': extraFeatures,
    };
  }
}

/// 问诊数据
///
/// 包含通过问诊收集的患者自述症状和病史信息
class InquiryData {
  /// 主诉
  final String chiefComplaint;
  
  /// 病史
  final MedicalHistoryData medicalHistory;
  
  /// 生活习惯
  final LifestyleData lifestyle;
  
  /// 系统症状问询
  final SystemInquiryData systemInquiry;
  
  /// 其他问诊数据
  final Map<String, dynamic>? extraData;
  
  /// 创建问诊数据
  InquiryData({
    required this.chiefComplaint,
    required this.medicalHistory,
    required this.lifestyle,
    required this.systemInquiry,
    this.extraData,
  });
  
  /// 从JSON创建实例
  factory InquiryData.fromJson(Map<String, dynamic> json) {
    return InquiryData(
      chiefComplaint: json['chiefComplaint'] as String,
      medicalHistory: MedicalHistoryData.fromJson(json['medicalHistory'] as Map<String, dynamic>),
      lifestyle: LifestyleData.fromJson(json['lifestyle'] as Map<String, dynamic>),
      systemInquiry: SystemInquiryData.fromJson(json['systemInquiry'] as Map<String, dynamic>),
      extraData: json['extraData'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'chiefComplaint': chiefComplaint,
      'medicalHistory': medicalHistory.toJson(),
      'lifestyle': lifestyle.toJson(),
      'systemInquiry': systemInquiry.toJson(),
      if (extraData != null) 'extraData': extraData,
    };
  }
}

/// 病史数据
class MedicalHistoryData {
  /// 现病史
  final String presentIllness;
  
  /// 既往史
  final String pastHistory;
  
  /// 家族史
  final String familyHistory;
  
  /// 过敏史
  final String allergicHistory;
  
  /// 用药史
  final String medicationHistory;
  
  /// 其他病史信息
  final Map<String, dynamic>? extraHistory;
  
  /// 创建病史数据
  MedicalHistoryData({
    required this.presentIllness,
    required this.pastHistory,
    required this.familyHistory,
    required this.allergicHistory,
    required this.medicationHistory,
    this.extraHistory,
  });
  
  /// 从JSON创建实例
  factory MedicalHistoryData.fromJson(Map<String, dynamic> json) {
    return MedicalHistoryData(
      presentIllness: json['presentIllness'] as String,
      pastHistory: json['pastHistory'] as String,
      familyHistory: json['familyHistory'] as String,
      allergicHistory: json['allergicHistory'] as String,
      medicationHistory: json['medicationHistory'] as String,
      extraHistory: json['extraHistory'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'presentIllness': presentIllness,
      'pastHistory': pastHistory,
      'familyHistory': familyHistory,
      'allergicHistory': allergicHistory,
      'medicationHistory': medicationHistory,
      if (extraHistory != null) 'extraHistory': extraHistory,
    };
  }
}

/// 生活习惯数据
class LifestyleData {
  /// 饮食习惯
  final String diet;
  
  /// 睡眠情况
  final String sleep;
  
  /// 情绪状态
  final String emotion;
  
  /// 运动习惯
  final String exercise;
  
  /// 嗜好习惯
  final String habits;
  
  /// 其他生活习惯
  final Map<String, dynamic>? extraLifestyle;
  
  /// 创建生活习惯数据
  LifestyleData({
    required this.diet,
    required this.sleep,
    required this.emotion,
    required this.exercise,
    required this.habits,
    this.extraLifestyle,
  });
  
  /// 从JSON创建实例
  factory LifestyleData.fromJson(Map<String, dynamic> json) {
    return LifestyleData(
      diet: json['diet'] as String,
      sleep: json['sleep'] as String,
      emotion: json['emotion'] as String,
      exercise: json['exercise'] as String,
      habits: json['habits'] as String,
      extraLifestyle: json['extraLifestyle'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'diet': diet,
      'sleep': sleep,
      'emotion': emotion,
      'exercise': exercise,
      'habits': habits,
      if (extraLifestyle != null) 'extraLifestyle': extraLifestyle,
    };
  }
}

/// 系统症状问询数据
class SystemInquiryData {
  /// 头部症状
  final List<String>? headSymptoms;
  
  /// 胸部症状
  final List<String>? chestSymptoms;
  
  /// 腹部症状
  final List<String>? abdominalSymptoms;
  
  /// 四肢症状
  final List<String>? limbSymptoms;
  
  /// 泌尿生殖系统症状
  final List<String>? urogenitalSymptoms;
  
  /// 消化系统症状
  final List<String>? digestiveSymptoms;
  
  /// 呼吸系统症状
  final List<String>? respiratorySymptoms;
  
  /// 心血管系统症状
  final List<String>? cardiovascularSymptoms;
  
  /// 神经系统症状
  final List<String>? neurologicalSymptoms;
  
  /// 其他系统症状
  final Map<String, List<String>>? otherSymptoms;
  
  /// 创建系统症状问询数据
  SystemInquiryData({
    this.headSymptoms,
    this.chestSymptoms,
    this.abdominalSymptoms,
    this.limbSymptoms,
    this.urogenitalSymptoms,
    this.digestiveSymptoms,
    this.respiratorySymptoms,
    this.cardiovascularSymptoms,
    this.neurologicalSymptoms,
    this.otherSymptoms,
  });
  
  /// 从JSON创建实例
  factory SystemInquiryData.fromJson(Map<String, dynamic> json) {
    return SystemInquiryData(
      headSymptoms: (json['headSymptoms'] as List?)?.cast<String>(),
      chestSymptoms: (json['chestSymptoms'] as List?)?.cast<String>(),
      abdominalSymptoms: (json['abdominalSymptoms'] as List?)?.cast<String>(),
      limbSymptoms: (json['limbSymptoms'] as List?)?.cast<String>(),
      urogenitalSymptoms: (json['urogenitalSymptoms'] as List?)?.cast<String>(),
      digestiveSymptoms: (json['digestiveSymptoms'] as List?)?.cast<String>(),
      respiratorySymptoms: (json['respiratorySymptoms'] as List?)?.cast<String>(),
      cardiovascularSymptoms: (json['cardiovascularSymptoms'] as List?)?.cast<String>(),
      neurologicalSymptoms: (json['neurologicalSymptoms'] as List?)?.cast<String>(),
      otherSymptoms: json['otherSymptoms'] != null
          ? (json['otherSymptoms'] as Map).map((k, v) => MapEntry(k.toString(), (v as List).cast<String>()))
          : null,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      if (headSymptoms != null) 'headSymptoms': headSymptoms,
      if (chestSymptoms != null) 'chestSymptoms': chestSymptoms,
      if (abdominalSymptoms != null) 'abdominalSymptoms': abdominalSymptoms,
      if (limbSymptoms != null) 'limbSymptoms': limbSymptoms,
      if (urogenitalSymptoms != null) 'urogenitalSymptoms': urogenitalSymptoms,
      if (digestiveSymptoms != null) 'digestiveSymptoms': digestiveSymptoms,
      if (respiratorySymptoms != null) 'respiratorySymptoms': respiratorySymptoms,
      if (cardiovascularSymptoms != null) 'cardiovascularSymptoms': cardiovascularSymptoms,
      if (neurologicalSymptoms != null) 'neurologicalSymptoms': neurologicalSymptoms,
      if (otherSymptoms != null) 'otherSymptoms': otherSymptoms,
    };
  }
}

/// 切诊数据
///
/// 包含通过切诊（摸脉和按压）观察记录的患者信息
class PalpationData {
  /// 脉象数据
  final PulseData pulse;
  
  /// 腹诊数据
  final AbdominalPalpationData? abdominal;
  
  /// 经络穴位按压反应
  final AcupointPalpationData? acupoints;
  
  /// 其他切诊数据
  final Map<String, dynamic>? extraData;
  
  /// 创建切诊数据
  PalpationData({
    required this.pulse,
    this.abdominal,
    this.acupoints,
    this.extraData,
  });
  
  /// 从JSON创建实例
  factory PalpationData.fromJson(Map<String, dynamic> json) {
    return PalpationData(
      pulse: PulseData.fromJson(json['pulse'] as Map<String, dynamic>),
      abdominal: json['abdominal'] != null
          ? AbdominalPalpationData.fromJson(json['abdominal'] as Map<String, dynamic>)
          : null,
      acupoints: json['acupoints'] != null
          ? AcupointPalpationData.fromJson(json['acupoints'] as Map<String, dynamic>)
          : null,
      extraData: json['extraData'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'pulse': pulse.toJson(),
      if (abdominal != null) 'abdominal': abdominal!.toJson(),
      if (acupoints != null) 'acupoints': acupoints!.toJson(),
      if (extraData != null) 'extraData': extraData,
    };
  }
}

/// 脉象数据
class PulseData {
  /// 左寸脉
  final String leftCun;
  
  /// 左关脉
  final String leftGuan;
  
  /// 左尺脉
  final String leftChi;
  
  /// 右寸脉
  final String rightCun;
  
  /// 右关脉
  final String rightGuan;
  
  /// 右尺脉
  final String rightChi;
  
  /// 脉率
  final int? pulseRate;
  
  /// 总体脉象特征
  final List<String> pulseCharacteristics;
  
  /// 其他脉象特征
  final Map<String, dynamic>? extraFeatures;
  
  /// 创建脉象数据
  PulseData({
    required this.leftCun,
    required this.leftGuan,
    required this.leftChi,
    required this.rightCun,
    required this.rightGuan,
    required this.rightChi,
    this.pulseRate,
    required this.pulseCharacteristics,
    this.extraFeatures,
  });
  
  /// 从JSON创建实例
  factory PulseData.fromJson(Map<String, dynamic> json) {
    return PulseData(
      leftCun: json['leftCun'] as String,
      leftGuan: json['leftGuan'] as String,
      leftChi: json['leftChi'] as String,
      rightCun: json['rightCun'] as String,
      rightGuan: json['rightGuan'] as String,
      rightChi: json['rightChi'] as String,
      pulseRate: json['pulseRate'] as int?,
      pulseCharacteristics: (json['pulseCharacteristics'] as List).cast<String>(),
      extraFeatures: json['extraFeatures'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'leftCun': leftCun,
      'leftGuan': leftGuan,
      'leftChi': leftChi,
      'rightCun': rightCun,
      'rightGuan': rightGuan,
      'rightChi': rightChi,
      if (pulseRate != null) 'pulseRate': pulseRate,
      'pulseCharacteristics': pulseCharacteristics,
      if (extraFeatures != null) 'extraFeatures': extraFeatures,
    };
  }
}

/// 腹诊数据
class AbdominalPalpationData {
  /// 腹部质地
  final String texture;
  
  /// 腹部温度
  final String temperature;
  
  /// 压痛点
  final List<String>? tenderPoints;
  
  /// 腹部反应区
  final Map<String, String>? abdominalReactions;
  
  /// 其他腹诊特征
  final Map<String, dynamic>? extraFeatures;
  
  /// 创建腹诊数据
  AbdominalPalpationData({
    required this.texture,
    required this.temperature,
    this.tenderPoints,
    this.abdominalReactions,
    this.extraFeatures,
  });
  
  /// 从JSON创建实例
  factory AbdominalPalpationData.fromJson(Map<String, dynamic> json) {
    return AbdominalPalpationData(
      texture: json['texture'] as String,
      temperature: json['temperature'] as String,
      tenderPoints: (json['tenderPoints'] as List?)?.cast<String>(),
      abdominalReactions: json['abdominalReactions'] != null
          ? Map<String, String>.from(json['abdominalReactions'] as Map)
          : null,
      extraFeatures: json['extraFeatures'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'texture': texture,
      'temperature': temperature,
      if (tenderPoints != null) 'tenderPoints': tenderPoints,
      if (abdominalReactions != null) 'abdominalReactions': abdominalReactions,
      if (extraFeatures != null) 'extraFeatures': extraFeatures,
    };
  }
}

/// 经络穴位按压数据
class AcupointPalpationData {
  /// 阳性反应穴位
  final Map<String, String> positivePoints;
  
  /// 经络反应
  final Map<String, String>? meridianReactions;
  
  /// 特定穴位组合反应
  final Map<String, dynamic>? pointCombinations;
  
  /// 其他穴位按压特征
  final Map<String, dynamic>? extraFeatures;
  
  /// 创建经络穴位按压数据
  AcupointPalpationData({
    required this.positivePoints,
    this.meridianReactions,
    this.pointCombinations,
    this.extraFeatures,
  });
  
  /// 从JSON创建实例
  factory AcupointPalpationData.fromJson(Map<String, dynamic> json) {
    return AcupointPalpationData(
      positivePoints: Map<String, String>.from(json['positivePoints'] as Map),
      meridianReactions: json['meridianReactions'] != null
          ? Map<String, String>.from(json['meridianReactions'] as Map)
          : null,
      pointCombinations: json['pointCombinations'] as Map<String, dynamic>?,
      extraFeatures: json['extraFeatures'] as Map<String, dynamic>?,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'positivePoints': positivePoints,
      if (meridianReactions != null) 'meridianReactions': meridianReactions,
      if (pointCombinations != null) 'pointCombinations': pointCombinations,
      if (extraFeatures != null) 'extraFeatures': extraFeatures,
    };
  }
} 