// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ai_chat.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class AIChatAdapter extends TypeAdapter<AIChat> {
  @override
  final int typeId = 4;

  @override
  AIChat read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return AIChat(
      id: fields[0] as String,
      role: fields[1] as String,
      content: fields[2] as String,
      time: fields[3] as String,
    );
  }

  @override
  void write(BinaryWriter writer, AIChat obj) {
    writer
      ..writeByte(4)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.role)
      ..writeByte(2)
      ..write(obj.content)
      ..writeByte(3)
      ..write(obj.time);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is AIChatAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
