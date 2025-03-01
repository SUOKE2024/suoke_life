import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';

import '../core/agent_microkernel.dart';
import '../core/security_privacy_framework.dart';
import '../models/ai_agent.dart';
import 'service_integration.dart';

/// 医疗机构类型
enum MedicalInstitutionType {
  /// 三级医院
  tertiaryHospital,
  
  /// 二级医院
  secondaryHospital,
  
  /// 一级医院
  primaryHospital,
  
  /// 社区医疗中心
  communityCare,
  
  /// 专科医院
  specialistClinic,
  
  /// 中医院
  tcmHospital,
  
  /// 健康管理中心
  healthManagementCenter,
  
  /// 综合医院
  generalHospital,
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
  
  /// 实习医师
  intern,
  
  /// 助理医师
  assistantPhysician,
  
  /// 医师
  physician,
  
  /// 专家
  expert,
}

/// 医疗科室类型
enum MedicalDepartment {
  /// 内科
  internalMedicine,
  
  /// 外科
  surgery,
  
  /// 妇产科
  obstetricsGynecology,
  
  /// 儿科
  pediatrics,
  
  /// 中医科
  traditionalChineseMedicine,
  
  /// 皮肤科
  dermatology,
  
  /// 眼科
  ophthalmology,
  
  /// 耳鼻喉科
  otolaryngology,
  
  /// 口腔科
  stomatology,
  
  /// 精神心理科
  psychiatry,
  
  /// 神经科
  neurology,
  
  /// 肿瘤科
  oncology,
  
  /// 康复科
  rehabilitation,
  
  /// 营养科
  nutrition,
  
  /// 预防医学科
  preventiveMedicine,
}

/// 预约状态
enum AppointmentStatus {
  /// 待确认
  pending,
  
  /// 已确认
  confirmed,
  
  /// 已完成
  completed,
  
  /// 已取消
  cancelled,
  
  /// 已过期
  expired,
  
  ///
  rescheduled,
}

/// 支付方式
enum PaymentMethod {
  /// 医保
  medicalInsurance,
  
  /// 自费
  selfPay,
  
  /// 商业保险
  commercialInsurance,
  
  /// 公司福利
  corporateWelfare,
}

/// 保险类型
enum InsuranceType {
  /// 基本医疗保险
  basicMedicalInsurance,
  
  /// 城镇职工医保
  urbanEmployeeMedicalInsurance,
  
  /// 城乡居民医保
  urbanRuralResidentMedicalInsurance,
  
  /// 大病保险
  criticalIllnessInsurance,
  
  /// 补充医疗保险
  supplementaryMedicalInsurance,
  
  /// 商业健康保险
  commercialHealthInsurance,
}

/// 远程医疗类型
enum TelemedicineType {
  /// 视频问诊
  videoConsultation,
  
  /// 图文问诊
  imageTextConsultation,
  
  /// 电话问诊
  telephoneConsultation,
  
  /// 在线随访
  onlineFollowUp,
  
  /// 远程监测
  remoteMonitoring,
  
  /// 远程会诊
  remoteConsultation,
}

/// 医疗机构
class MedicalInstitution {
  /// 机构ID
  final String id;
  
  /// 机构名称
  final String name;
  
  /// 机构类型
  final MedicalInstitutionType type;
  
  /// 机构等级（A-AAA）
  final String? grade;
  
  /// 地址
  final String address;
  
  /// 省份
  final String province;
  
  /// 城市
  final String city;
  
  /// 区/县
  final String district;
  
  /// 详细地址
  final String detailedAddress;
  
  /// 联系电话
  final String phone;
  
  /// 官方网站
  final String? website;
  
  /// 可预约科室
  final List<MedicalDepartment>? availableDepartments;
  
  /// 机构简介
  final String? introduction;
  
  /// 营业时间
  final String? operatingHours;
  
  /// 机构照片URL列表
  final List<String>? imageUrls;
  
  /// 经度
  final double? longitude;
  
  /// 纬度
  final double? latitude;
  
  /// 是否支持线上预约
  final bool supportsOnlineAppointment;
  
  /// 是否支持远程医疗
  final bool supportsTelemedicine;
  
  /// 平均评分（1-5）
  final double? rating;
  
  /// 评价数量
  final int? reviewCount;
  
  /// 医保定点
  final bool isMedicalInsuranceDesignated;
  
  /// 急诊电话
  final String? emergencyPhone;
  
  const MedicalInstitution({
    required this.id,
    required this.name,
    required this.type,
    this.grade,
    required this.address,
    required this.province,
    required this.city,
    required this.district,
    required this.detailedAddress,
    required this.phone,
    this.website,
    this.availableDepartments,
    this.introduction,
    this.operatingHours,
    this.imageUrls,
    this.longitude,
    this.latitude,
    required this.supportsOnlineAppointment,
    required this.supportsTelemedicine,
    this.rating,
    this.reviewCount,
    required this.isMedicalInsuranceDesignated,
    this.emergencyPhone,
  });
  
  /// 从JSON创建
  factory MedicalInstitution.fromJson(Map<String, dynamic> json) {
    return MedicalInstitution(
      id: json['id'],
      name: json['name'],
      type: MedicalInstitutionType.values.firstWhere(
        (t) => t.toString() == 'MedicalInstitutionType.${json['type']}',
        orElse: () => MedicalInstitutionType.generalHospital,
      ),
      grade: json['grade'],
      address: json['address'],
      province: json['province'],
      city: json['city'],
      district: json['district'],
      detailedAddress: json['detailed_address'],
      phone: json['phone'],
      website: json['website'],
      availableDepartments: json['available_departments'] != null
        ? (json['available_departments'] as List).map((d) =>
            MedicalDepartment.values.firstWhere(
              (dep) => dep.toString() == 'MedicalDepartment.$d',
              orElse: () => MedicalDepartment.internalMedicine,
            )
          ).toList()
        : null,
      introduction: json['introduction'],
      operatingHours: json['operating_hours'],
      imageUrls: json['image_urls'] != null
        ? List<String>.from(json['image_urls'])
        : null,
      longitude: json['longitude']?.toDouble(),
      latitude: json['latitude']?.toDouble(),
      supportsOnlineAppointment: json['supports_online_appointment'] ?? false,
      supportsTelemedicine: json['supports_telemedicine'] ?? false,
      rating: json['rating']?.toDouble(),
      reviewCount: json['review_count'],
      isMedicalInsuranceDesignated: json['is_medical_insurance_designated'] ?? false,
      emergencyPhone: json['emergency_phone'],
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'type': type.toString().split('.').last,
      'grade': grade,
      'address': address,
      'province': province,
      'city': city,
      'district': district,
      'detailed_address': detailedAddress,
      'phone': phone,
      'website': website,
      'available_departments': availableDepartments?.map(
        (d) => d.toString().split('.').last
      ).toList(),
      'introduction': introduction,
      'operating_hours': operatingHours,
      'image_urls': imageUrls,
      'longitude': longitude,
      'latitude': latitude,
      'supports_online_appointment': supportsOnlineAppointment,
      'supports_telemedicine': supportsTelemedicine,
      'rating': rating,
      'review_count': reviewCount,
      'is_medical_insurance_designated': isMedicalInsuranceDesignated,
      'emergency_phone': emergencyPhone,
    };
  }
}

/// 医生信息
class Doctor {
  /// 医生ID
  final String id;
  
  /// 姓名
  final String name;
  
  /// 性别
  final String gender;
  
  /// 照片URL
  final String? photoUrl;
  
  /// 所属机构ID
  final String institutionId;
  
  /// 所属机构名称
  final String institutionName;
  
  /// 科室
  final MedicalDepartment department;
  
  /// 职称
  final DoctorTitle title;
  
  /// 专长
  final List<String> specialties;
  
  /// 简介
  final String? introduction;
  
  /// 教育背景
  final List<String>? education;
  
  /// 工作经历
  final List<String>? workExperience;
  
  /// 学术成就
  final List<String>? academicAchievements;
  
  /// 评分（1-5）
  final double? rating;
  
  /// 评价数量
  final int? reviewCount;
  
  /// 问诊费用（元）
  final double? consultationFee;
  
  /// 出诊安排
  final Map<String, List<String>>? scheduleInfo;
  
  /// 可预约日期列表
  final List<DateTime>? availableDates;
  
  /// 是否支持远程医疗
  final bool supportsTelemedicine;
  
  /// 是否支持医保
  final bool supportsMedicalInsurance;
  
  const Doctor({
    required this.id,
    required this.name,
    required this.gender,
    this.photoUrl,
    required this.institutionId,
    required this.institutionName,
    required this.department,
    required this.title,
    required this.specialties,
    this.introduction,
    this.education,
    this.workExperience,
    this.academicAchievements,
    this.rating,
    this.reviewCount,
    this.consultationFee,
    this.scheduleInfo,
    this.availableDates,
    required this.supportsTelemedicine,
    required this.supportsMedicalInsurance,
  });
  
  /// 从JSON创建
  factory Doctor.fromJson(Map<String, dynamic> json) {
    return Doctor(
      id: json['id'],
      name: json['name'],
      gender: json['gender'],
      photoUrl: json['photo_url'],
      institutionId: json['institution_id'],
      institutionName: json['institution_name'],
      department: MedicalDepartment.values.firstWhere(
        (d) => d.toString() == 'MedicalDepartment.${json['department']}',
        orElse: () => MedicalDepartment.internalMedicine,
      ),
      title: DoctorTitle.values.firstWhere(
        (t) => t.toString() == 'DoctorTitle.${json['title']}',
        orElse: () => DoctorTitle.physician,
      ),
      specialties: List<String>.from(json['specialties']),
      introduction: json['introduction'],
      education: json['education'] != null
        ? List<String>.from(json['education'])
        : null,
      workExperience: json['work_experience'] != null
        ? List<String>.from(json['work_experience'])
        : null,
      academicAchievements: json['academic_achievements'] != null
        ? List<String>.from(json['academic_achievements'])
        : null,
      rating: json['rating']?.toDouble(),
      reviewCount: json['review_count'],
      consultationFee: json['consultation_fee']?.toDouble(),
      scheduleInfo: json['schedule_info'] != null
        ? Map<String, List<String>>.from(
            json['schedule_info'].map((key, value) => 
              MapEntry(key, List<String>.from(value))
            )
          )
        : null,
      availableDates: json['available_dates'] != null
        ? (json['available_dates'] as List).map((date) => 
            DateTime.parse(date)).toList()
        : null,
      supportsTelemedicine: json['supports_telemedicine'] ?? false,
      supportsMedicalInsurance: json['supports_medical_insurance'] ?? false,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'gender': gender,
      'photo_url': photoUrl,
      'institution_id': institutionId,
      'institution_name': institutionName,
      'department': department.toString().split('.').last,
      'title': title.toString().split('.').last,
      'specialties': specialties,
      'introduction': introduction,
      'education': education,
      'work_experience': workExperience,
      'academic_achievements': academicAchievements,
      'rating': rating,
      'review_count': reviewCount,
      'consultation_fee': consultationFee,
      'schedule_info': scheduleInfo,
      'available_dates': availableDates?.map((date) => 
        date.toIso8601String()).toList(),
      'supports_telemedicine': supportsTelemedicine,
      'supports_medical_insurance': supportsMedicalInsurance,
    };
  }
}

/// 预约记录
class Appointment {
  /// 预约ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 医生ID
  final String doctorId;
  
  /// 医生姓名
  final String doctorName;
  
  /// 医疗机构ID
  final String institutionId;
  
  /// 医疗机构名称
  final String institutionName;
  
  /// 科室
  final MedicalDepartment department;
  
  /// 预约时间
  final DateTime appointmentTime;
  
  /// 创建时间
  final DateTime createdTime;
  
  /// 更新时间
  final DateTime updatedTime;
  
  /// 就诊类型（线上/线下）
  final bool isOnline;
  
  /// 远程医疗类型（如果是线上就诊）
  final TelemedicineType? telemedicineType;
  
  /// 预约状态
  final AppointmentStatus status;
  
  /// 就诊目的
  final String? purpose;
  
  /// 症状描述
  final String? symptomDescription;
  
  /// 就诊记录ID（完成后关联）
  final String? medicalRecordId;
  
  /// 支付金额
  final double? paymentAmount;
  
  /// 支付方式
  final PaymentMethod? paymentMethod;
  
  /// 支付状态
  final bool? isPaid;
  
  /// 支付时间
  final DateTime? paymentTime;
  
  /// 病历预览
  final String? medicalSummary;
  
  /// 患者反馈
  final String? patientFeedback;
  
  /// 医生反馈
  final String? doctorFeedback;
  
  /// 评分（1-5）
  final int? rating;
  
  const Appointment({
    required this.id,
    required this.userId,
    required this.doctorId,
    required this.doctorName,
    required this.institutionId,
    required this.institutionName,
    required this.department,
    required this.appointmentTime,
    required this.createdTime,
    required this.updatedTime,
    required this.isOnline,
    this.telemedicineType,
    required this.status,
    this.purpose,
    this.symptomDescription,
    this.medicalRecordId,
    this.paymentAmount,
    this.paymentMethod,
    this.isPaid,
    this.paymentTime,
    this.medicalSummary,
    this.patientFeedback,
    this.doctorFeedback,
    this.rating,
  });
  
  /// 从JSON创建
  factory Appointment.fromJson(Map<String, dynamic> json) {
    return Appointment(
      id: json['id'],
      userId: json['user_id'],
      doctorId: json['doctor_id'],
      doctorName: json['doctor_name'],
      institutionId: json['institution_id'],
      institutionName: json['institution_name'],
      department: MedicalDepartment.values.firstWhere(
        (d) => d.toString() == 'MedicalDepartment.${json['department']}',
        orElse: () => MedicalDepartment.internalMedicine,
      ),
      appointmentTime: DateTime.parse(json['appointment_time']),
      createdTime: DateTime.parse(json['created_time']),
      updatedTime: DateTime.parse(json['updated_time']),
      isOnline: json['is_online'] ?? false,
      telemedicineType: json['telemedicine_type'] != null
        ? TelemedicineType.values.firstWhere(
            (t) => t.toString() == 'TelemedicineType.${json['telemedicine_type']}',
            orElse: () => TelemedicineType.videoConsultation,
          )
        : null,
      status: AppointmentStatus.values.firstWhere(
        (s) => s.toString() == 'AppointmentStatus.${json['status']}',
        orElse: () => AppointmentStatus.pending,
      ),
      purpose: json['purpose'],
      symptomDescription: json['symptom_description'],
      medicalRecordId: json['medical_record_id'],
      paymentAmount: json['payment_amount']?.toDouble(),
      paymentMethod: json['payment_method'] != null
        ? PaymentMethod.values.firstWhere(
            (p) => p.toString() == 'PaymentMethod.${json['payment_method']}',
            orElse: () => PaymentMethod.selfPay,
          )
        : null,
      isPaid: json['is_paid'],
      paymentTime: json['payment_time'] != null
        ? DateTime.parse(json['payment_time'])
        : null,
      medicalSummary: json['medical_summary'],
      patientFeedback: json['patient_feedback'],
      doctorFeedback: json['doctor_feedback'],
      rating: json['rating'],
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'doctor_id': doctorId,
      'doctor_name': doctorName,
      'institution_id': institutionId,
      'institution_name': institutionName,
      'department': department.toString().split('.').last,
      'appointment_time': appointmentTime.toIso8601String(),
      'created_time': createdTime.toIso8601String(),
      'updated_time': updatedTime.toIso8601String(),
      'is_online': isOnline,
      'telemedicine_type': telemedicineType?.toString().split('.').last,
      'status': status.toString().split('.').last,
      'purpose': purpose,
      'symptom_description': symptomDescription,
      'medical_record_id': medicalRecordId,
      'payment_amount': paymentAmount,
      'payment_method': paymentMethod?.toString().split('.').last,
      'is_paid': isPaid,
      'payment_time': paymentTime?.toIso8601String(),
      'medical_summary': medicalSummary,
      'patient_feedback': patientFeedback,
      'doctor_feedback': doctorFeedback,
      'rating': rating,
    };
  }
}

/// 医疗保险信息
class MedicalInsurance {
  /// 保险ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 保险类型
  final InsuranceType type;
  
  /// 保险计划名称
  final String planName;
  
  /// 保险号码
  final String insuranceNumber;
  
  /// 保险状态（有效/失效）
  final bool isActive;
  
  /// 生效日期
  final DateTime effectiveDate;
  
  /// 到期日期
  final DateTime? expirationDate;
  
  /// 当年累计医保支付（元）
  final double? yearToDatePayment;
  
  /// 当年自付额度（元）
  final double? yearToDateDeductible;
  
  /// 个人账户余额（元）
  final double? personalAccountBalance;
  
  /// 医保定点医院列表
  final List<String>? designatedHospitals;
  
  /// 保险公司名称
  final String? insuranceCompany;
  
  /// 联系电话
  final String? contactPhone;
  
  /// 备注
  final String? notes;
  
  const MedicalInsurance({
    required this.id,
    required this.userId,
    required this.type,
    required this.planName,
    required this.insuranceNumber,
    required this.isActive,
    required this.effectiveDate,
    this.expirationDate,
    this.yearToDatePayment,
    this.yearToDateDeductible,
    this.personalAccountBalance,
    this.designatedHospitals,
    this.insuranceCompany,
    this.contactPhone,
    this.notes,
  });
  
  /// 从JSON创建
  factory MedicalInsurance.fromJson(Map<String, dynamic> json) {
    return MedicalInsurance(
      id: json['id'],
      userId: json['user_id'],
      type: InsuranceType.values.firstWhere(
        (t) => t.toString() == 'InsuranceType.${json['type']}',
        orElse: () => InsuranceType.basicMedicalInsurance,
      ),
      planName: json['plan_name'],
      insuranceNumber: json['insurance_number'],
      isActive: json['is_active'] ?? false,
      effectiveDate: DateTime.parse(json['effective_date']),
      expirationDate: json['expiration_date'] != null
        ? DateTime.parse(json['expiration_date'])
        : null,
      yearToDatePayment: json['year_to_date_payment']?.toDouble(),
      yearToDateDeductible: json['year_to_date_deductible']?.toDouble(),
      personalAccountBalance: json['personal_account_balance']?.toDouble(),
      designatedHospitals: json['designated_hospitals'] != null
        ? List<String>.from(json['designated_hospitals'])
        : null,
      insuranceCompany: json['insurance_company'],
      contactPhone: json['contact_phone'],
      notes: json['notes'],
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'type': type.toString().split('.').last,
      'plan_name': planName,
      'insurance_number': insuranceNumber,
      'is_active': isActive,
      'effective_date': effectiveDate.toIso8601String(),
      'expiration_date': expirationDate?.toIso8601String(),
      'year_to_date_payment': yearToDatePayment,
      'year_to_date_deductible': yearToDateDeductible,
      'personal_account_balance': personalAccountBalance,
      'designated_hospitals': designatedHospitals,
      'insurance_company': insuranceCompany,
      'contact_phone': contactPhone,
      'notes': notes,
    };
  }
}

/// 健康记录
class MedicalRecord {
  /// 记录ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 医生ID
  final String doctorId;
  
  /// 医生姓名
  final String doctorName;
  
  /// 机构ID
  final String institutionId;
  
  /// 机构名称
  final String institutionName;
  
  /// 科室
  final MedicalDepartment department;
  
  /// 记录类型
  final String recordType;
  
  /// 就诊日期
  final DateTime visitDate;
  
  /// 主诉
  final String chiefComplaint;
  
  /// 症状描述
  final String? symptomsDescription;
  
  /// 病史
  final String? medicalHistory;
  
  /// 诊断
  final List<String> diagnosis;
  
  /// 检查项目
  final List<Map<String, dynamic>>? examinations;
  
  /// 治疗方案
  final String? treatmentPlan;
  
  /// 处方
  final List<Map<String, dynamic>>? prescriptions;
  
  /// 建议
  final String? advice;
  
  /// 随访计划
  final String? followUpPlan;
  
  /// 下次复诊日期
  final DateTime? nextVisitDate;
  
  /// 检查报告URL列表
  final List<String>? reportUrls;
  
  /// 是否为远程就诊
  final bool isTelemedicine;
  
  /// 就诊费用
  final double? cost;
  
  /// 医保支付金额
  final double? insurancePayment;
  
  /// 自付金额
  final double? selfPayment;
  
  /// 创建时间
  final DateTime createdTime;
  
  /// 更新时间
  final DateTime updatedTime;
  
  const MedicalRecord({
    required this.id,
    required this.userId,
    required this.doctorId,
    required this.doctorName,
    required this.institutionId,
    required this.institutionName,
    required this.department,
    required this.recordType,
    required this.visitDate,
    required this.chiefComplaint,
    this.symptomsDescription,
    this.medicalHistory,
    required this.diagnosis,
    this.examinations,
    this.treatmentPlan,
    this.prescriptions,
    this.advice,
    this.followUpPlan,
    this.nextVisitDate,
    this.reportUrls,
    required this.isTelemedicine,
    this.cost,
    this.insurancePayment,
    this.selfPayment,
    required this.createdTime,
    required this.updatedTime,
  });
  
  /// 从JSON创建
  factory MedicalRecord.fromJson(Map<String, dynamic> json) {
    return MedicalRecord(
      id: json['id'],
      userId: json['user_id'],
      doctorId: json['doctor_id'],
      doctorName: json['doctor_name'],
      institutionId: json['institution_id'],
      institutionName: json['institution_name'],
      department: MedicalDepartment.values.firstWhere(
        (d) => d.toString() == 'MedicalDepartment.${json['department']}',
        orElse: () => MedicalDepartment.internalMedicine,
      ),
      recordType: json['record_type'],
      visitDate: DateTime.parse(json['visit_date']),
      chiefComplaint: json['chief_complaint'],
      symptomsDescription: json['symptoms_description'],
      medicalHistory: json['medical_history'],
      diagnosis: List<String>.from(json['diagnosis']),
      examinations: json['examinations'] != null
        ? List<Map<String, dynamic>>.from(json['examinations'].map(
            (e) => Map<String, dynamic>.from(e)))
        : null,
      treatmentPlan: json['treatment_plan'],
      prescriptions: json['prescriptions'] != null
        ? List<Map<String, dynamic>>.from(json['prescriptions'].map(
            (p) => Map<String, dynamic>.from(p)))
        : null,
      advice: json['advice'],
      followUpPlan: json['follow_up_plan'],
      nextVisitDate: json['next_visit_date'] != null
        ? DateTime.parse(json['next_visit_date'])
        : null,
      reportUrls: json['report_urls'] != null
        ? List<String>.from(json['report_urls'])
        : null,
      isTelemedicine: json['is_telemedicine'] ?? false,
      cost: json['cost']?.toDouble(),
      insurancePayment: json['insurance_payment']?.toDouble(),
      selfPayment: json['self_payment']?.toDouble(),
      createdTime: DateTime.parse(json['created_time']),
      updatedTime: DateTime.parse(json['updated_time']),
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'doctor_id': doctorId,
      'doctor_name': doctorName,
      'institution_id': institutionId,
      'institution_name': institutionName,
      'department': department.toString().split('.').last,
      'record_type': recordType,
      'visit_date': visitDate.toIso8601String(),
      'chief_complaint': chiefComplaint,
      'symptoms_description': symptomsDescription,
      'medical_history': medicalHistory,
      'diagnosis': diagnosis,
      'examinations': examinations,
      'treatment_plan': treatmentPlan,
      'prescriptions': prescriptions,
      'advice': advice,
      'follow_up_plan': followUpPlan,
      'next_visit_date': nextVisitDate?.toIso8601String(),
      'report_urls': reportUrls,
      'is_telemedicine': isTelemedicine,
      'cost': cost,
      'insurance_payment': insurancePayment,
      'self_payment': selfPayment,
      'created_time': createdTime.toIso8601String(),
      'updated_time': updatedTime.toIso8601String(),
    };
  }
}

/// 远程医疗会话
class TelemedicineSession {
  /// 会话ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 医生ID
  final String doctorId;
  
  /// 医生姓名
  final String doctorName;
  
  /// 会话类型
  final TelemedicineType type;
  
  /// 预约ID
  final String appointmentId;
  
  /// 会话状态
  final String status;
  
  /// 开始时间
  final DateTime? startTime;
  
  /// 结束时间
  final DateTime? endTime;
  
  /// 会话时长（分钟）
  final int? durationMinutes;
  
  /// 会话URL
  final String? sessionUrl;
  
  /// 聊天记录
  final List<Map<String, dynamic>>? chatHistory;
  
  /// 会话笔记
  final String? sessionNotes;
  
  /// 诊断结果
  final List<String>? diagnosis;
  
  /// 建议
  final String? recommendations;
  
  /// 处方ID
  final String? prescriptionId;
  
  /// 医生评分（1-5）
  final int? doctorRating;
  
  /// 用户评分（1-5）
  final int? userRating;
  
  /// 用户反馈
  final String? userFeedback;
  
  /// 创建时间
  final DateTime createdTime;
  
  /// 更新时间
  final DateTime updatedTime;
  
  const TelemedicineSession({
    required this.id,
    required this.userId,
    required this.doctorId,
    required this.doctorName,
    required this.type,
    required this.appointmentId,
    required this.status,
    this.startTime,
    this.endTime,
    this.durationMinutes,
    this.sessionUrl,
    this.chatHistory,
    this.sessionNotes,
    this.diagnosis,
    this.recommendations,
    this.prescriptionId,
    this.doctorRating,
    this.userRating,
    this.userFeedback,
    required this.createdTime,
    required this.updatedTime,
  });
  
  /// 从JSON创建
  factory TelemedicineSession.fromJson(Map<String, dynamic> json) {
    return TelemedicineSession(
      id: json['id'],
      userId: json['user_id'],
      doctorId: json['doctor_id'],
      doctorName: json['doctor_name'],
      type: TelemedicineType.values.firstWhere(
        (t) => t.toString() == 'TelemedicineType.${json['type']}',
        orElse: () => TelemedicineType.videoConsultation,
      ),
      appointmentId: json['appointment_id'],
      status: json['status'],
      startTime: json['start_time'] != null
        ? DateTime.parse(json['start_time'])
        : null,
      endTime: json['end_time'] != null
        ? DateTime.parse(json['end_time'])
        : null,
      durationMinutes: json['duration_minutes'],
      sessionUrl: json['session_url'],
      chatHistory: json['chat_history'] != null
        ? List<Map<String, dynamic>>.from(json['chat_history'].map(
            (m) => Map<String, dynamic>.from(m)))
        : null,
      sessionNotes: json['session_notes'],
      diagnosis: json['diagnosis'] != null
        ? List<String>.from(json['diagnosis'])
        : null,
      recommendations: json['recommendations'],
      prescriptionId: json['prescription_id'],
      doctorRating: json['doctor_rating'],
      userRating: json['user_rating'],
      userFeedback: json['user_feedback'],
      createdTime: DateTime.parse(json['created_time']),
      updatedTime: DateTime.parse(json['updated_time']),
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'doctor_id': doctorId,
      'doctor_name': doctorName,
      'type': type.toString().split('.').last,
      'appointment_id': appointmentId,
      'status': status,
      'start_time': startTime?.toIso8601String(),
      'end_time': endTime?.toIso8601String(),
      'duration_minutes': durationMinutes,
      'session_url': sessionUrl,
      'chat_history': chatHistory,
      'session_notes': sessionNotes,
      'diagnosis': diagnosis,
      'recommendations': recommendations,
      'prescription_id': prescriptionId,
      'doctor_rating': doctorRating,
      'user_rating': userRating,
      'user_feedback': userFeedback,
      'created_time': createdTime.toIso8601String(),
      'updated_time': updatedTime.toIso8601String(),
    };
  }
}

/// 医疗机构搜索过滤条件
class MedicalInstitutionFilter {
  /// 关键词
  final String? keyword;
  
  /// 省份
  final String? province;
  
  /// 城市
  final String? city;
  
  /// 区/县
  final String? district;
  
  /// 机构类型
  final List<MedicalInstitutionType>? types;
  
  /// 科室
  final List<MedicalDepartment>? departments;
  
  /// 评分下限（1-5）
  final double? minRating;
  
  /// 距离范围（公里）
  final double? maxDistance;
  
  /// 当前位置经度（用于计算距离）
  final double? currentLongitude;
  
  /// 当前位置纬度（用于计算距离）
  final double? currentLatitude;
  
  /// 是否支持医保
  final bool? isMedicalInsuranceDesignated;
  
  /// 是否支持远程医疗
  final bool? supportsTelemedicine;
  
  /// 是否支持在线预约
  final bool? supportsOnlineAppointment;
  
  const MedicalInstitutionFilter({
    this.keyword,
    this.province,
    this.city,
    this.district,
    this.types,
    this.departments,
    this.minRating,
    this.maxDistance,
    this.currentLongitude,
    this.currentLatitude,
    this.isMedicalInsuranceDesignated,
    this.supportsTelemedicine,
    this.supportsOnlineAppointment,
  });
  
  /// 转换为查询参数
  Map<String, dynamic> toQueryParams() {
    final params = <String, dynamic>{};
    
    if (keyword != null) params['keyword'] = keyword;
    if (province != null) params['province'] = province;
    if (city != null) params['city'] = city;
    if (district != null) params['district'] = district;
    
    if (types != null && types!.isNotEmpty) {
      params['types'] = types!.map((t) => t.toString().split('.').last).join(',');
    }
    
    if (departments != null && departments!.isNotEmpty) {
      params['departments'] = departments!.map((d) => d.toString().split('.').last).join(',');
    }
    
    if (minRating != null) params['min_rating'] = minRating.toString();
    if (maxDistance != null) params['max_distance'] = maxDistance.toString();
    if (currentLongitude != null) params['longitude'] = currentLongitude.toString();
    if (currentLatitude != null) params['latitude'] = currentLatitude.toString();
    if (isMedicalInsuranceDesignated != null) params['is_medical_insurance_designated'] = isMedicalInsuranceDesignated.toString();
    if (supportsTelemedicine != null) params['supports_telemedicine'] = supportsTelemedicine.toString();
    if (supportsOnlineAppointment != null) params['supports_online_appointment'] = supportsOnlineAppointment.toString();
    
    return params;
  }
}

/// 医生搜索过滤条件
class DoctorFilter {
  /// 关键词
  final String? keyword;
  
  /// 机构ID
  final String? institutionId;
  
  /// 科室
  final List<MedicalDepartment>? departments;
  
  /// 职称
  final List<DoctorTitle>? titles;
  
  /// 专长关键词
  final List<String>? specialtyKeywords;
  
  /// 评分下限（1-5）
  final double? minRating;
  
  /// 是否支持医保
  final bool? supportsMedicalInsurance;
  
  /// 是否支持远程医疗
  final bool? supportsTelemedicine;
  
  /// 可预约时间范围开始
  final DateTime? availableTimeStart;
  
  /// 可预约时间范围结束
  final DateTime? availableTimeEnd;
  
  /// 问诊费用上限
  final double? maxConsultationFee;
  
  const DoctorFilter({
    this.keyword,
    this.institutionId,
    this.departments,
    this.titles,
    this.specialtyKeywords,
    this.minRating,
    this.supportsMedicalInsurance,
    this.supportsTelemedicine,
    this.availableTimeStart,
    this.availableTimeEnd,
    this.maxConsultationFee,
  });
  
  /// 转换为查询参数
  Map<String, dynamic> toQueryParams() {
    final params = <String, dynamic>{};
    
    if (keyword != null) params['keyword'] = keyword;
    if (institutionId != null) params['institution_id'] = institutionId;
    
    if (departments != null && departments!.isNotEmpty) {
      params['departments'] = departments!.map((d) => d.toString().split('.').last).join(',');
    }
    
    if (titles != null && titles!.isNotEmpty) {
      params['titles'] = titles!.map((t) => t.toString().split('.').last).join(',');
    }
    
    if (specialtyKeywords != null && specialtyKeywords!.isNotEmpty) {
      params['specialty_keywords'] = specialtyKeywords!.join(',');
    }
    
    if (minRating != null) params['min_rating'] = minRating.toString();
    if (supportsMedicalInsurance != null) params['supports_medical_insurance'] = supportsMedicalInsurance.toString();
    if (supportsTelemedicine != null) params['supports_telemedicine'] = supportsTelemedicine.toString();
    
    if (availableTimeStart != null) params['available_time_start'] = availableTimeStart!.toIso8601String();
    if (availableTimeEnd != null) params['available_time_end'] = availableTimeEnd!.toIso8601String();
    if (maxConsultationFee != null) params['max_consultation_fee'] = maxConsultationFee.toString();
    
    return params;
  }
}

/// 食材属性（中医四性）
enum FoodProperty {
  /// 寒性
  cold,
  
  /// 凉性
  cool,
  
  /// 平性
  neutral,
  
  /// 温性
  warm,
  
  /// 热性
  hot,
}

/// 食材味道（中医五味）
enum FoodFlavor {
  /// 酸味
  sour,
  
  /// 苦味
  bitter,
  
  /// 甘味（甜）
  sweet,
  
  /// 辛味（辣）
  pungent,
  
  /// 咸味
  salty,
}

/// 食材功效分类
enum FoodTherapeuticEffect {
  /// 补气
  tonifyQi,
  
  /// 养血
  nourishBlood,
  
  /// 补阴
  tonifyYin,
  
  /// 补阳
  tonifyYang,
  
  /// 祛风
  dispelWind,
  
  /// 清热
  clearHeat,
  
  /// 祛湿
  removeDampness,
  
  /// 化痰
  resolvePhlegm,
  
  /// 理气
  regulateQi,
  
  /// 活血
  activateBlood,
  
  /// 消食
  digestFood,
  
  /// 安神
  calmMind,
  
  /// 明目
  benefitEyes,
  
  /// 润肺
  moistenLungs,
  
  /// 健脾
  strengthenSpleen,
  
  /// 补肾
  tonifyKidney,
  
  /// 护肝
  protectLiver,
  
  /// 益智
  enhanceBrain,
}

/// 中医体质分类
enum TraditionalChineseBodyType {
  /// 平和质
  balanced,
  
  /// 气虚质
  qiDeficiency,
  
  /// 阳虚质
  yangDeficiency,
  
  /// 阴虚质
  yinDeficiency,
  
  /// 痰湿质
  phlegmDampness,
  
  /// 湿热质
  dampnessHeat,
  
  /// 血瘀质
  bloodStasis,
  
  /// 气郁质
  qiStagnation,
  
  /// 特禀质
  allergic,
}

/// 处方类型
enum PrescriptionType {
  /// 药膳
  medicinalFood,
  
  /// 食疗
  dietTherapy,
  
  /// 药茶
  medicinalTea,
  
  /// 药酒
  medicinalWine,
  
  /// 药粥
  medicinalPorridge,
  
  /// 药汤
  medicinalSoup,
}

/// 膳食时段
enum MealTime {
  /// 早餐
  breakfast,
  
  /// 午餐
  lunch,
  
  /// 晚餐
  dinner,
  
  /// 加餐
  snack,
}

/// 药食同源食材
class MedicinalFood {
  /// 食材ID
  final String id;
  
  /// 中文名称
  final String chineseName;
  
  /// 英文名称
  final String? englishName;
  
  /// 拼音
  final String? pinyin;
  
  /// 别名列表
  final List<String>? aliases;
  
  /// 食材分类
  final List<String> categories;
  
  /// 食材属性（四性）
  final FoodProperty property;
  
  /// 食材味道（五味）
  final List<FoodFlavor> flavors;
  
  /// 归经
  final List<String> meridians;
  
  /// 功效列表
  final List<FoodTherapeuticEffect> effects;
  
  /// 功效描述
  final String efficacyDescription;
  
  /// 宜用人群
  final List<String> suitableFor;
  
  /// 禁忌人群
  final List<String> contraindicatedFor;
  
  /// 用法用量
  final String? usageGuideline;
  
  /// 现代研究
  final String? modernResearch;
  
  /// 常用搭配
  final List<String>? commonCombinations;
  
  /// 相关方剂
  final List<String>? relatedPrescriptions;
  
  /// 图片URL列表
  final List<String>? imageUrls;
  
  /// 食材来源
  final String? source;
  
  /// 价格（人民币，元/kg）
  final double? price;
  
  /// 营养成分
  final Map<String, dynamic>? nutrition;
  
  /// 相关文献引用
  final List<String>? references;

  const MedicinalFood({
    required this.id,
    required this.chineseName,
    this.englishName,
    this.pinyin,
    this.aliases,
    required this.categories,
    required this.property,
    required this.flavors,
    required this.meridians,
    required this.effects,
    required this.efficacyDescription,
    required this.suitableFor,
    required this.contraindicatedFor,
    this.usageGuideline,
    this.modernResearch,
    this.commonCombinations,
    this.relatedPrescriptions,
    this.imageUrls,
    this.source,
    this.price,
    this.nutrition,
    this.references,
  });
  
  /// 从JSON创建
  factory MedicinalFood.fromJson(Map<String, dynamic> json) {
    return MedicinalFood(
      id: json['id'],
      chineseName: json['chinese_name'],
      englishName: json['english_name'],
      pinyin: json['pinyin'],
      aliases: json['aliases'] != null 
        ? List<String>.from(json['aliases']) 
        : null,
      categories: List<String>.from(json['categories']),
      property: FoodProperty.values.firstWhere(
        (p) => p.toString() == 'FoodProperty.${json['property']}',
        orElse: () => FoodProperty.neutral,
      ),
      flavors: (json['flavors'] as List).map((f) => 
        FoodFlavor.values.firstWhere(
          (fl) => fl.toString() == 'FoodFlavor.$f',
          orElse: () => FoodFlavor.sweet,
        )
      ).toList(),
      meridians: List<String>.from(json['meridians']),
      effects: (json['effects'] as List).map((e) => 
        FoodTherapeuticEffect.values.firstWhere(
          (ef) => ef.toString() == 'FoodTherapeuticEffect.$e',
          orElse: () => FoodTherapeuticEffect.tonifyQi,
        )
      ).toList(),
      efficacyDescription: json['efficacy_description'],
      suitableFor: List<String>.from(json['suitable_for']),
      contraindicatedFor: List<String>.from(json['contraindicated_for']),
      usageGuideline: json['usage_guideline'],
      modernResearch: json['modern_research'],
      commonCombinations: json['common_combinations'] != null 
        ? List<String>.from(json['common_combinations']) 
        : null,
      relatedPrescriptions: json['related_prescriptions'] != null 
        ? List<String>.from(json['related_prescriptions']) 
        : null,
      imageUrls: json['image_urls'] != null 
        ? List<String>.from(json['image_urls']) 
        : null,
      source: json['source'],
      price: json['price']?.toDouble(),
      nutrition: json['nutrition'],
      references: json['references'] != null 
        ? List<String>.from(json['references']) 
        : null,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'chinese_name': chineseName,
      'english_name': englishName,
      'pinyin': pinyin,
      'aliases': aliases,
      'categories': categories,
      'property': property.toString().split('.').last,
      'flavors': flavors.map((f) => f.toString().split('.').last).toList(),
      'meridians': meridians,
      'effects': effects.map((e) => e.toString().split('.').last).toList(),
      'efficacy_description': efficacyDescription,
      'suitable_for': suitableFor,
      'contraindicated_for': contraindicatedFor,
      'usage_guideline': usageGuideline,
      'modern_research': modernResearch,
      'common_combinations': commonCombinations,
      'related_prescriptions': relatedPrescriptions,
      'image_urls': imageUrls,
      'source': source,
      'price': price,
      'nutrition': nutrition,
      'references': references,
    };
  }
}

/// 药膳配方
class MedicinalRecipe {
  /// 配方ID
  final String id;
  
  /// 配方名称
  final String name;
  
  /// 处方类型
  final PrescriptionType type;
  
  /// 配方食材列表
  final List<RecipeIngredient> ingredients;
  
  /// 制作方法
  final String preparation;
  
  /// 食用方法
  final String? consumptionMethod;
  
  /// 推荐食用时间
  final List<MealTime>? recommendedMealTimes;
  
  /// 功效描述
  final String efficacyDescription;
  
  /// 主治
  final List<String> mainIndications;
  
  /// 宜用人群
  final List<String> suitableFor;
  
  /// 禁忌人群
  final List<String> contraindicatedFor;
  
  /// 相关中医理论
  final String? tcmTheoryBackground;
  
  /// 图片URL列表
  final List<String>? imageUrls;
  
  /// 视频URL
  final String? videoUrl;
  
  /// 适用体质
  final List<TraditionalChineseBodyType>? suitableBodyTypes;
  
  /// 来源/出处
  final String? source;
  
  /// 难度级别（1-5）
  final int? difficultyLevel;
  
  /// 准备时间（分钟）
  final int? prepTime;
  
  /// 烹饪时间（分钟）
  final int? cookTime;
  
  /// 评分（1-5）
  final double? rating;
  
  /// 评论数
  final int? reviewCount;
  
  /// 相关文献引用
  final List<String>? references;

  const MedicinalRecipe({
    required this.id,
    required this.name,
    required this.type,
    required this.ingredients,
    required this.preparation,
    this.consumptionMethod,
    this.recommendedMealTimes,
    required this.efficacyDescription,
    required this.mainIndications,
    required this.suitableFor,
    required this.contraindicatedFor,
    this.tcmTheoryBackground,
    this.imageUrls,
    this.videoUrl,
    this.suitableBodyTypes,
    this.source,
    this.difficultyLevel,
    this.prepTime,
    this.cookTime,
    this.rating,
    this.reviewCount,
    this.references,
  });
  
  /// 从JSON创建
  factory MedicinalRecipe.fromJson(Map<String, dynamic> json) {
    return MedicinalRecipe(
      id: json['id'],
      name: json['name'],
      type: PrescriptionType.values.firstWhere(
        (t) => t.toString() == 'PrescriptionType.${json['type']}',
        orElse: () => PrescriptionType.medicinalFood,
      ),
      ingredients: (json['ingredients'] as List).map(
        (i) => RecipeIngredient.fromJson(i)
      ).toList(),
      preparation: json['preparation'],
      consumptionMethod: json['consumption_method'],
      recommendedMealTimes: json['recommended_meal_times'] != null 
        ? (json['recommended_meal_times'] as List).map((m) => 
            MealTime.values.firstWhere(
              (mt) => mt.toString() == 'MealTime.$m',
              orElse: () => MealTime.lunch,
            )
          ).toList() 
        : null,
      efficacyDescription: json['efficacy_description'],
      mainIndications: List<String>.from(json['main_indications']),
      suitableFor: List<String>.from(json['suitable_for']),
      contraindicatedFor: List<String>.from(json['contraindicated_for']),
      tcmTheoryBackground: json['tcm_theory_background'],
      imageUrls: json['image_urls'] != null 
        ? List<String>.from(json['image_urls']) 
        : null,
      videoUrl: json['video_url'],
      suitableBodyTypes: json['suitable_body_types'] != null 
        ? (json['suitable_body_types'] as List).map((b) => 
            TraditionalChineseBodyType.values.firstWhere(
              (bt) => bt.toString() == 'TraditionalChineseBodyType.$b',
              orElse: () => TraditionalChineseBodyType.balanced,
            )
          ).toList() 
        : null,
      source: json['source'],
      difficultyLevel: json['difficulty_level'],
      prepTime: json['prep_time'],
      cookTime: json['cook_time'],
      rating: json['rating']?.toDouble(),
      reviewCount: json['review_count'],
      references: json['references'] != null 
        ? List<String>.from(json['references']) 
        : null,
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'type': type.toString().split('.').last,
      'ingredients': ingredients.map((i) => i.toJson()).toList(),
      'preparation': preparation,
      'consumption_method': consumptionMethod,
      'recommended_meal_times': recommendedMealTimes?.map(
        (m) => m.toString().split('.').last
      ).toList(),
      'efficacy_description': efficacyDescription,
      'main_indications': mainIndications,
      'suitable_for': suitableFor,
      'contraindicated_for': contraindicatedFor,
      'tcm_theory_background': tcmTheoryBackground,
      'image_urls': imageUrls,
      'video_url': videoUrl,
      'suitable_body_types': suitableBodyTypes?.map(
        (b) => b.toString().split('.').last
      ).toList(),
      'source': source,
      'difficulty_level': difficultyLevel,
      'prep_time': prepTime,
      'cook_time': cookTime,
      'rating': rating,
      'review_count': reviewCount,
      'references': references,
    };
  }
}

/// 配方食材
class RecipeIngredient {
  /// 食材ID
  final String foodId;
  
  /// 食材名称
  final String name;
  
  /// 用量
  final String amount;
  
  /// 药用部位
  final String? medicinalPart;
  
  /// 处理方法
  final String? processingMethod;
  
  /// 是否必需
  final bool isRequired;
  
  /// 在配方中的功效
  final String? roleInRecipe;
  
  const RecipeIngredient({
    required this.foodId,
    required this.name,
    required this.amount,
    this.medicinalPart,
    this.processingMethod,
    this.isRequired = true,
    this.roleInRecipe,
  });
  
  /// 从JSON创建
  factory RecipeIngredient.fromJson(Map<String, dynamic> json) {
    return RecipeIngredient(
      foodId: json['food_id'],
      name: json['name'],
      amount: json['amount'],
      medicinalPart: json['medicinal_part'],
      processingMethod: json['processing_method'],
      isRequired: json['is_required'] ?? true,
      roleInRecipe: json['role_in_recipe'],
    );
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'food_id': foodId,
      'name': name,
      'amount': amount,
      'medicinal_part': medicinalPart,
      'processing_method': processingMethod,
      'is_required': isRequired,
      'role_in_recipe': roleInRecipe,
    };
  }
}

/// 食材搜索过滤条件
class MedicinalFoodFilter {
  /// 关键词
  final String? keyword;
  
  /// 功效列表
  final List<FoodTherapeuticEffect>? effects;
  
  /// 食材属性
  final List<FoodProperty>? properties;
  
  /// 食材味道
  final List<FoodFlavor>? flavors;
  
  /// 归经
  final List<String>? meridians;
  
  /// 适用体质
  final List<TraditionalChineseBodyType>? suitableBodyTypes;
  
  /// 健康状况关键词
  final List<String>? healthConditions;
  
  /// 分类
  final List<String>? categories;
  
  /// 价格范围
  final RangeValues? priceRange;
  
  const MedicinalFoodFilter({
    this.keyword,
    this.effects,
    this.properties,
    this.flavors,
    this.meridians,
    this.suitableBodyTypes,
    this.healthConditions,
    this.categories,
    this.priceRange,
  });
}

/// 价格范围
class RangeValues {
  final double start;
  final double end;
  
  const RangeValues(this.start, this.end);
}

/// 食疗方案
class DietTherapyPlan {
  /// 方案ID
  final String id;
  
  /// 方案名称
  final String name;
  
  /// 方案描述
  final String description;
  
  /// 目标健康状况
  final List<String> targetHealthConditions;
  
  /// 适用体质
  final List<TraditionalChineseBodyType> suitableBodyTypes;
  
  /// 推荐食材列表
  final List<MedicinalFood> recommendedFoods;
  
  /// 避免食材列表
  final List<MedicinalFood> avoidFoods;
  
  /// 推荐配方列表
  final List<MedicinalRecipe> recommendedRecipes;
  
  /// 每周食谱安排
  final Map<String, List<MedicinalRecipe>>? weeklyMealPlan;
  
  /// 中医理论依据
  final String tcmTheoryBasis;
  
  /// 注意事项
  final List<String> precautions;
  
  /// 预期效果
  final String expectedOutcomes;
  
  /// 方案周期（天）
  final int durationDays;
  
  /// 创建时间
  final DateTime createdAt;
  
  /// 更新时间
  final DateTime updatedAt;
  
  /// 创建者
  final String createdBy;
  
  const DietTherapyPlan({
    required this.id,
    required this.name,
    required this.description,
    required this.targetHealthConditions,
    required this.suitableBodyTypes,
    required this.recommendedFoods,
    required this.avoidFoods,
    required this.recommendedRecipes,
    this.weeklyMealPlan,
    required this.tcmTheoryBasis,
    required this.precautions,
    required this.expectedOutcomes,
    required this.durationDays,
    required this.createdAt,
    required this.updatedAt,
    required this.createdBy,
  });
}

/// 食材分析结果
class FoodAnalysisResult {
  /// 食材
  final MedicinalFood food;
  
  /// 适合当前用户体质的评分（0-100）
  final int bodyTypeCompatibilityScore;
  
  /// 适合当前季节的评分（0-100）
  final int seasonalCompatibilityScore;
  
  /// 适合当前健康状况的评分（0-100）
  final int healthConditionCompatibilityScore;
  
  /// 总体推荐度（0-100）
  final int overallRecommendationScore;
  
  /// 推荐理由
  final List<String> recommendationReasons;
  
  /// 注意事项
  final List<String>? precautions;
  
  /// 建议用法
  final String? suggestedUsage;
  
  /// 推荐搭配
  final List<MedicinalFood>? recommendedCombinations;
  
  const FoodAnalysisResult({
    required this.food,
    required this.bodyTypeCompatibilityScore,
    required this.seasonalCompatibilityScore,
    required this.healthConditionCompatibilityScore,
    required this.overallRecommendationScore,
    required this.recommendationReasons,
    this.precautions,
    this.suggestedUsage,
    this.recommendedCombinations,
  });
}

/// 药食同源代理接口
abstract class MedicinalFoodAgent {
  /// 根据条件搜索药食同源食材
  Future<List<MedicinalFood>> searchMedicinalFoods(MedicinalFoodFilter filter);
  
  /// 获取食材详情
  Future<MedicinalFood?> getFoodDetail(String foodId);
  
  /// 根据健康状况获取推荐食材
  Future<List<FoodAnalysisResult>> getRecommendedFoodsForHealthConditions(
    List<String> healthConditions, {
    TraditionalChineseBodyType? bodyType,
    String? userId,
  });
  
  /// 根据体质获取推荐食材
  Future<List<MedicinalFood>> getRecommendedFoodsForBodyType(
    TraditionalChineseBodyType bodyType,
  );
  
  /// 搜索药膳配方
  Future<List<MedicinalRecipe>> searchRecipes({
    String? keyword,
    List<String>? healthConditions,
    List<FoodTherapeuticEffect>? effects,
    PrescriptionType? type,
    TraditionalChineseBodyType? bodyType,
  });
  
  /// 获取配方详情
  Future<MedicinalRecipe?> getRecipeDetail(String recipeId);
  
  /// 创建个性化食疗方案
  Future<DietTherapyPlan> createPersonalizedDietPlan({
    required String userId,
    required List<String> healthConditions,
    required TraditionalChineseBodyType bodyType,
    int durationDays = 28,
  });
  
  /// 分析食材的药用价值
  Future<FoodAnalysisResult> analyzeFoodMedicinalValue(
    String foodId, {
    String? userId,
    List<String>? userHealthConditions,
    TraditionalChineseBodyType? userBodyType,
  });
  
  /// 获取季节性养生食材
  Future<List<MedicinalFood>> getSeasonalHealthFoods();
  
  /// 获取针对特定脏腑的食材
  Future<List<MedicinalFood>> getFoodsForOrgan(String organName);
  
  /// 获取相互作用（食材相克）信息
  Future<List<Map<String, dynamic>>> getFoodInteractions(List<String> foodIds);
  
  /// 获取常见体质调理方案
  Future<Map<TraditionalChineseBodyType, List<String>>> getBodyTypeAdjustmentGuidelines();
}

/// 药食同源代理实现
class MedicinalFoodAgentImpl implements MedicinalFoodAgent {
  final AIAgent _aiAgent;
  final ServiceIntegration _serviceIntegration;
  final AgentMicrokernel _microkernel;
  final SecurityPrivacyFramework _securityFramework;
  final KnowledgeGraphAgent? _knowledgeGraphAgent;
  final HealthManagementAgent? _healthManagementAgent;
  final AutonomousLearningSystem _learningSystem;
  
  MedicinalFoodAgentImpl({
    required AIAgent aiAgent,
    required ServiceIntegration serviceIntegration,
    required AgentMicrokernel microkernel,
    required SecurityPrivacyFramework securityFramework,
    required AutonomousLearningSystem learningSystem,
    this.knowledgeGraphAgentId,
    this.healthManagementAgentId,
  }) : _aiAgent = aiAgent,
       _serviceIntegration = serviceIntegration,
       _microkernel = microkernel,
       _securityFramework = securityFramework,
       _learningSystem = learningSystem,
       _knowledgeGraphAgent = null,
       _healthManagementAgent = null;
  
  /// 知识图谱代理ID（可选）
  final String? knowledgeGraphAgentId;
  
  /// 健康管理代理ID（可选）
  final String? healthManagementAgentId;
  
  /// 初始化
  Future<void> initialize() async {
    // 注册接收消息的处理函数
    _microkernel.registerAgent(_aiAgent.id, _handleMessage);
    
    // 如果提供了知识图谱代理ID，建立通信
    if (knowledgeGraphAgentId != null) {
      final initMessage = AgentMessage(
        senderId: _aiAgent.id,
        receiverId: knowledgeGraphAgentId!,
        type: AgentMessageType.query,
        content: {
          'action': 'register_callback',
          'callback_agent_id': _aiAgent.id,
        },
      );
      
      await _microkernel.sendMessage(initMessage);
    }
    
    // 如果提供了健康管理代理ID，建立通信
    if (healthManagementAgentId != null) {
      final initMessage = AgentMessage(
        senderId: _aiAgent.id,
        receiverId: healthManagementAgentId!,
        type: AgentMessageType.query,
        content: {
          'action': 'register_callback',
          'callback_agent_id': _aiAgent.id,
        },
      );
      
      await _microkernel.sendMessage(initMessage);
    }
  }
  
  /// 处理接收到的消息
  Future<void> _handleMessage(AgentMessage message) async {
    try {
      final action = message.content['action'] as String?;
      
      if (action == null) {
        return;
      }
      
      switch (action) {
        case 'health_update':
          final healthData = message.content['health_data'];
          if (healthData != null) {
            // 处理健康数据更新
            _processHealthUpdate(healthData);
          }
          break;
          
        case 'knowledge_update':
          final knowledgeData = message.content['knowledge_data'];
          if (knowledgeData != null) {
            // 处理知识图谱更新
            _processKnowledgeUpdate(knowledgeData);
          }
          break;
          
        default:
          // 无法识别的动作
          break;
      }
      
      // 如果消息需要响应，发送响应
      if (message.requiresResponse) {
        final responseMessage = message.createResponse(
          responderId: _aiAgent.id,
          responseContent: {
            'success': true,
            'message': 'Message processed successfully',
          },
        );
        
        await _microkernel.sendMessage(responseMessage);
      }
      
    } catch (e) {
      print('Error handling message: $e');
      
      // 如果消息需要响应，发送错误响应
      if (message.requiresResponse) {
        final errorResponse = message.createResponse(
          responderId: _aiAgent.id,
          responseContent: {
            'success': false,
            'error': e.toString(),
          },
        );
        
        await _microkernel.sendMessage(errorResponse);
      }
    }
  }
  
  /// 处理健康数据更新
  void _processHealthUpdate(Map<String, dynamic> healthData) {
    // 实现健康数据更新的处理逻辑
    // 例如缓存用户的健康状况，以便在推荐药食同源食材时使用
  }
  
  /// 处理知识图谱更新
  void _processKnowledgeUpdate(Map<String, dynamic> knowledgeData) {
    // 实现知识图谱更新的处理逻辑
    // 例如更新食材之间的关系、功效等信息
  }
  
  @override
  Future<List<MedicinalFood>> searchMedicinalFoods(MedicinalFoodFilter filter) async {
    try {
      // 构建查询参数
      final queryParams = <String, dynamic>{};
      
      if (filter.keyword != null) {
        queryParams['keyword'] = filter.keyword;
      }
      
      if (filter.effects != null && filter.effects!.isNotEmpty) {
        queryParams['effects'] = filter.effects!.map(
          (e) => e.toString().split('.').last
        ).join(',');
      }
      
      if (filter.properties != null && filter.properties!.isNotEmpty) {
        queryParams['properties'] = filter.properties!.map(
          (p) => p.toString().split('.').last
        ).join(',');
      }
      
      if (filter.flavors != null && filter.flavors!.isNotEmpty) {
        queryParams['flavors'] = filter.flavors!.map(
          (f) => f.toString().split('.').last
        ).join(',');
      }
      
      if (filter.meridians != null && filter.meridians!.isNotEmpty) {
        queryParams['meridians'] = filter.meridians!.join(',');
      }
      
      if (filter.suitableBodyTypes != null && filter.suitableBodyTypes!.isNotEmpty) {
        queryParams['suitable_body_types'] = filter.suitableBodyTypes!.map(
          (b) => b.toString().split('.').last
        ).join(',');
      }
      
      if (filter.healthConditions != null && filter.healthConditions!.isNotEmpty) {
        queryParams['health_conditions'] = filter.healthConditions!.join(',');
      }
      
      if (filter.categories != null && filter.categories!.isNotEmpty) {
        queryParams['categories'] = filter.categories!.join(',');
      }
      
      if (filter.priceRange != null) {
        queryParams['min_price'] = filter.priceRange!.start;
        queryParams['max_price'] = filter.priceRange!.end;
      }
      
      // 发送请求到服务
      final response = await _serviceIntegration.sendRequest<Map<String, dynamic>>(
        endpoint: '/api/medicinal-foods/search',
        method: 'GET',
        queryParams: queryParams,
      );
      
      if (!response.success || response.data == null) {
        return [];
      }
      
      final foodsData = response.data!['foods'] as List<dynamic>;
      final foods = foodsData.map(
        (data) => MedicinalFood.fromJson(data as Map<String, dynamic>)
      ).toList();
      
      // 收集学习数据
      await _learningSystem.collectData(LearningDataItem(
        id: 'search_${DateTime.now().millisecondsSinceEpoch}',
        type: LearningDataType.userInteraction,
        source: LearningDataSource.medicinalFoodAgent,
        content: {
          'action': 'search_foods',
          'filter': queryParams,
          'results_count': foods.length,
        },
        timestamp: DateTime.now(),
      ));
      
      return foods;
    } catch (e) {
      print('Error searching medicinal foods: $e');
      return [];
    }
  }
  
  @override
  Future<MedicinalFood?> getFoodDetail(String foodId) async {
    try {
      // 首先尝试从知识图谱获取更丰富的数据
      if (knowledgeGraphAgentId != null) {
        final graphQueryMessage = AgentMessage(
          senderId: _aiAgent.id,
          receiverId: knowledgeGraphAgentId!,
          type: AgentMessageType.query,
          content: {
            'action': 'get_node_details',
            'node_id': foodId,
            'node_type': 'medicinal_food',
          },
          requiresResponse: true,
        );
        
        final messageId = await _microkernel.sendMessage(graphQueryMessage);
        
        // 等待响应，实际实现中应该使用异步回调机制
        // 这里简化处理
        await Future.delayed(const Duration(milliseconds: 500));
        
        // 获取响应消息
        final responses = _microkernel.getAgentMessageHistory(
          agentId: _aiAgent.id,
          type: AgentMessageType.response,
        ).where((msg) => msg.parentMessageId == messageId).toList();
        
        if (responses.isNotEmpty && responses.first.content['success'] == true) {
          final nodeData = responses.first.content['node_data'];
          if (nodeData != null) {
            return MedicinalFood.fromJson(nodeData);
          }
        }
      }
      
      // 如果从知识图谱未获取到，则从API获取
      final response = await _serviceIntegration.sendRequest<Map<String, dynamic>>(
        endpoint: '/api/medicinal-foods/$foodId',
        method: 'GET',
      );
      
      if (!response.success || response.data == null) {
        return null;
      }
      
      return MedicinalFood.fromJson(response.data!);
    } catch (e) {
      print('Error getting food detail: $e');
      return null;
    }
  }
  
  @override
  Future<List<FoodAnalysisResult>> getRecommendedFoodsForHealthConditions(
    List<String> healthConditions, {
    TraditionalChineseBodyType? bodyType,
    String? userId,
  }) async {
    try {
      // 构建查询参数
      final queryParams = <String, dynamic>{
        'health_conditions': healthConditions.join(','),
      };
      
      if (bodyType != null) {
        queryParams['body_type'] = bodyType.toString().split('.').last;
      }
      
      if (userId != null) {
        queryParams['user_id'] = userId;
        
        // 如果有健康管理代理，获取用户的更多健康数据
        if (healthManagementAgentId != null) {
          final healthDataMessage = AgentMessage(
            senderId: _aiAgent.id,
            receiverId: healthManagementAgentId!,
            type: AgentMessageType.query,
            content: {
              'action': 'get_user_health_data',
              'user_id': userId,
            },
            requiresResponse: true,
          );
          
          final messageId = await _microkernel.sendMessage(healthDataMessage);
          
          // 等待响应，实际实现中应该使用异步回调机制
          await Future.delayed(const Duration(milliseconds: 500));
          
          // 获取响应消息
          final responses = _microkernel.getAgentMessageHistory(
            agentId: _aiAgent.id,
            type: AgentMessageType.response,
          ).where((msg) => msg.parentMessageId == messageId).toList();
          
          if (responses.isNotEmpty && responses.first.content['success'] == true) {
            final userData = responses.first.content['user_data'];
            if (userData != null) {
              // 处理用户健康数据
              _processUserHealthData(userData);
            }
          }
        }
      }
      
      // 发送请求到服务
      final response = await _serviceIntegration.sendRequest<Map<String, dynamic>>(
        endpoint: '/api/medicinal-foods/recommend',
        method: 'POST',
        requestBody: queryParams,
      );
      
      if (!response.success || response.data == null) {
        return [];
      }
      
      final foodsData = response.data!['foods'] as List<dynamic>;
      final foods = foodsData.map(
        (data) => FoodAnalysisResult(
          food: MedicinalFood.fromJson(data as Map<String, dynamic>),
          bodyTypeCompatibilityScore: 0,
          seasonalCompatibilityScore: 0,
          healthConditionCompatibilityScore: 0,
          overallRecommendationScore: 0,
          recommendationReasons: [],
          precautions: null,
          suggestedUsage: null,
          recommendedCombinations: null,
        )
      ).toList();
      
      // 收集学习数据
      await _learningSystem.collectData(LearningDataItem(
        id: 'recommend_${DateTime.now().millisecondsSinceEpoch}',
        type: LearningDataType.userInteraction,
        source: LearningDataSource.medicinalFoodAgent,
        content: {
          'action': 'recommend_foods',
          'filter': queryParams,
          'results_count': foods.length,
        },
        timestamp: DateTime.now(),
      ));
      
      return foods;
    } catch (e) {
      print('Error recommending foods: $e');
      return [];
    }
  }
  
  void _processUserHealthData(Map<String, dynamic> userData) {
    // 实现处理用户健康数据的逻辑
  }
  
  @override
  Future<List<MedicinalFood>> getRecommendedFoodsForBodyType(
    TraditionalChineseBodyType bodyType,
  ) async {
    // 实现根据体质获取推荐食材的逻辑
    return [];
  }
  
  @override
  Future<List<MedicinalRecipe>> searchRecipes({
    String? keyword,
    List<String>? healthConditions,
    List<FoodTherapeuticEffect>? effects,
    PrescriptionType? type,
    TraditionalChineseBodyType? bodyType,
  }) async {
    // 实现搜索药膳配方的逻辑
    return [];
  }
  
  @override
  Future<MedicinalRecipe?> getRecipeDetail(String recipeId) async {
    // 实现获取配方详情的逻辑
    return null;
  }
  
  @override
  Future<DietTherapyPlan> createPersonalizedDietPlan({
    required String userId,
    required List<String> healthConditions,
    required TraditionalChineseBodyType bodyType,
    int durationDays = 28,
  }) async {
    // 实现创建个性化食疗方案的逻辑
    return DietTherapyPlan(
      id: '',
      name: '',
      description: '',
      targetHealthConditions: [],
      suitableBodyTypes: [],
      recommendedFoods: [],
      avoidFoods: [],
      recommendedRecipes: [],
      weeklyMealPlan: null,
      tcmTheoryBasis: '',
      precautions: [],
      expectedOutcomes: '',
      durationDays: 0,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
      createdBy: '',
    );
  }
  
  @override
  Future<FoodAnalysisResult> analyzeFoodMedicinalValue(
    String foodId, {
    String? userId,
    List<String>? userHealthConditions,
    TraditionalChineseBodyType? userBodyType,
  }) async {
    // 实现分析食材药用价值的逻辑
    return FoodAnalysisResult(
      food: MedicinalFood(
        id: '',
        chineseName: '',
        englishName: null,
        pinyin: null,
        aliases: null,
        categories: [],
        property: FoodProperty.neutral,
        flavors: [],
        meridians: [],
        effects: [],
        efficacyDescription: '',
        suitableFor: [],
        contraindicatedFor: [],
        usageGuideline: null,
        modernResearch: null,
        commonCombinations: null,
        relatedPrescriptions: null,
        imageUrls: null,
        source: null,
        price: null,
        nutrition: null,
        references: null,
      ),
      bodyTypeCompatibilityScore: 0,
      seasonalCompatibilityScore: 0,
      healthConditionCompatibilityScore: 0,
      overallRecommendationScore: 0,
      recommendationReasons: [],
      precautions: null,
      suggestedUsage: null,
      recommendedCombinations: null,
    );
  }
  
  @override
  Future<List<MedicinalFood>> getSeasonalHealthFoods() async {
    // 实现获取季节性养生食材的逻辑
    return [];
  }
  
  @override
  Future<List<MedicinalFood>> getFoodsForOrgan(String organName) async {
    // 实现获取针对特定脏腑的食材的逻辑
    return [];
  }
  
  @override
  Future<List<Map<String, dynamic>>> getFoodInteractions(List<String> foodIds) async {
    // 实现获取食材相互作用信息的逻辑
    return [];
  }
  
  @override
  Future<Map<TraditionalChineseBodyType, List<String>>> getBodyTypeAdjustmentGuidelines() async {
    // 实现获取常见体质调理方案的逻辑
    return {};
  }
}

/// 医疗服务API接口
/// 提供医疗服务相关的接口调用，包括预约挂号、获取医疗机构信息、远程问诊等功能
abstract class MedicalServiceAPI {
  /// 获取医疗机构列表
  Future<List<MedicalInstitution>> getMedicalInstitutions({
    String? name,
    MedicalInstitutionType? type,
    String? location,
    int? distance,
    bool? hasOnlineService,
  });
  
  /// 获取医疗机构详情
  Future<MedicalInstitution?> getMedicalInstitutionDetail(String institutionId);
  
  /// 获取医生列表
  Future<List<Doctor>> getDoctors({
    String? institutionId,
    MedicalDepartment? department,
    DoctorTitle? title,
    String? name,
    double? minRating,
  });
  
  /// 获取医生详情
  Future<Doctor?> getDoctorDetail(String doctorId);
  
  /// 获取可预约时间段
  Future<List<AvailableTimeSlot>> getAvailableTimeSlots({
    required String doctorId,
    required DateTime startDate,
    required DateTime endDate,
  });
  
  /// 创建预约
  Future<Appointment?> createAppointment({
    required String userId,
    required String doctorId,
    required String institutionId,
    required DateTime appointmentTime,
    required String purpose,
    required bool isFirstVisit,
    PaymentMethod? paymentMethod,
    String? insuranceId,
    List<String>? attachmentUrls,
  });
  
  /// 获取用户预约列表
  Future<List<Appointment>> getUserAppointments({
    required String userId,
    AppointmentStatus? status,
    DateTime? startDate,
    DateTime? endDate,
  });
  
  /// 取消预约
  Future<bool> cancelAppointment({
    required String appointmentId,
    required String cancelReason,
  });
  
  /// 重新安排预约
  Future<Appointment?> rescheduleAppointment({
    required String appointmentId,
    required DateTime newAppointmentTime,
  });
  
  /// 创建远程问诊
  Future<TelemedicineSession?> createTelemedicineSession({
    required String userId,
    required String doctorId,
    required TelemedicineType type,
    required String description,
    List<String>? attachmentUrls,
    PaymentMethod? paymentMethod,
  });
  
  /// 获取用户的远程问诊记录
  Future<List<TelemedicineSession>> getUserTelemedicineSessions({
    required String userId,
    TelemedicineStatus? status,
    DateTime? startDate,
    DateTime? endDate,
  });
  
  /// 结束远程问诊会话
  Future<bool> endTelemedicineSession({
    required String sessionId,
  });
  
  /// 评价医疗服务
  Future<bool> rateHealthcareService({
    required String serviceId,
    required ServiceType serviceType,
    required double rating,
    String? comment,
    Map<String, double>? detailedRatings,
  });
  
  /// 获取用户的医疗记录
  Future<List<MedicalRecord>> getUserMedicalRecords({
    required String userId,
    DateTime? startDate,
    DateTime? endDate,
    RecordType? type,
  });
  
  /// 上传医疗文档
  Future<String?> uploadMedicalDocument({
    required String userId,
    required Uint8List fileData,
    required String fileName,
    required String fileType,
    required RecordType documentType,
    String? description,
    DateTime? documentDate,
  });
  
  /// 获取医保信息
  Future<InsuranceInfo?> getInsuranceInfo({
    required String userId,
  });
  
  /// 查询医保待遇
  Future<List<InsuranceCoverage>> queryInsuranceCoverage({
    required String userId,
    String? treatmentType,
    String? medicineName,
  });
  
  /// 获取附近药店
  Future<List<Pharmacy>> getNearbyPharmacies({
    required double latitude,
    required double longitude,
    required int radiusInKm,
    bool? has24HourService,
    bool? hasDeliveryService,
  });
  
  /// 获取药品信息
  Future<Medicine?> getMedicineInfo({
    String? medicineId,
    String? medicineName,
  });
  
  /// 检查药品相互作用
  Future<List<MedicineInteraction>> checkMedicineInteractions({
    required List<String> medicineIds,
  });
  
  /// 获取健康教育内容
  Future<List<HealthEducationContent>> getHealthEducationContents({
    String? category,
    String? keyword,
    int? limit,
    int? offset,
  });
  
  /// 获取线下健康活动
  Future<List<HealthActivity>> getOfflineHealthActivities({
    required double latitude,
    required double longitude,
    required int radiusInKm,
    DateTime? startDate,
    DateTime? endDate,
    String? category,
  });
}

/// 医疗服务API实现类
class MedicalServiceAPIImpl implements MedicalServiceAPI {
  final ServiceIntegration _serviceIntegration;
  final SecurityPrivacyFramework _securityFramework;
  final AgentMicrokernel _agentMicrokernel;
  
  MedicalServiceAPIImpl({
    required ServiceIntegration serviceIntegration,
    required SecurityPrivacyFramework securityFramework,
    required AgentMicrokernel agentMicrokernel,
  }) : 
    _serviceIntegration = serviceIntegration,
    _securityFramework = securityFramework,
    _agentMicrokernel = agentMicrokernel;
    
  @override
  Future<List<MedicalInstitution>> getMedicalInstitutions({
    String? name,
    MedicalInstitutionType? type,
    String? location,
    int? distance,
    bool? hasOnlineService,
  }) async {
    try {
      // 构建请求参数
      final Map<String, dynamic> queryParams = {};
      if (name != null) queryParams['name'] = name;
      if (type != null) queryParams['type'] = type.toString().split('.').last;
      if (location != null) queryParams['location'] = location;
      if (distance != null) queryParams['distance'] = distance;
      if (hasOnlineService != null) queryParams['hasOnlineService'] = hasOnlineService;
      
      // 记录审计日志
      await _securityFramework.logSecurityAudit(
        operation: 'GET_MEDICAL_INSTITUTIONS',
        parameters: queryParams,
        agentId: 'MEDICAL_SERVICE_API',
      );
      
      // 发送API请求
      final response = await _serviceIntegration.sendRequest(
        'GET',
        '/api/medical/institutions',
        queryParams: queryParams,
      );
      
      // 解析响应数据
      final List<dynamic> data = response.data['institutions'] ?? [];
      return data.map((item) => MedicalInstitution.fromJson(item)).toList();
    } catch (e) {
      if (kDebugMode) {
        print('获取医疗机构列表失败: $e');
      }
      
      // 发送错误事件到Agent微内核
      _agentMicrokernel.publishEvent(
        AgentEvent(
          type: AgentEventType.error,
          source: 'MEDICAL_SERVICE_API',
          data: {
            'operation': 'getMedicalInstitutions',
            'error': e.toString(),
          },
        ),
      );
      
      return [];
    }
  }
  
  @override
  Future<MedicalInstitution?> getMedicalInstitutionDetail(String institutionId) async {
    try {
      // 记录审计日志
      await _securityFramework.logSecurityAudit(
        operation: 'GET_MEDICAL_INSTITUTION_DETAIL',
        parameters: {'institutionId': institutionId},
        agentId: 'MEDICAL_SERVICE_API',
      );
      
      // 发送API请求
      final response = await _serviceIntegration.sendRequest(
        'GET',
        '/api/medical/institutions/$institutionId',
      );
      
      // 解析响应数据
      return MedicalInstitution.fromJson(response.data);
    } catch (e) {
      if (kDebugMode) {
        print('获取医疗机构详情失败: $e');
      }
      
      // 发送错误事件到Agent微内核
      _agentMicrokernel.publishEvent(
        AgentEvent(
          type: AgentEventType.error,
          source: 'MEDICAL_SERVICE_API',
          data: {
            'operation': 'getMedicalInstitutionDetail',
            'institutionId': institutionId,
            'error': e.toString(),
          },
        ),
      );
      
      return null;
    }
  }
  
  @override
  Future<List<Doctor>> getDoctors({
    String? institutionId,
    MedicalDepartment? department,
    DoctorTitle? title,
    String? name,
    double? minRating,
  }) async {
    try {
      // 构建请求参数
      final Map<String, dynamic> queryParams = {};
      if (institutionId != null) queryParams['institutionId'] = institutionId;
      if (department != null) queryParams['department'] = department.toString().split('.').last;
      if (title != null) queryParams['title'] = title.toString().split('.').last;
      if (name != null) queryParams['name'] = name;
      if (minRating != null) queryParams['minRating'] = minRating;
      
      // 记录审计日志
      await _securityFramework.logSecurityAudit(
        operation: 'GET_DOCTORS',
        parameters: queryParams,
        agentId: 'MEDICAL_SERVICE_API',
      );
      
      // 发送API请求
      final response = await _serviceIntegration.sendRequest(
        'GET',
        '/api/medical/doctors',
        queryParams: queryParams,
      );
      
      // 解析响应数据
      final List<dynamic> data = response.data['doctors'] ?? [];
      return data.map((item) => Doctor.fromJson(item)).toList();
    } catch (e) {
      if (kDebugMode) {
        print('获取医生列表失败: $e');
      }
      
      // 发送错误事件到Agent微内核
      _agentMicrokernel.publishEvent(
        AgentEvent(
          type: AgentEventType.error,
          source: 'MEDICAL_SERVICE_API',
          data: {
            'operation': 'getDoctors',
            'error': e.toString(),
          },
        ),
      );
      
      return [];
    }
  }
  
  @override
  Future<Doctor?> getDoctorDetail(String doctorId) async {
    try {
      // 记录审计日志
      await _securityFramework.logSecurityAudit(
        operation: 'GET_DOCTOR_DETAIL',
        parameters: {'doctorId': doctorId},
        agentId: 'MEDICAL_SERVICE_API',
      );
      
      // 发送API请求
      final response = await _serviceIntegration.sendRequest(
        'GET',
        '/api/medical/doctors/$doctorId',
      );
      
      // 解析响应数据
      return Doctor.fromJson(response.data);
    } catch (e) {
      if (kDebugMode) {
        print('获取医生详情失败: $e');
      }
      
      // 发送错误事件到Agent微内核
      _agentMicrokernel.publishEvent(
        AgentEvent(
          type: AgentEventType.error,
          source: 'MEDICAL_SERVICE_API',
          data: {
            'operation': 'getDoctorDetail',
            'doctorId': doctorId,
            'error': e.toString(),
          },
        ),
      );
      
      return null;
    }
  }
  
  @override
  Future<List<AvailableTimeSlot>> getAvailableTimeSlots({
    required String doctorId,
    required DateTime startDate,
    required DateTime endDate,
  }) async {
    try {
      // 构建请求参数
      final Map<String, dynamic> queryParams = {
        'doctorId': doctorId,
        'startDate': startDate.toIso8601String(),
        'endDate': endDate.toIso8601String(),
      };
      
      // 记录审计日志
      await _securityFramework.logSecurityAudit(
        operation: 'GET_AVAILABLE_TIME_SLOTS',
        parameters: queryParams,
        agentId: 'MEDICAL_SERVICE_API',
      );
      
      // 发送API请求
      final response = await _serviceIntegration.sendRequest(
        'GET',
        '/api/medical/appointments/available-slots',
        queryParams: queryParams,
      );
      
      // 解析响应数据
      final List<dynamic> data = response.data['timeSlots'] ?? [];
      return data.map((item) => AvailableTimeSlot.fromJson(item)).toList();
    } catch (e) {
      if (kDebugMode) {
        print('获取可用时间段失败: $e');
      }
      
      // 发送错误事件到Agent微内核
      _agentMicrokernel.publishEvent(
        AgentEvent(
          type: AgentEventType.error,
          source: 'MEDICAL_SERVICE_API',
          data: {
            'operation': 'getAvailableTimeSlots',
            'doctorId': doctorId,
            'error': e.toString(),
          },
        ),
      );
      
      return [];
    }
  }
  
  @override
  Future<Appointment?> createAppointment({
    required String userId,
    required String doctorId,
    required String institutionId,
    required DateTime appointmentTime,
    required String purpose,
    required bool isFirstVisit,
    PaymentMethod? paymentMethod,
    String? insuranceId,
    List<String>? attachmentUrls,
  }) async {
    try {
      // 构建请求体
      final Map<String, dynamic> body = {
        'userId': userId,
        'doctorId': doctorId,
        'institutionId': institutionId,
        'appointmentTime': appointmentTime.toIso8601String(),
        'purpose': purpose,
        'isFirstVisit': isFirstVisit,
      };
      
      if (paymentMethod != null) {
        body['paymentMethod'] = paymentMethod.toString().split('.').last;
      }
      
      if (insuranceId != null) {
        body['insuranceId'] = insuranceId;
      }
      
      if (attachmentUrls != null && attachmentUrls.isNotEmpty) {
        body['attachmentUrls'] = attachmentUrls;
      }
      
      // 记录审计日志
      await _securityFramework.logSecurityAudit(
        operation: 'CREATE_APPOINTMENT',
        parameters: {'userId': userId, 'doctorId': doctorId},
        agentId: 'MEDICAL_SERVICE_API',
      );
      
      // 安全检查
      final securityCheck = await _securityFramework.checkDataPrivacy(
        data: body,
        operation: 'CREATE_APPOINTMENT',
        userId: userId,
      );
      
      if (!securityCheck.isApproved) {
        throw Exception('安全检查未通过: ${securityCheck.reason}');
      }
      
      // 发送API请求
      final response = await _serviceIntegration.sendRequest(
        'POST',
        '/api/medical/appointments',
        body: body,
      );
      
      // 解析响应数据
      return Appointment.fromJson(response.data);
    } catch (e) {
      if (kDebugMode) {
        print('创建预约失败: $e');
      }
      
      // 发送错误事件到Agent微内核
      _agentMicrokernel.publishEvent(
        AgentEvent(
          type: AgentEventType.error,
          source: 'MEDICAL_SERVICE_API',
          data: {
            'operation': 'createAppointment',
            'userId': userId,
            'doctorId': doctorId,
            'error': e.toString(),
          },
        ),
      );
      
      return null;
    }
  }
  
  // 实现其他接口方法...
  
  @override
  Future<List<Appointment>> getUserAppointments({
    required String userId,
    AppointmentStatus? status,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    // 暂时简化实现
    return [];
  }
  
  @override
  Future<bool> cancelAppointment({
    required String appointmentId,
    required String cancelReason,
  }) async {
    // 暂时简化实现
    return false;
  }
  
  @override
  Future<Appointment?> rescheduleAppointment({
    required String appointmentId,
    required DateTime newAppointmentTime,
  }) async {
    // 暂时简化实现
    return null;
  }
  
  @override
  Future<TelemedicineSession?> createTelemedicineSession({
    required String userId,
    required String doctorId,
    required TelemedicineType type,
    required String description,
    List<String>? attachmentUrls,
    PaymentMethod? paymentMethod,
  }) async {
    // 暂时简化实现
    return null;
  }
  
  @override
  Future<List<TelemedicineSession>> getUserTelemedicineSessions({
    required String userId,
    TelemedicineStatus? status,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    // 暂时简化实现
    return [];
  }
  
  @override
  Future<bool> endTelemedicineSession({
    required String sessionId,
  }) async {
    // 暂时简化实现
    return false;
  }
  
  @override
  Future<bool> rateHealthcareService({
    required String serviceId,
    required ServiceType serviceType,
    required double rating,
    String? comment,
    Map<String, double>? detailedRatings,
  }) async {
    // 暂时简化实现
    return false;
  }
  
  @override
  Future<List<MedicalRecord>> getUserMedicalRecords({
    required String userId,
    DateTime? startDate,
    DateTime? endDate,
    RecordType? type,
  }) async {
    // 暂时简化实现
    return [];
  }
  
  @override
  Future<String?> uploadMedicalDocument({
    required String userId,
    required Uint8List fileData,
    required String fileName,
    required String fileType,
    required RecordType documentType,
    String? description,
    DateTime? documentDate,
  }) async {
    // 暂时简化实现
    return null;
  }
  
  @override
  Future<InsuranceInfo?> getInsuranceInfo({
    required String userId,
  }) async {
    // 暂时简化实现
    return null;
  }
  
  @override
  Future<List<InsuranceCoverage>> queryInsuranceCoverage({
    required String userId,
    String? treatmentType,
    String? medicineName,
  }) async {
    // 暂时简化实现
    return [];
  }
  
  @override
  Future<List<Pharmacy>> getNearbyPharmacies({
    required double latitude,
    required double longitude,
    required int radiusInKm,
    bool? has24HourService,
    bool? hasDeliveryService,
  }) async {
    // 暂时简化实现
    return [];
  }
  
  @override
  Future<Medicine?> getMedicineInfo({
    String? medicineId,
    String? medicineName,
  }) async {
    // 暂时简化实现
    return null;
  }
  
  @override
  Future<List<MedicineInteraction>> checkMedicineInteractions({
    required List<String> medicineIds,
  }) async {
    // 暂时简化实现
    return [];
  }
  
  @override
  Future<List<HealthEducationContent>> getHealthEducationContents({
    String? category,
    String? keyword,
    int? limit,
    int? offset,
  }) async {
    // 暂时简化实现
    return [];
  }
  
  @override
  Future<List<HealthActivity>> getOfflineHealthActivities({
    required double latitude,
    required double longitude,
    required int radiusInKm,
    DateTime? startDate,
    DateTime? endDate,
    String? category,
  }) async {
    // 暂时简化实现
    return [];
  }
}

/// Provider for MedicalServiceAPI
final medicalServiceAPIServiceProvider = Provider<MedicalServiceAPI>((ref) {
  final serviceIntegration = ref.watch(serviceIntegrationRegistryServiceProvider);
  final securityFramework = ref.watch(securityFrameworkServiceProvider);
  final agentMicrokernel = ref.watch(agentMicrokernelServiceProvider);
  
  return MedicalServiceAPIImpl(
    serviceIntegration: serviceIntegration,
    securityFramework: securityFramework,
    agentMicrokernel: agentMicrokernel,
  );
});

/// @deprecated 使用medicalServiceAPIServiceProvider替代
@Deprecated('使用medicalServiceAPIServiceProvider替代')
final medicalServiceAPIProvider = medicalServiceAPIServiceProvider;
  