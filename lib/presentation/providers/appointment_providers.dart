import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/api_client.dart';
import '../../data/repositories/appointment_repository_impl.dart';
import '../../domain/entities/appointment.dart';
import '../../domain/repositories/appointment_repository.dart';
import 'auth_providers.dart';

/// 预约仓库提供者
final appointmentRepositoryProvider = Provider<AppointmentRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return AppointmentRepositoryImpl(apiClient: apiClient);
});

/// API客户端提供者
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

/// 预约状态
class AppointmentState {
  final List<Appointment> appointments;
  final List<Appointment> upcomingAppointments;
  final List<Appointment> pastAppointments;
  final bool isLoading;
  final String? errorMessage;
  final Appointment? selectedAppointment;
  final List<DateTime> availableTimeSlots;
  final bool isCreatingAppointment;
  final bool isUpdatingAppointment;

  AppointmentState({
    this.appointments = const [],
    this.upcomingAppointments = const [],
    this.pastAppointments = const [],
    this.isLoading = false,
    this.errorMessage,
    this.selectedAppointment,
    this.availableTimeSlots = const [],
    this.isCreatingAppointment = false,
    this.isUpdatingAppointment = false,
  });

  AppointmentState copyWith({
    List<Appointment>? appointments,
    List<Appointment>? upcomingAppointments,
    List<Appointment>? pastAppointments,
    bool? isLoading,
    String? errorMessage,
    Appointment? selectedAppointment,
    List<DateTime>? availableTimeSlots,
    bool? isCreatingAppointment,
    bool? isUpdatingAppointment,
  }) {
    return AppointmentState(
      appointments: appointments ?? this.appointments,
      upcomingAppointments: upcomingAppointments ?? this.upcomingAppointments,
      pastAppointments: pastAppointments ?? this.pastAppointments,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      selectedAppointment: selectedAppointment ?? this.selectedAppointment,
      availableTimeSlots: availableTimeSlots ?? this.availableTimeSlots,
      isCreatingAppointment: isCreatingAppointment ?? this.isCreatingAppointment,
      isUpdatingAppointment: isUpdatingAppointment ?? this.isUpdatingAppointment,
    );
  }
}

/// 预约状态通知者
class AppointmentNotifier extends StateNotifier<AppointmentState> {
  final AppointmentRepository _repository;

  AppointmentNotifier({required AppointmentRepository repository})
      : _repository = repository,
        super(AppointmentState());

  /// 获取用户所有预约
  Future<void> getUserAppointments(String userId) async {
    try {
      state = state.copyWith(isLoading: true, errorMessage: null);
      final appointments = await _repository.getUserAppointments(userId);
      state = state.copyWith(
        appointments: appointments,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '获取预约失败: $e',
      );
    }
  }

  /// 获取用户即将到来的预约
  Future<void> getUpcomingAppointments(String userId) async {
    try {
      state = state.copyWith(isLoading: true, errorMessage: null);
      final appointments = await _repository.getUpcomingAppointments(userId);
      state = state.copyWith(
        upcomingAppointments: appointments,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '获取即将到来的预约失败: $e',
      );
    }
  }

  /// 获取用户历史预约
  Future<void> getPastAppointments(String userId, {int limit = 10, int offset = 0}) async {
    try {
      state = state.copyWith(isLoading: true, errorMessage: null);
      final appointments = await _repository.getPastAppointments(
        userId,
        limit: limit,
        offset: offset,
      );
      state = state.copyWith(
        pastAppointments: appointments,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '获取历史预约失败: $e',
      );
    }
  }

  /// 获取预约详情
  Future<void> getAppointmentById(String appointmentId) async {
    try {
      state = state.copyWith(isLoading: true, errorMessage: null);
      final appointment = await _repository.getAppointmentById(appointmentId);
      state = state.copyWith(
        selectedAppointment: appointment,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '获取预约详情失败: $e',
      );
    }
  }

  /// 创建预约
  Future<Appointment?> createAppointment({
    required String userId,
    required String serviceId,
    required String providerId,
    required DateTime appointmentDate,
    required DateTime startTime,
    required DateTime endTime,
    String? notes,
  }) async {
    try {
      state = state.copyWith(isCreatingAppointment: true, errorMessage: null);
      final appointment = await _repository.createAppointment(
        userId: userId,
        serviceId: serviceId,
        providerId: providerId,
        appointmentDate: appointmentDate,
        startTime: startTime,
        endTime: endTime,
        notes: notes,
      );
      
      // 更新即将到来的预约列表
      final updatedUpcoming = [...state.upcomingAppointments, appointment];
      
      state = state.copyWith(
        upcomingAppointments: updatedUpcoming,
        isCreatingAppointment: false,
      );
      
      return appointment;
    } catch (e) {
      state = state.copyWith(
        isCreatingAppointment: false,
        errorMessage: '创建预约失败: $e',
      );
      return null;
    }
  }

  /// 取消预约
  Future<bool> cancelAppointment(String appointmentId, {String? reason}) async {
    try {
      state = state.copyWith(isUpdatingAppointment: true, errorMessage: null);
      final success = await _repository.cancelAppointment(appointmentId, reason: reason);
      
      if (success) {
        // 更新预约状态
        final updatedUpcoming = state.upcomingAppointments.map((appointment) {
          if (appointment.id == appointmentId) {
            return appointment.copyWith(status: AppointmentStatus.cancelled);
          }
          return appointment;
        }).toList();
        
        state = state.copyWith(
          upcomingAppointments: updatedUpcoming,
          isUpdatingAppointment: false,
        );
      } else {
        state = state.copyWith(
          isUpdatingAppointment: false,
          errorMessage: '取消预约失败',
        );
      }
      
      return success;
    } catch (e) {
      state = state.copyWith(
        isUpdatingAppointment: false,
        errorMessage: '取消预约失败: $e',
      );
      return false;
    }
  }

  /// 确认预约
  Future<bool> confirmAppointment(String appointmentId) async {
    try {
      state = state.copyWith(isUpdatingAppointment: true, errorMessage: null);
      final success = await _repository.confirmAppointment(appointmentId);
      
      if (success) {
        // 更新预约状态
        final updatedUpcoming = state.upcomingAppointments.map((appointment) {
          if (appointment.id == appointmentId) {
            return appointment.copyWith(status: AppointmentStatus.confirmed);
          }
          return appointment;
        }).toList();
        
        state = state.copyWith(
          upcomingAppointments: updatedUpcoming,
          isUpdatingAppointment: false,
        );
      } else {
        state = state.copyWith(
          isUpdatingAppointment: false,
          errorMessage: '确认预约失败',
        );
      }
      
      return success;
    } catch (e) {
      state = state.copyWith(
        isUpdatingAppointment: false,
        errorMessage: '确认预约失败: $e',
      );
      return false;
    }
  }

  /// 完成预约
  Future<bool> completeAppointment(String appointmentId) async {
    try {
      state = state.copyWith(isUpdatingAppointment: true, errorMessage: null);
      final success = await _repository.completeAppointment(appointmentId);
      
      if (success) {
        // 从即将到来的预约中移除，并添加到历史预约中
        final appointment = state.upcomingAppointments.firstWhere(
          (appointment) => appointment.id == appointmentId,
        );
        
        final updatedUpcoming = state.upcomingAppointments
            .where((appointment) => appointment.id != appointmentId)
            .toList();
        
        final updatedPast = [
          appointment.copyWith(status: AppointmentStatus.completed),
          ...state.pastAppointments,
        ];
        
        state = state.copyWith(
          upcomingAppointments: updatedUpcoming,
          pastAppointments: updatedPast,
          isUpdatingAppointment: false,
        );
      } else {
        state = state.copyWith(
          isUpdatingAppointment: false,
          errorMessage: '完成预约失败',
        );
      }
      
      return success;
    } catch (e) {
      state = state.copyWith(
        isUpdatingAppointment: false,
        errorMessage: '完成预约失败: $e',
      );
      return false;
    }
  }

  /// 获取可用时间段
  Future<void> getAvailableTimeSlots({
    required String serviceId,
    required String providerId,
    required DateTime date,
  }) async {
    try {
      state = state.copyWith(isLoading: true, errorMessage: null);
      final slots = await _repository.getAvailableTimeSlots(
        serviceId: serviceId,
        providerId: providerId,
        date: date,
      );
      state = state.copyWith(
        availableTimeSlots: slots,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: '获取可用时间段失败: $e',
      );
    }
  }

  /// 重新安排预约
  Future<Appointment?> rescheduleAppointment({
    required String appointmentId,
    required DateTime newDate,
    required DateTime newStartTime,
    required DateTime newEndTime,
  }) async {
    try {
      state = state.copyWith(isUpdatingAppointment: true, errorMessage: null);
      final appointment = await _repository.rescheduleAppointment(
        appointmentId: appointmentId,
        newDate: newDate,
        newStartTime: newStartTime,
        newEndTime: newEndTime,
      );
      
      // 更新即将到来的预约列表
      final updatedUpcoming = state.upcomingAppointments.map((apt) {
        if (apt.id == appointmentId) {
          return appointment;
        }
        return apt;
      }).toList();
      
      state = state.copyWith(
        upcomingAppointments: updatedUpcoming,
        selectedAppointment: appointment,
        isUpdatingAppointment: false,
      );
      
      return appointment;
    } catch (e) {
      state = state.copyWith(
        isUpdatingAppointment: false,
        errorMessage: '重新安排预约失败: $e',
      );
      return null;
    }
  }

  /// 更新预约备注
  Future<bool> updateAppointmentNotes(String appointmentId, String notes) async {
    try {
      state = state.copyWith(isUpdatingAppointment: true, errorMessage: null);
      final success = await _repository.updateAppointmentNotes(appointmentId, notes);
      
      if (success) {
        // 更新预约备注
        final updatedUpcoming = state.upcomingAppointments.map((appointment) {
          if (appointment.id == appointmentId) {
            return appointment.copyWith(notes: notes);
          }
          return appointment;
        }).toList();
        
        final updatedPast = state.pastAppointments.map((appointment) {
          if (appointment.id == appointmentId) {
            return appointment.copyWith(notes: notes);
          }
          return appointment;
        }).toList();
        
        // 更新选中的预约
        Appointment? updatedSelected = state.selectedAppointment;
        if (updatedSelected != null && updatedSelected.id == appointmentId) {
          updatedSelected = updatedSelected.copyWith(notes: notes);
        }
        
        state = state.copyWith(
          upcomingAppointments: updatedUpcoming,
          pastAppointments: updatedPast,
          selectedAppointment: updatedSelected,
          isUpdatingAppointment: false,
        );
      } else {
        state = state.copyWith(
          isUpdatingAppointment: false,
          errorMessage: '更新预约备注失败',
        );
      }
      
      return success;
    } catch (e) {
      state = state.copyWith(
        isUpdatingAppointment: false,
        errorMessage: '更新预约备注失败: $e',
      );
      return false;
    }
  }

  /// 发送预约提醒
  Future<bool> sendAppointmentReminder(String appointmentId) async {
    try {
      state = state.copyWith(isUpdatingAppointment: true, errorMessage: null);
      final success = await _repository.sendAppointmentReminder(appointmentId);
      
      state = state.copyWith(isUpdatingAppointment: false);
      
      if (!success) {
        state = state.copyWith(errorMessage: '发送预约提醒失败');
      }
      
      return success;
    } catch (e) {
      state = state.copyWith(
        isUpdatingAppointment: false,
        errorMessage: '发送预约提醒失败: $e',
      );
      return false;
    }
  }

  /// 检查时间段是否可用
  Future<bool> isTimeSlotAvailable({
    required String serviceId,
    required String providerId,
    required DateTime startTime,
    required DateTime endTime,
  }) async {
    try {
      return await _repository.isTimeSlotAvailable(
        serviceId: serviceId,
        providerId: providerId,
        startTime: startTime,
        endTime: endTime,
      );
    } catch (e) {
      state = state.copyWith(errorMessage: '检查时间段可用性失败: $e');
      return false;
    }
  }

  /// 清除错误消息
  void clearError() {
    state = state.copyWith(errorMessage: null);
  }

  /// 清除选中的预约
  void clearSelectedAppointment() {
    state = state.copyWith(selectedAppointment: null);
  }
}

/// 预约提供者
final appointmentProvider = StateNotifierProvider<AppointmentNotifier, AppointmentState>((ref) {
  final repository = ref.watch(appointmentRepositoryProvider);
  return AppointmentNotifier(repository: repository);
});

/// 用户即将到来的预约提供者
final userUpcomingAppointmentsProvider = FutureProvider.family<List<Appointment>, String>((ref, userId) async {
  final repository = ref.watch(appointmentRepositoryProvider);
  return repository.getUpcomingAppointments(userId);
});

/// 用户历史预约提供者
final userPastAppointmentsProvider = FutureProvider.family<List<Appointment>, String>((ref, userId) async {
  final repository = ref.watch(appointmentRepositoryProvider);
  return repository.getPastAppointments(userId);
});

/// 预约详情提供者
final appointmentDetailsProvider = FutureProvider.family<Appointment, String>((ref, appointmentId) async {
  final repository = ref.watch(appointmentRepositoryProvider);
  return repository.getAppointmentById(appointmentId);
});

/// 可用时间段提供者
final availableTimeSlotsProvider = FutureProvider.family<List<DateTime>, Map<String, dynamic>>((ref, params) async {
  final repository = ref.watch(appointmentRepositoryProvider);
  return repository.getAvailableTimeSlots(
    serviceId: params['serviceId'] as String,
    providerId: params['providerId'] as String,
    date: params['date'] as DateTime,
  );
});