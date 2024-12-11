import 'dart:async';
import '../core/network/websocket_client.dart';
import 'error_handler_service.dart';

enum ParticipantRole {
  patient, // 患者
  doctor, // 医生
  specialist, // 专家
  assistant, // AI助手
  familyMember, // 家属
  nurse // 护士
}

enum ParticipantStatus {
  invited, // 已邀请
  waiting, // 等待中
  joined, // 已加入
  left, // 已离开
  offline // 离线
}

class ParticipantInfo {
  final String id;
  final String name;
  final ParticipantRole role;
  final ParticipantStatus status;
  final Map<String, dynamic>? metadata;
  final DateTime joinTime;
  final DateTime? leaveTime;

  ParticipantInfo({
    required this.id,
    required this.name,
    required this.role,
    required this.status,
    this.metadata,
    required this.joinTime,
    this.leaveTime,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'role': role.toString(),
      'status': status.toString(),
      'metadata': metadata,
      'joinTime': joinTime.toIso8601String(),
      'leaveTime': leaveTime?.toIso8601String(),
    };
  }

  factory ParticipantInfo.fromJson(Map<String, dynamic> json) {
    return ParticipantInfo(
      id: json['id'],
      name: json['name'],
      role: ParticipantRole.values.firstWhere(
        (e) => e.toString() == json['role'],
      ),
      status: ParticipantStatus.values.firstWhere(
        (e) => e.toString() == json['status'],
      ),
      metadata: json['metadata'],
      joinTime: DateTime.parse(json['joinTime']),
      leaveTime: json['leaveTime'] != null 
          ? DateTime.parse(json['leaveTime']) 
          : null,
    );
  }
}

class ConsultationParticipantService {
  final WebSocketClient _wsClient;
  final ErrorHandlerService _errorHandler;
  
  final _participantsController = StreamController<List<ParticipantInfo>>.broadcast();
  final _statusController = StreamController<Map<String, ParticipantStatus>>.broadcast();
  final _messageController = StreamController<Map<String, dynamic>>.broadcast();
  
  final Map<String, ParticipantInfo> _participants = {};
  String? _currentUserId;

  ConsultationParticipantService({
    required WebSocketClient wsClient,
    required ErrorHandlerService errorHandler,
  }) : _wsClient = wsClient,
       _errorHandler = errorHandler {
    _initializeMessageHandling();
  }

  void _initializeMessageHandling() {
    _wsClient.messages.listen(
      (message) {
        try {
          if (message is Map<String, dynamic>) {
            switch (message['type']) {
              case 'participantJoined':
                _handleParticipantJoined(message['data']);
                break;
              case 'participantLeft':
                _handleParticipantLeft(message['data']);
                break;
              case 'participantStatusChanged':
                _handleStatusChanged(message['data']);
                break;
              case 'participantMessage':
                _handleParticipantMessage(message['data']);
                break;
            }
          }
        } catch (e, stackTrace) {
          _errorHandler.handleError(
            'PARTICIPANT_MESSAGE_ERROR',
            '处理参与者消息失败: ${e.toString()}',
            ErrorSeverity.low,
            originalError: e,
            stackTrace: stackTrace,
          );
        }
      },
    );
  }

  Future<void> joinConsultation({
    required String userId,
    required String userName,
    required ParticipantRole role,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      _currentUserId = userId;
      final participant = ParticipantInfo(
        id: userId,
        name: userName,
        role: role,
        status: ParticipantStatus.joined,
        metadata: metadata,
        joinTime: DateTime.now(),
      );

      await _wsClient.send({
        'type': 'participantJoin',
        'data': participant.toJson(),
      });

      _participants[userId] = participant;
      _notifyParticipantsChanged();
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'PARTICIPANT_JOIN_ERROR',
        '加入会诊失败: ${e.toString()}',
        ErrorSeverity.high,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> leaveConsultation() async {
    if (_currentUserId == null) return;

    try {
      final participant = _participants[_currentUserId!];
      if (participant == null) return;

      final updatedParticipant = ParticipantInfo(
        id: participant.id,
        name: participant.name,
        role: participant.role,
        status: ParticipantStatus.left,
        metadata: participant.metadata,
        joinTime: participant.joinTime,
        leaveTime: DateTime.now(),
      );

      await _wsClient.send({
        'type': 'participantLeave',
        'data': updatedParticipant.toJson(),
      });

      _participants[_currentUserId!] = updatedParticipant;
      _notifyParticipantsChanged();
      _currentUserId = null;
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'PARTICIPANT_LEAVE_ERROR',
        '离开会诊失败: ${e.toString()}',
        ErrorSeverity.medium,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> updateStatus(ParticipantStatus status) async {
    if (_currentUserId == null) return;

    try {
      await _wsClient.send({
        'type': 'participantStatus',
        'userId': _currentUserId,
        'status': status.toString(),
      });

      final participant = _participants[_currentUserId!];
      if (participant != null) {
        final updatedParticipant = ParticipantInfo(
          id: participant.id,
          name: participant.name,
          role: participant.role,
          status: status,
          metadata: participant.metadata,
          joinTime: participant.joinTime,
          leaveTime: participant.leaveTime,
        );
        _participants[_currentUserId!] = updatedParticipant;
        _notifyParticipantsChanged();
      }
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'PARTICIPANT_STATUS_ERROR',
        '更新状态失败: ${e.toString()}',
        ErrorSeverity.low,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> sendMessageToParticipant(String targetId, Map<String, dynamic> message) async {
    if (_currentUserId == null) return;

    try {
      await _wsClient.send({
        'type': 'participantMessage',
        'fromId': _currentUserId,
        'toId': targetId,
        'message': message,
      });
    } catch (e, stackTrace) {
      _errorHandler.handleError(
        'PARTICIPANT_MESSAGE_SEND_ERROR',
        '发送消息失败: ${e.toString()}',
        ErrorSeverity.low,
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  void _handleParticipantJoined(Map<String, dynamic> data) {
    final participant = ParticipantInfo.fromJson(data);
    _participants[participant.id] = participant;
    _notifyParticipantsChanged();
  }

  void _handleParticipantLeft(Map<String, dynamic> data) {
    final participant = ParticipantInfo.fromJson(data);
    _participants[participant.id] = participant;
    _notifyParticipantsChanged();
  }

  void _handleStatusChanged(Map<String, dynamic> data) {
    final userId = data['userId'];
    final status = ParticipantStatus.values.firstWhere(
      (e) => e.toString() == data['status'],
    );

    final statusMap = <String, ParticipantStatus>{};
    for (final participant in _participants.values) {
      statusMap[participant.id] = participant.id == userId 
          ? status 
          : participant.status;
    }
    _statusController.add(statusMap);
  }

  void _handleParticipantMessage(Map<String, dynamic> data) {
    _messageController.add(data);
  }

  void _notifyParticipantsChanged() {
    _participantsController.add(_participants.values.toList());
  }

  // Getters
  List<ParticipantInfo> get participants => _participants.values.toList();
  Stream<List<ParticipantInfo>> get participantsStream => _participantsController.stream;
  Stream<Map<String, ParticipantStatus>> get statusStream => _statusController.stream;
  Stream<Map<String, dynamic>> get messageStream => _messageController.stream;

  // 便捷方法
  List<ParticipantInfo> getParticipantsByRole(ParticipantRole role) {
    return _participants.values
        .where((p) => p.role == role)
        .toList();
  }

  ParticipantInfo? getParticipant(String id) {
    return _participants[id];
  }

  bool isCurrentUser(String id) {
    return id == _currentUserId;
  }

  void dispose() {
    _participantsController.close();
    _statusController.close();
    _messageController.close();
  }
} 