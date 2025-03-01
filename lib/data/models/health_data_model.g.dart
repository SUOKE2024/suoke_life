// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'health_data_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

HealthDataModel _$HealthDataModelFromJson(Map<String, dynamic> json) =>
    HealthDataModel(
      id: json['id'] as String,
      userId: json['userId'] as String,
      type: $enumDecode(_$HealthDataTypeEnumMap, json['type'],
          unknownValue: HealthDataType.steps),
      value: json['value'] as num,
      unit: $enumDecode(_$HealthUnitEnumMap, json['unit'],
          unknownValue: HealthUnit.count),
      timestamp: DateTime.parse(json['timestamp'] as String),
      source: $enumDecode(_$HealthDataSourceEnumMap, json['source'],
          unknownValue: HealthDataSource.manual),
      metadata: json['metadata'] as Map<String, dynamic>?,
      notes: json['notes'] as String?,
    );

Map<String, dynamic> _$HealthDataModelToJson(HealthDataModel instance) =>
    <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'type': _$HealthDataTypeEnumMap[instance.type]!,
      'value': instance.value,
      'unit': _$HealthUnitEnumMap[instance.unit]!,
      'timestamp': instance.timestamp.toIso8601String(),
      'source': _$HealthDataSourceEnumMap[instance.source]!,
      'metadata': instance.metadata,
      'notes': instance.notes,
    };

const _$HealthDataTypeEnumMap = {
  HealthDataType.steps: 'steps',
  HealthDataType.sleep: 'sleep',
  HealthDataType.heartRate: 'heartRate',
  HealthDataType.bloodPressure: 'bloodPressure',
  HealthDataType.bloodOxygen: 'bloodOxygen',
  HealthDataType.temperature: 'temperature',
  HealthDataType.weight: 'weight',
  HealthDataType.waterIntake: 'waterIntake',
  HealthDataType.foodIntake: 'foodIntake',
  HealthDataType.medication: 'medication',
  HealthDataType.mood: 'mood',
  HealthDataType.symptom: 'symptom',
  HealthDataType.activity: 'activity',
  HealthDataType.meditation: 'meditation',
};

const _$HealthUnitEnumMap = {
  HealthUnit.count: 'count',
  HealthUnit.minute: 'minute',
  HealthUnit.hour: 'hour',
  HealthUnit.step: 'step',
  HealthUnit.kilometer: 'kilometer',
  HealthUnit.meter: 'meter',
  HealthUnit.kilogram: 'kilogram',
  HealthUnit.gram: 'gram',
  HealthUnit.liter: 'liter',
  HealthUnit.milliliter: 'milliliter',
  HealthUnit.kilocalorie: 'kilocalorie',
  HealthUnit.bpm: 'bpm',
  HealthUnit.mmHg: 'mmHg',
  HealthUnit.celsius: 'celsius',
  HealthUnit.fahrenheit: 'fahrenheit',
  HealthUnit.percent: 'percent',
  HealthUnit.point: 'point',
};

const _$HealthDataSourceEnumMap = {
  HealthDataSource.manual: 'manual',
  HealthDataSource.device: 'device',
  HealthDataSource.thirdPartyApp: 'thirdPartyApp',
  HealthDataSource.calculation: 'calculation',
  HealthDataSource.aiInference: 'aiInference',
};
