// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'feedback.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class FeedbackRecordAdapter extends TypeAdapter<FeedbackRecord> {
  @override
  final int typeId = 3;

  @override
  FeedbackRecord read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return FeedbackRecord(
      id: fields[0] as String,
      type: fields[1] as String,
      content: fields[2] as String,
      contact: fields[3] as String?,
      images: (fields[4] as List?)?.cast<String>(),
      time: fields[5] as String,
      status: fields[6] as String,
    );
  }

  @override
  void write(BinaryWriter writer, FeedbackRecord obj) {
    writer
      ..writeByte(7)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.type)
      ..writeByte(2)
      ..write(obj.content)
      ..writeByte(3)
      ..write(obj.contact)
      ..writeByte(4)
      ..write(obj.images)
      ..writeByte(5)
      ..write(obj.time)
      ..writeByte(6)
      ..write(obj.status);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FeedbackRecordAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
