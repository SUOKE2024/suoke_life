// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'sync_config.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class SyncConfigAdapter extends TypeAdapter<SyncConfig> {
  @override
  final int typeId = 10;

  @override
  SyncConfig read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return SyncConfig(
      autoSync: fields[0] as bool,
      wifiOnlySync: fields[1] as bool,
      syncRanges: (fields[2] as List).cast<String>(),
      lastSyncTime: fields[3] as DateTime?,
    );
  }

  @override
  void write(BinaryWriter writer, SyncConfig obj) {
    writer
      ..writeByte(4)
      ..writeByte(0)
      ..write(obj.autoSync)
      ..writeByte(1)
      ..write(obj.wifiOnlySync)
      ..writeByte(2)
      ..write(obj.syncRanges)
      ..writeByte(3)
      ..write(obj.lastSyncTime);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SyncConfigAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
