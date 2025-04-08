import 'package:json_annotation/json_annotation.dart';
import 'package:suoke_life/domain/entities/health_data_token.dart';

part 'health_data_token_model.g.dart';

@JsonSerializable()
class HealthDataTokenModel {
  final String address;
  final String symbol;
  final String name;
  @JsonKey(fromJson: _bigIntFromString, toJson: _bigIntToString)
  final BigInt totalSupply;
  @JsonKey(fromJson: _bigIntFromString, toJson: _bigIntToString)
  final BigInt balance;

  HealthDataTokenModel({
    required this.address,
    required this.symbol,
    required this.name,
    required this.totalSupply,
    required this.balance,
  });

  factory HealthDataTokenModel.fromJson(Map<String, dynamic> json) => 
      _$HealthDataTokenModelFromJson(json);

  Map<String, dynamic> toJson() => _$HealthDataTokenModelToJson(this);

  factory HealthDataTokenModel.fromEntity(HealthDataToken entity) {
    return HealthDataTokenModel(
      address: entity.address,
      symbol: entity.symbol,
      name: entity.name,
      totalSupply: entity.totalSupply,
      balance: entity.balance,
    );
  }

  HealthDataToken toEntity() {
    return HealthDataToken(
      address: address,
      symbol: symbol,
      name: name,
      totalSupply: totalSupply,
      balance: balance,
    );
  }

  static BigInt _bigIntFromString(String value) => BigInt.parse(value);
  static String _bigIntToString(BigInt value) => value.toString();
} 