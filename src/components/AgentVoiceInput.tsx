import {
import React, { useState } from "react";

  View,
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
} from "react-native";

// 推荐集成react-native-voice或expo-speech
// import Voice from '@react-native-voice/voice';

export const AgentVoiceInput: React.FC<{
  onResult: (text: string) => void;
}> = ({ onResult }) => {
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);

  // 伪实现，实际应集成语音识别SDK
  const startRecording = async () => {
    setRecording(true);
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setRecording(false);
      onResult("模拟语音识别结果");
    }, 2000);
  };

  const stopRecording = async () => {
    setRecording(false);
    setLoading(false);
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={[styles.button, recording && styles.buttonActive]}
        onPress={recording ? stopRecording : startRecording}
        disabled={loading}
      >
        <Text style={styles.icon}>{recording ? "🛑" : "🎤"}</Text>
        <Text style={styles.text}>{recording ? "录音中..." : "按下说话"}</Text>
      </TouchableOpacity>
      {loading && <ActivityIndicator style={{ marginLeft: 12 }} />}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: 12,
  },
  button: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#E1F5FE",
    borderRadius: 24,
    paddingVertical: 10,
    paddingHorizontal: 20,
  },
  buttonActive: {
    backgroundColor: "#B3E5FC",
  },
  icon: {
    fontSize: 22,
    marginRight: 8,
  },
  text: {
    fontSize: 16,
    color: "#0277BD",
  },
});
