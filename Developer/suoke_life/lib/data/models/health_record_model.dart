import 'package:json_annotation/json_annotation.dart';
import 'package:suoke_life/domain/entities/health_record.dart';

part 'health_record_model.g.dart';

@JsonSerializable()
class HealthRecordModel {
  @JsonKey(fromJson: _bigIntFromString, toJson: _bigIntToString)
  final BigInt id;
  final String owner;
  final String dataHash;
  final String dataUrl;
  @JsonKey(fromJson: _bigIntFromString, toJson: _bigIntToString)
  final BigInt timestamp;
  final bool isShared;
  final List<String> authorizedUsers;

  HealthRecordModel({
    required this.id,
    required this.owner,
    required this.dataHash,
    required this.dataUrl,
    required this.timestamp,
    required this.isShared,
    required this.authorizedUsers,
  });

  factory HealthRecordModel.fromJson(Map<String, dynamic> json) => 
      _$HealthRecordModelFromJson(json);

  Map<String, dynamic> toJson() => _$HealthRecordModelToJson(this);

  factory HealthRecordModel.fromEntity(HealthRecord entity) {
    return HealthRecordModel(
      id: entity.id,
      owner: entity.owner,
      dataHash: entity.dataHash,
      dataUrl: entity.dataUrl,
      timestamp: entity.timestamp,
      isShared: entity.isShared,
      authorizedUsers: entity.authorizedUsers,
    );
  }

  HealthRecord toEntity() {
    return HealthRecord(
      id: id,
      owner: owner,
      dataHash: dataHash,
      dataUrl: dataUrl,
      timestamp: timestamp,
      isShared: isShared,
      authorizedUsers: authorizedUsers,
    );
  }

  static BigInt _bigIntFromString(String value) => BigInt.parse(value);
  static String _bigIntToString(BigInt value) => value.toString();
} 