import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { AgentAvatar } from './AgentAvatar';
export type AgentType = 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';
interface AgentChatBubbleProps {
  agentType: AgentType;,
  message: string;
  emotion?: string;
  isVoice?: boolean;
  onPlayVoice?: () => void;
}
export const AgentChatBubble: React.FC<AgentChatBubbleProps> = ({
  agentType,
  message,
  emotion,
  isVoice,
  onPlayVoice}) => {
  return (
  <View style={styles.row}>
      <AgentAvatar agentType={agentType} emotion={emotion} size={40} />
      <View style={styles.bubble}>
        {isVoice ? ()
          <TouchableOpacity;
            onPress={onPlayVoice}
            style={styles.voiceBtn}
            accessibilityLabel="播放智能体语音回复"
            accessibilityRole="button"
          >
            <Text style={styles.voiceIcon}>🔊</Text>
            <Text style={styles.voiceText}>点击播放语音</Text>
          </TouchableOpacity>
        ) : (
          <Text style={styles.text}>{message}</Text>
        )}
      </View>
    </View>
  );
};
const styles = StyleSheet.create({
  row: {,
  flexDirection: 'row',
    alignItems: 'flex-end',
    marginVertical: 8},
  bubble: {,
  backgroundColor: '#F1F8E9',
    borderRadius: 16,
    padding: 12,
    marginLeft: 8,
    maxWidth: '75%'},
  text: {,
  fontSize: 16,
    color: '#333'},
  voiceBtn: {,
  flexDirection: 'row',
    alignItems: 'center'},
  voiceIcon: {,
  fontSize: 20,
    marginRight: 6},
  voiceText: {,
  fontSize: 15,
    color: '#00796B'}});