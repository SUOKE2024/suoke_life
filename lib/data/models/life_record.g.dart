// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'life_record.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class LifeRecordAdapter extends TypeAdapter<LifeRecord> {
  @override
  final int typeId = 1;

  @override
  LifeRecord read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return LifeRecord(
      id: fields[0] as String,
      title: fields[1] as String,
      content: fields[2] as String?,
      time: fields[3] as String,
      tags: (fields[4] as List).cast<String>(),
      location: fields[5] as String?,
      images: (fields[6] as List?)?.cast<String>(),
      metadata: (fields[7] as Map?)?.cast<String, dynamic>(),
      createdAt: fields[8] as DateTime,
      updatedAt: fields[9] as DateTime?,
    );
  }

  @override
  void write(BinaryWriter writer, LifeRecord obj) {
    writer
      ..writeByte(10)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.title)
      ..writeByte(2)
      ..write(obj.content)
      ..writeByte(3)
      ..write(obj.time)
      ..writeByte(4)
      ..write(obj.tags)
      ..writeByte(5)
      ..write(obj.location)
      ..writeByte(6)
      ..write(obj.images)
      ..writeByte(7)
      ..write(obj.metadata)
      ..writeByte(8)
      ..write(obj.createdAt)
      ..writeByte(9)
      ..write(obj.updatedAt);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is LifeRecordAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
