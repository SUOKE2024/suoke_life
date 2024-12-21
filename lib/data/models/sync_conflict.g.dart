// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'sync_conflict.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class SyncConflictAdapter extends TypeAdapter<SyncConflict> {
  @override
  final int typeId = 12;

  @override
  SyncConflict read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return SyncConflict(
      id: fields[0] as String,
      type: fields[1] as String,
      localTime: fields[2] as DateTime,
      serverTime: fields[3] as DateTime,
      localData: (fields[4] as Map).cast<String, dynamic>(),
      serverData: (fields[5] as Map).cast<String, dynamic>(),
      resolved: fields[6] as bool,
      resolution: fields[7] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, SyncConflict obj) {
    writer
      ..writeByte(8)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.type)
      ..writeByte(2)
      ..write(obj.localTime)
      ..writeByte(3)
      ..write(obj.serverTime)
      ..writeByte(4)
      ..write(obj.localData)
      ..writeByte(5)
      ..write(obj.serverData)
      ..writeByte(6)
      ..write(obj.resolved)
      ..writeByte(7)
      ..write(obj.resolution);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SyncConflictAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
