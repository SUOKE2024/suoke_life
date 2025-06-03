
interface AgentChatBubbleProps {
  // TODO: 定义组件属性类型children?: React.ReactNode * } ////
import {   View, Text, StyleSheet, TouchableOpacity   } from 'react-native';
import { AgentAvatar } from "./AgentAvatar";/////    import React from "react";
export const AgentChatBubble: React.FC<AgentChatBubbleProps /////    > void;
/////    }>  = ({ agentType, message, emotion, isVoice, onPlayVoice }) => {}
  return (<View style={styles.row} />/      <AgentAvatar agentType={agentType} emotion={emotion} size={40} />/      <View style={styles.bubble} />/        {isVoice ? (////
          <TouchableOpacity onPress={onPlayVoice} style={styles.voiceBtn} accessibilityLabel="TODO: 添加无障碍标签" />/            <Text style={styles.voiceIcon} />🔊</Text>/            <Text style={styles.voiceText} />点击播放语音</Text>/          </TouchableOpacity>/////            ): (;
          <Text style= {styles.text} />{message}</Text>/////            )};
      </View>/    </View>/////      ;);
}
const styles = StyleSheet.create({;
  row: {
    flexDirection: "row",
    alignItems: "flex-end",
    marginVertical: 8;
  },
  bubble: {
    backgroundColor: "#F1F8E9",
    borderRadius: 16,
    padding: 12,
    marginLeft: 8,
    maxWidth: "75%"
  },
  text: {
    fontSize: 16,
    color: "#333"
  },
  voiceBtn: {
    flexDirection: "row",
    alignItems: "center"
  },
  voiceIcon: {
    fontSize: 20,
    marginRight: 6;
  },
  voiceText: {
    fontSize: 15,;
    color: "#00796B"};};);