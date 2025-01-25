import 'package:get/get.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class OnboardingService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final hasCompletedOnboarding = false.obs;
  final currentStep = 0.obs;
  final onboardingData = <String, dynamic>{}.obs;

  @override
  void onInit() {
    super.onInit();
    _initOnboarding();
  }

  Future<void> _initOnboarding() async {
    try {
      await _loadOnboardingStatus();
      await _loadOnboardingData();
    } catch (e) {
      await _loggingService.log('error', 'Failed to initialize onboarding', data: {'error': e.toString()});
    }
  }

  // 开始引导
  Future<void> startOnboarding() async {
    try {
      currentStep.value = 0;
      hasCompletedOnboarding.value = false;
      await _saveOnboardingStatus();
    } catch (e) {
      await _loggingService.log('error', 'Failed to start onboarding', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 下一步
  Future<void> nextStep() async {
    try {
      currentStep.value++;
      await _saveOnboardingStatus();
    } catch (e) {
      await _loggingService.log('error', 'Failed to proceed to next step', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 完成引导
  Future<void> completeOnboarding() async {
    try {
      hasCompletedOnboarding.value = true;
      await _saveOnboardingStatus();
      await _recordCompletion();
    } catch (e) {
      await _loggingService.log('error', 'Failed to complete onboarding', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 更新引导数据
  Future<void> updateOnboardingData(Map<String, dynamic> data) async {
    try {
      onboardingData.addAll(data);
      await _saveOnboardingData();
    } catch (e) {
      await _loggingService.log('error', 'Failed to update onboarding data', data: {'error': e.toString()});
      rethrow;
    }
  }

  // 重置引导
  Future<void> resetOnboarding() async {
    try {
      currentStep.value = 0;
      hasCompletedOnboarding.value = false;
      onboardingData.clear();
      await _saveOnboardingStatus();
      await _saveOnboardingData();
    } catch (e) {
      await _loggingService.log('error', 'Failed to reset onboarding', data: {'error': e.toString()});
      rethrow;
    }
  }

  Future<void> _loadOnboardingStatus() async {
    try {
      final status = await _storageService.getLocal('onboarding_status');
      if (status != null) {
        hasCompletedOnboarding.value = status['completed'] ?? false;
        currentStep.value = status['current_step'] ?? 0;
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveOnboardingStatus() async {
    try {
      await _storageService.saveLocal('onboarding_status', {
        'completed': hasCompletedOnboarding.value,
        'current_step': currentStep.value,
        'updated_at': DateTime.now().toIso8601String(),
      });
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _loadOnboardingData() async {
    try {
      final data = await _storageService.getLocal('onboarding_data');
      if (data != null) {
        onboardingData.value = Map<String, dynamic>.from(data);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveOnboardingData() async {
    try {
      await _storageService.saveLocal('onboarding_data', onboardingData.value);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordCompletion() async {
    try {
      final completion = {
        'completed_at': DateTime.now().toIso8601String(),
        'steps_taken': currentStep.value,
        'data_collected': onboardingData.value,
      };

      final history = await _getCompletionHistory();
      history.add(completion);
      await _storageService.saveLocal('onboarding_history', history);
    } catch (e) {
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> _getCompletionHistory() async {
    try {
      final history = await _storageService.getLocal('onboarding_history');
      return history != null ? List<Map<String, dynamic>>.from(history) : [];
    } catch (e) {
      return [];
    }
  }
} 