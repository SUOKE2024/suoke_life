import 'package:equatable/equatable.dart';

class HealthRecord extends Equatable {
  final BigInt id;
  final String owner;
  final String dataHash;
  final String dataUrl;
  final BigInt timestamp;
  final bool isShared;
  final List<String> authorizedUsers;

  const HealthRecord({
    required this.id,
    required this.owner,
    required this.dataHash,
    required this.dataUrl,
    required this.timestamp,
    required this.isShared,
    required this.authorizedUsers,
  });

  @override
  List<Object?> get props => [id, owner, dataHash, dataUrl, timestamp, isShared, authorizedUsers];

  HealthRecord copyWith({
    BigInt? id,
    String? owner,
    String? dataHash,
    String? dataUrl,
    BigInt? timestamp,
    bool? isShared,
    List<String>? authorizedUsers,
  }) {
    return HealthRecord(
      id: id ?? this.id,
      owner: owner ?? this.owner,
      dataHash: dataHash ?? this.dataHash,
      dataUrl: dataUrl ?? this.dataUrl,
      timestamp: timestamp ?? this.timestamp,
      isShared: isShared ?? this.isShared,
      authorizedUsers: authorizedUsers ?? this.authorizedUsers,
    );
  }
} 