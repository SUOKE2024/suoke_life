import 'dart:async';
import '../core/network/http_client.dart';
import 'multimedia_service.dart';

enum WorkflowType {
  medicalReport,
  consultation,
  followUp,
  dataCollection
}

enum WorkflowStatus {
  pending,
  processing,
  completed,
  failed
}

class WorkflowResult {
  final String id;
  final WorkflowType type;
  final WorkflowStatus status;
  final DateTime timestamp;
  final Map<String, dynamic> result;
  final String? error;

  WorkflowResult({
    required this.id,
    required this.type,
    required this.status,
    required this.timestamp,
    required this.result,
    this.error,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'type': type.toString(),
    'status': status.toString(),
    'timestamp': timestamp.toIso8601String(),
    'result': result,
    'error': error,
  };
}

class WorkflowService {
  final HttpClient _httpClient;
  final MultimediaService _multimediaService;
  final StreamController<WorkflowResult> _workflowController = 
      StreamController<WorkflowResult>.broadcast();

  WorkflowService({
    required HttpClient httpClient,
    required MultimediaService multimediaService,
  }) : _httpClient = httpClient,
       _multimediaService = multimediaService {
    _initializeWorkflowHandlers();
  }

  void _initializeWorkflowHandlers() {
    _multimediaService.mediaStream.listen((mediaData) {
      if (mediaData.type == MediaType.medicalReport) {
        _handleMedicalReport(mediaData);
      }
    });
  }

  Future<WorkflowResult> _handleMedicalReport(MediaData mediaData) async {
    try {
      // 创建工作流结果
      final workflowResult = WorkflowResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: WorkflowType.medicalReport,
        status: WorkflowStatus.processing,
        timestamp: DateTime.now(),
        result: {'mediaId': mediaData.id},
      );

      // 发送到工作流流
      _workflowController.add(workflowResult);

      // 调用医疗报告处理API
      final response = await _httpClient.post(
        Uri.parse('YOUR_API_ENDPOINT/process-medical-report'),
        body: {
          'mediaId': mediaData.id,
          'metadata': mediaData.metadata,
          'timestamp': mediaData.timestamp.toIso8601String(),
        },
      );

      if (response.statusCode == 200) {
        final updatedResult = WorkflowResult(
          id: workflowResult.id,
          type: WorkflowType.medicalReport,
          status: WorkflowStatus.completed,
          timestamp: DateTime.now(),
          result: {
            ...workflowResult.result,
            'apiResponse': response.body,
          },
        );
        _workflowController.add(updatedResult);
        return updatedResult;
      } else {
        throw Exception('处理失败: ${response.statusCode}');
      }
    } catch (e) {
      final errorResult = WorkflowResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: WorkflowType.medicalReport,
        status: WorkflowStatus.failed,
        timestamp: DateTime.now(),
        result: {'mediaId': mediaData.id},
        error: e.toString(),
      );
      _workflowController.add(errorResult);
      return errorResult;
    }
  }

  Future<WorkflowResult> startConsultation({
    required String userId,
    required List<MediaData> attachments,
  }) async {
    try {
      // 创建会诊工作流
      final workflowResult = WorkflowResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: WorkflowType.consultation,
        status: WorkflowStatus.processing,
        timestamp: DateTime.now(),
        result: {
          'userId': userId,
          'attachmentIds': attachments.map((a) => a.id).toList(),
        },
      );

      _workflowController.add(workflowResult);

      // 调用会诊API
      final response = await _httpClient.post(
        Uri.parse('YOUR_API_ENDPOINT/start-consultation'),
        body: {
          'userId': userId,
          'attachments': attachments.map((a) => a.toJson()).toList(),
          'timestamp': DateTime.now().toIso8601String(),
        },
      );

      if (response.statusCode == 200) {
        final updatedResult = WorkflowResult(
          id: workflowResult.id,
          type: WorkflowType.consultation,
          status: WorkflowStatus.completed,
          timestamp: DateTime.now(),
          result: {
            ...workflowResult.result,
            'consultationId': response.body,
          },
        );
        _workflowController.add(updatedResult);
        return updatedResult;
      } else {
        throw Exception('创建会诊失败: ${response.statusCode}');
      }
    } catch (e) {
      final errorResult = WorkflowResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: WorkflowType.consultation,
        status: WorkflowStatus.failed,
        timestamp: DateTime.now(),
        result: {'userId': userId},
        error: e.toString(),
      );
      _workflowController.add(errorResult);
      return errorResult;
    }
  }

  Future<WorkflowResult> startDataCollection({
    required String userId,
    required String type,
    required Map<String, dynamic> parameters,
  }) async {
    try {
      // 创建数据采集工作流
      final workflowResult = WorkflowResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: WorkflowType.dataCollection,
        status: WorkflowStatus.processing,
        timestamp: DateTime.now(),
        result: {
          'userId': userId,
          'type': type,
          'parameters': parameters,
        },
      );

      _workflowController.add(workflowResult);

      // 调用数据采集API
      final response = await _httpClient.post(
        Uri.parse('YOUR_API_ENDPOINT/start-data-collection'),
        body: {
          'userId': userId,
          'type': type,
          'parameters': parameters,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );

      if (response.statusCode == 200) {
        final updatedResult = WorkflowResult(
          id: workflowResult.id,
          type: WorkflowType.dataCollection,
          status: WorkflowStatus.completed,
          timestamp: DateTime.now(),
          result: {
            ...workflowResult.result,
            'collectionId': response.body,
          },
        );
        _workflowController.add(updatedResult);
        return updatedResult;
      } else {
        throw Exception('创建数据采集任务失败: ${response.statusCode}');
      }
    } catch (e) {
      final errorResult = WorkflowResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        type: WorkflowType.dataCollection,
        status: WorkflowStatus.failed,
        timestamp: DateTime.now(),
        result: {'userId': userId},
        error: e.toString(),
      );
      _workflowController.add(errorResult);
      return errorResult;
    }
  }

  void dispose() {
    _workflowController.close();
  }

  // Getters
  Stream<WorkflowResult> get workflowStream => _workflowController.stream;
  MultimediaService get multimediaService => _multimediaService;
} 