import 'dart:async';
import '../intelligence/services/coze_service.dart';
import '../intelligence/services/intent_recognition_service.dart';
import 'consultation_service.dart';
import 'consultation_participant_service.dart';
import 'error_handler_service.dart';

enum ScheduleStatus {
  pending, // 待处理
  confirmed, // 已确认
  inProgress, // 进行中
  completed, // 已完成
  cancelled, // 已取消
  rescheduled // 已改期
}

class ScheduleRequest {
  final String id;
  final String patientId;
  final String patientName;
  final String description;
  final DateTime preferredTime;
  final ConsultationType type;
  final List<String>? preferredDoctors;
  final bool isUrgent;
  final Map<String, dynamic>? metadata;

  ScheduleRequest({
    required this.id,
    required this.patientId,
    required this.patientName,
    required this.description,
    required this.preferredTime,
    required this.type,
    this.preferredDoctors,
    this.isUrgent = false,
    this.metadata,
  });
}

class ScheduleInfo {
  final String id;
  final ScheduleRequest request;
  final ScheduleStatus status;
  final DateTime scheduledTime;
  final List<ParticipantInfo> participants;
  final String? cancelReason;
  final Map<String, dynamic>? aiAnalysis;

  ScheduleInfo({
    required this.id,
    required this.request,
    required this.status,
    required this.scheduledTime,
    required this.participants,
    this.cancelReason,
    this.aiAnalysis,
  });
}

class ConsultationSchedulingService {
  final CozeService _cozeService;
  final IntentRecognitionService _intentService;
  final ConsultationService _consultationService;
  final ConsultationParticipantService _participantService;
  final ErrorHandlerService _errorHandler;

  final _scheduleController = StreamController<ScheduleInfo>.broadcast();
  final _reminderController = StreamController<Map<String, dynamic>>.broadcast();
  
  final Map<String, ScheduleInfo> _schedules = {};
  Timer? _schedulingTimer;

  ConsultationSchedulingService({
    required CozeService cozeService,
    required IntentRecognitionService intentService,
    required ConsultationService consultationService,
    required ConsultationParticipantService participantService,
    required ErrorHandlerService errorHandler,
  }) : _cozeService = cozeService,
       _intentService = intentService,
       _consultationService = consultationService,
       _participantService = participantService,
       _errorHandler = errorHandler {
    _initializeScheduling();
  }

  void _initializeScheduling() {
    // 启动定时调度检查
    _schedulingTimer = Timer.periodic(const Duration(minutes: 1), (_) {
      _checkUpcomingSchedules();
    });
  }

  Future<ScheduleInfo> requestConsultation(ScheduleRequest request) async {
    try {
      // AI分析请求
      final analysis = await _cozeService.analyzeConsultationRequest(
        request.description,
        request.type,
        request.isUrgent,
      );

      // 创建调度信息
      final schedule = ScheduleInfo(
        id: request.id,
        request: request,
        status: ScheduleStatus.pending,
        scheduledTime: request.preferredTime,
        participants: [],
        aiAnalysis: analysis,
      );

      // 存储调度信息
      _schedules[request.id] = schedule;
      _scheduleController.add(schedule);

      // AI处理请求
      await _processScheduleRequest(schedule);

      return schedule;
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'SCHEDULE_REQUEST_ERROR',
        '处理会诊请求失败: ${e.toString()}',
        ErrorSeverity.high,
        originalError: e,
        stackTrace: stackTrace,
      );
      rethrow;
    }
  }

  Future<void> _processScheduleRequest(ScheduleInfo schedule) async {
    try {
      // 分析紧急程度
      if (schedule.request.isUrgent) {
        await _handleUrgentRequest(schedule);
      } else {
        await _handleNormalRequest(schedule);
      }
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'SCHEDULE_PROCESS_ERROR',
        '处理调度请求失败: ${e.toString()}',
        ErrorSeverity.medium,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> _handleUrgentRequest(ScheduleInfo schedule) async {
    // 立即寻找可用专家
    final availableDoctors = await _findAvailableDoctors(
      schedule.request.type,
      DateTime.now(),
      isUrgent: true,
    );

    if (availableDoctors.isEmpty) {
      // 没有立即可用的专家，升级处理
      await _escalateUrgentRequest(schedule);
    } else {
      // 立即安排会诊
      await _arrangeConsultation(
        schedule,
        availableDoctors,
        DateTime.now(),
      );
    }
  }

  Future<void> _handleNormalRequest(ScheduleInfo schedule) async {
    // 分析最佳时间
    final preferredTime = schedule.request.preferredTime;
    final availableDoctors = await _findAvailableDoctors(
      schedule.request.type,
      preferredTime,
    );

    if (availableDoctors.isEmpty) {
      // 寻找替代时间
      final alternativeTime = await _findAlternativeTime(
        schedule.request.type,
        preferredTime,
      );
      
      if (alternativeTime != null) {
        final doctors = await _findAvailableDoctors(
          schedule.request.type,
          alternativeTime,
        );
        
        if (doctors.isNotEmpty) {
          await _arrangeConsultation(schedule, doctors, alternativeTime);
          return;
        }
      }
      
      // 无法找到合适时间，通知重新安排
      await _requestReschedule(schedule);
    } else {
      // 安排会诊
      await _arrangeConsultation(
        schedule,
        availableDoctors,
        preferredTime,
      );
    }
  }

  Future<List<ParticipantInfo>> _findAvailableDoctors(
    ConsultationType type,
    DateTime time, {
    bool isUrgent = false,
  }) async {
    // TODO: 实现医生查找逻辑
    return [];
  }

  Future<DateTime?> _findAlternativeTime(
    ConsultationType type,
    DateTime preferredTime,
  ) async {
    // TODO: 实现替代时间查找逻辑
    return null;
  }

  Future<void> _arrangeConsultation(
    ScheduleInfo schedule,
    List<ParticipantInfo> doctors,
    DateTime time,
  ) async {
    try {
      // 更新调度状态
      final updatedSchedule = ScheduleInfo(
        id: schedule.id,
        request: schedule.request,
        status: ScheduleStatus.confirmed,
        scheduledTime: time,
        participants: [
          ...doctors,
          ParticipantInfo(
            id: schedule.request.patientId,
            name: schedule.request.patientName,
            role: ParticipantRole.patient,
            status: ParticipantStatus.invited,
            joinTime: time,
          ),
        ],
        aiAnalysis: schedule.aiAnalysis,
      );

      _schedules[schedule.id] = updatedSchedule;
      _scheduleController.add(updatedSchedule);

      // 发送通知
      await _sendScheduleNotifications(updatedSchedule);
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'SCHEDULE_ARRANGE_ERROR',
        '安排会诊失败: ${e.toString()}',
        ErrorSeverity.high,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> _escalateUrgentRequest(ScheduleInfo schedule) async {
    // TODO: 实现紧急请求升级逻辑
  }

  Future<void> _requestReschedule(ScheduleInfo schedule) async {
    try {
      final updatedSchedule = ScheduleInfo(
        id: schedule.id,
        request: schedule.request,
        status: ScheduleStatus.rescheduled,
        scheduledTime: schedule.scheduledTime,
        participants: schedule.participants,
        aiAnalysis: schedule.aiAnalysis,
      );

      _schedules[schedule.id] = updatedSchedule;
      _scheduleController.add(updatedSchedule);

      // 发送重新安排通知
      await _sendRescheduleNotifications(updatedSchedule);
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'SCHEDULE_RESCHEDULE_ERROR',
        '重新安排会诊失败: ${e.toString()}',
        ErrorSeverity.medium,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> _checkUpcomingSchedules() async {
    final now = DateTime.now();
    
    for (final schedule in _schedules.values) {
      if (schedule.status == ScheduleStatus.confirmed) {
        final difference = schedule.scheduledTime.difference(now);
        
        // 发送提醒
        if (difference.inMinutes <= 30 && difference.inMinutes > 0) {
          await _sendReminders(schedule);
        }
        
        // 自动开始会诊
        if (difference.inMinutes <= 1 && difference.isNegative == false) {
          await _startConsultation(schedule);
        }
      }
    }
  }

  Future<void> _startConsultation(ScheduleInfo schedule) async {
    try {
      // 创建会诊
      final consultation = ConsultationData(
        id: schedule.id,
        type: schedule.request.type,
        startTime: DateTime.now(),
        patientId: schedule.request.patientId,
        patientName: schedule.request.patientName,
        doctorIds: schedule.participants
            .where((p) => p.role == ParticipantRole.doctor)
            .map((p) => p.id)
            .toList(),
        doctorNames: Map.fromEntries(
          schedule.participants
              .where((p) => p.role == ParticipantRole.doctor)
              .map((p) => MapEntry(p.id, p.name)),
        ),
      );

      // 启动会诊
      await _consultationService.startConsultation(consultation);

      // 更新状态
      final updatedSchedule = ScheduleInfo(
        id: schedule.id,
        request: schedule.request,
        status: ScheduleStatus.inProgress,
        scheduledTime: schedule.scheduledTime,
        participants: schedule.participants,
        aiAnalysis: schedule.aiAnalysis,
      );

      _schedules[schedule.id] = updatedSchedule;
      _scheduleController.add(updatedSchedule);
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'CONSULTATION_START_ERROR',
        '启动会诊失败: ${e.toString()}',
        ErrorSeverity.high,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> _sendScheduleNotifications(ScheduleInfo schedule) async {
    // TODO: 实现发送调度通知的逻辑
  }

  Future<void> _sendRescheduleNotifications(ScheduleInfo schedule) async {
    // TODO: 实现发送重新安排通知的逻辑
  }

  Future<void> _sendReminders(ScheduleInfo schedule) async {
    try {
      final reminder = {
        'scheduleId': schedule.id,
        'type': 'reminder',
        'time': DateTime.now().toIso8601String(),
        'message': '您有一个会诊即将在${schedule.scheduledTime.hour}:${schedule.scheduledTime.minute}开始',
      };

      _reminderController.add(reminder);
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'REMINDER_SEND_ERROR',
        '发送提醒失败: ${e.toString()}',
        ErrorSeverity.low,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  // Getters
  Stream<ScheduleInfo> get scheduleStream => _scheduleController.stream;
  Stream<Map<String, dynamic>> get reminderStream => _reminderController.stream;

  void dispose() {
    _scheduleController.close();
    _reminderController.close();
    _schedulingTimer?.cancel();
  }
} 