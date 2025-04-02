import 'package:json_annotation/json_annotation.dart';

part 'supply_chain_model.g.dart';

@JsonSerializable()
class SupplyChainEventModel {
  final String id;
  final String productId;
  final String type;
  final String description;
  final String timestamp;
  final String? location;
  final Map<String, dynamic>? metadata;
  
  // 区块链验证状态
  final bool? verified;
  final String? blockchainHash;

  SupplyChainEventModel({
    required this.id,
    required this.productId,
    required this.type,
    required this.description,
    required this.timestamp,
    this.location,
    this.metadata,
    this.verified,
    this.blockchainHash,
  });

  factory SupplyChainEventModel.fromJson(Map<String, dynamic> json) => 
      _$SupplyChainEventModelFromJson(json);
  
  Map<String, dynamic> toJson() => _$SupplyChainEventModelToJson(this);
}

@JsonSerializable()
class ProductTraceabilityModel {
  final String qrCodeId;
  final Map<String, dynamic> product;
  final Map<String, dynamic> journey;
  final List<Map<String, dynamic>> keyEvents;
  final Map<String, dynamic> certification;
  final Map<String, dynamic> scanInfo;
  
  ProductTraceabilityModel({
    required this.qrCodeId,
    required this.product,
    required this.journey,
    required this.keyEvents,
    required this.certification,
    required this.scanInfo,
  });

  factory ProductTraceabilityModel.fromJson(Map<String, dynamic> json) => 
      _$ProductTraceabilityModelFromJson(json);
  
  Map<String, dynamic> toJson() => _$ProductTraceabilityModelToJson(this);
}

@JsonSerializable()
class SupplyChainRiskModel {
  final String type;
  final double probability;
  final int severity;
  final int impact;
  final String description;
  final List<String> suggestedActions;
  final String expectedTimeframe;

  SupplyChainRiskModel({
    required this.type,
    required this.probability,
    required this.severity,
    required this.impact,
    required this.description,
    required this.suggestedActions,
    required this.expectedTimeframe,
  });

  factory SupplyChainRiskModel.fromJson(Map<String, dynamic> json) => 
      _$SupplyChainRiskModelFromJson(json);
  
  Map<String, dynamic> toJson() => _$SupplyChainRiskModelToJson(this);
}