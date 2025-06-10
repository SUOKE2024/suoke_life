import React, { useState } from 'react';
import {
  ActivityIndicator,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

interface AgentVoiceInputProps {
  onResult: (result: string) => void;
  disabled?: boolean;
  children?: React.ReactNode;
}

export const AgentVoiceInput: React.FC<AgentVoiceInputProps> = ({
  onResult,
  disabled = false,
}) => {
  const [recording, setRecording] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  const startRecording = async () => {
    if (disabled) return;

    setRecording(true);
    setLoading(true);

    // 模拟语音识别过程
    setTimeout(() => {
      setLoading(false);
      setRecording(false);
      onResult('模拟语音识别结果');
    }, 2000);
  };

  const stopRecording = async () => {
    setRecording(false);
    setLoading(false);
  };

  const handlePress = () => {
    if (recording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={[
          styles.button,
          recording && styles.buttonActive,
          disabled && styles.buttonDisabled,
        ]}
        onPress={handlePress}
        disabled={loading || disabled}
        accessibilityLabel={recording ? '停止录音' : '开始语音输入'}
        accessibilityRole="button"
        accessibilityState={{
          disabled: loading || disabled,
          selected: recording,
        }}
      >
        <Text style={styles.icon}>{recording ? '🛑' : '🎤'}</Text>
        <Text style={[styles.text, disabled && styles.textDisabled]}>
          {recording ? '录音中...' : '按下说话'}
        </Text>
      </TouchableOpacity>

      {loading && (
        <ActivityIndicator style={styles.loader} color="#0277BD" size="small" />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 12,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E1F5FE',
    borderRadius: 24,
    paddingVertical: 10,
    paddingHorizontal: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  buttonActive: {
    backgroundColor: '#B3E5FC',
  },
  buttonDisabled: {
    backgroundColor: '#F5F5F5',
    opacity: 0.6,
  },
  icon: {
    fontSize: 22,
    marginRight: 8,
  },
  text: {
    fontSize: 16,
    color: '#0277BD',
    fontWeight: '500',
  },
  textDisabled: {
    color: '#999',
  },
  loader: {
    marginLeft: 12,
  },
});
