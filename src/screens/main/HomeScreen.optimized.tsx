import React, { useEffect } from 'react';
import {
  StyleSheet,
  FlatList,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, spacing } from '../../constants/theme';

// 导入新的组件和hooks
import {
  ScreenHeader,
  ChatMessage,
  MessageInput,
  AgentSelector,
} from '../components';
import { useAgent, useChat } from '../hooks';
import { Message } from '../components/ChatMessage';

export const HomeScreenOptimized: React.FC = () => {
  // 使用自定义hooks
  const { selectedAgent, switchAgent, generateAgentResponse } = useAgent('xiaoai');
  const { 
    messages, 
    isTyping, 
    sendMessage, 
    addMessage, 
    flatListRef, 
  } = useChat([
    {
      id: '1',
      text: '您好！我是小艾，您的健康助手。有什么可以帮助您的吗？',
      sender: 'xiaoai',
      timestamp: new Date(),
    },
  ]);

  // 处理智能体切换
  const handleAgentSwitch = (agent: typeof selectedAgent) => {
    switchAgent(agent);
    
    // 添加切换消息
    const switchMessage: Message = {
      id: Date.now().toString(),
      text: `您好！我是${agent === 'xiaoai' ? '小艾' : agent === 'xiaoke' ? '小克' : agent === 'laoke' ? '老克' : '索儿'}，很高兴为您服务！`,
      sender: agent,
      timestamp: new Date(),
    };
    addMessage(switchMessage);
  };

  // 处理发送消息
  const handleSendMessage = async (text: string) => {
    await sendMessage(text, selectedAgent, generateAgentResponse);
  };

  // 渲染消息项
  const renderMessage = ({ item }: { item: Message }) => (
    <ChatMessage
      message={item}
      showTimestamp={true}
      showAvatar={true}
    />
  );

  // 自动滚动到底部
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages.length, flatListRef]);

  return (
    <SafeAreaView style={styles.container}>
      {/* 头部 */}
      <ScreenHeader
        title="索克生活"
        subtitle="AI健康助手"
        backgroundColor={colors.primary}
        rightIcon="settings"
        onRightPress={() => {
          // 导航到设置页面
          console.log('打开设置');
        }}
      />

      {/* 智能体选择器 */}
      <AgentSelector
        selectedAgent={selectedAgent}
        onAgentSelect={handleAgentSwitch}
        horizontal={true}
        showSpecialty={false}
        size="small"
        style={styles.agentSelector}
      />

      {/* 聊天消息列表 */}
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContent}
        showsVerticalScrollIndicator={false}
        onContentSizeChange={() => {
          flatListRef.current?.scrollToEnd({ animated: true });
        }}
      />

      {/* 消息输入框 */}
      <MessageInput
        onSend={handleSendMessage}
        placeholder={`向${selectedAgent === 'xiaoai' ? '小艾' : selectedAgent === 'xiaoke' ? '小克' : selectedAgent === 'laoke' ? '老克' : '索儿'}发送消息...`}
        isTyping={isTyping}
        showVoiceButton={true}
        showAttachButton={true}
        onVoicePress={() => {
          console.log('语音输入');
        }}
        onAttachPress={() => {
          console.log('附件');
        }}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  agentSelector: {
    backgroundColor: colors.surface,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  messagesList: {
    flex: 1,
  },
  messagesContent: {
    paddingVertical: spacing.sm,
  },
}); 