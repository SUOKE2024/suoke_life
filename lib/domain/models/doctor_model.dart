import 'package:suoke_life/domain/models/chat_contact_model.dart';

/// 名医模型
class Doctor {
  /// 医生ID
  final String id;
  
  /// 医生姓名
  final String name;
  
  /// 头像URL
  final String avatarUrl;
  
  /// 医生职称
  final DoctorTitle title;
  
  /// 专业方向
  final List<Specialty> specialties;
  
  /// 执业医院
  final String hospital;
  
  /// 所在科室
  final String department;
  
  /// 医生简介
  final String description;
  
  /// 执业年限
  final int yearsOfExperience;
  
  /// 医生资格证号
  final String licenseNumber;
  
  /// 认证状态
  final VerificationStatus verificationStatus;
  
  /// 评分（1-5）
  final double rating;
  
  /// 评价数量
  final int reviewCount;
  
  /// 咨询费用
  final double consultationFee;
  
  /// 是否在线
  final bool isOnline;
  
  /// 最后在线时间
  final DateTime lastActiveTime;
  
  /// 附加数据
  final Map<String, dynamic>? extraData;

  /// 构造函数
  Doctor({
    required this.id,
    required this.name,
    required this.avatarUrl,
    required this.title,
    required this.specialties,
    required this.hospital,
    required this.department,
    required this.description,
    required this.yearsOfExperience,
    required this.licenseNumber,
    this.verificationStatus = VerificationStatus.verified,
    this.rating = 5.0,
    this.reviewCount = 0,
    required this.consultationFee,
    this.isOnline = false,
    required this.lastActiveTime,
    this.extraData,
  });
  
  /// 转换为聊天联系人
  ChatContact toChatContact() {
    return ChatContact(
      id: id,
      name: name,
      type: ChatContactType.doctor,
      avatarUrl: avatarUrl,
      description: '$title · $hospital',
      lastActiveTime: lastActiveTime,
      extraData: {
        'title': title.toString(),
        'specialties': specialties.map((s) => s.toString()).toList(),
        'hospital': hospital,
        'department': department,
        'rating': rating,
        'isOnline': isOnline,
        'consultationFee': consultationFee,
      },
    );
  }
}

/// 医生职称
enum DoctorTitle {
  /// 主任医师
  chiefPhysician,
  
  /// 副主任医师
  associateChiefPhysician,
  
  /// 主治医师
  attendingPhysician,
  
  /// 住院医师
  residentPhysician,
  
  /// 医师
  physician,
  
  /// 中医
  chineseMedicineDoctor,
}

/// 专业方向
enum Specialty {
  /// 内科
  internalMedicine,
  
  /// 外科
  surgery,
  
  /// 妇产科
  obstetricsAndGynecology,
  
  /// 儿科
  pediatrics,
  
  /// 针灸
  acupuncture,
  
  /// 推拿
  massage,
  
  /// 中药学
  herbology,
  
  /// 养生保健
  healthPreservation,
} 