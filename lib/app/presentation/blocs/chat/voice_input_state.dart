abstract class VoiceInputState {
  const VoiceInputState();
}

class VoiceInputInitial extends VoiceInputState {
  const VoiceInputInitial();
}

class VoiceInputRecording extends VoiceInputState {
  const VoiceInputRecording();
}

class VoiceInputProcessing extends VoiceInputState {
  const VoiceInputProcessing();
}

class VoiceInputSuccess extends VoiceInputState {
  final String text;
  const VoiceInputSuccess(this.text);
}

class VoiceInputFailure extends VoiceInputState {
  final String error;
  const VoiceInputFailure(this.error);
} 