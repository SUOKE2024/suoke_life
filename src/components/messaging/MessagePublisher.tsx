import React, { useState, useCallback } from 'react';
import {import { messageBusService, PublishRequest } from '../../services/messageBusService';
/**
* 消息发布组件
* 用于发布消息到指定主题
*/
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  ScrollView;
} from 'react-native';
interface MessagePublisherProps {
  topic: string;
  defaultPayload?: any;
  attributes?: Record<string, string>;
  onPublish?: (messageId: string) => void;
  onError?: (error: Error) => void;
  style?: any;
}
export const MessagePublisher: React.FC<MessagePublisherProps> = ({
  topic,
  defaultPayload = '',
  attributes = {},
  onPublish,
  onError,
  style;
}) => {
  const [payload, setPayload] = useState(;
    typeof defaultPayload === 'string' ? defaultPayload : JSON.stringify(defaultPayload, null, 2);
  );
  const [customAttributes, setCustomAttributes] = useState(;
    JSON.stringify(attributes, null, 2);
  );
  const [isPublishing, setIsPublishing] = useState(false);
  const [lastMessageId, setLastMessageId] = useState<string | null>(null);
  const handlePublish = useCallback(async () => {if (!payload.trim()) {Alert.alert("错误",请输入消息内容');
      return;
    }
    setIsPublishing(true);
    try {
      // 解析payload;
      let parsedPayload: any;
      try {
        parsedPayload = JSON.parse(payload);
      } catch {
        parsedPayload = payload; // 如果不是JSON，则作为字符串处理
      }
      // 解析attributes;
      let parsedAttributes: Record<string, string> = {};
      try {
        if (customAttributes.trim()) {
          parsedAttributes = JSON.parse(customAttributes);
        }
      } catch (error) {
        Alert.alert("错误",属性格式不正确，请输入有效的JSON');
        return;
      }
      const request: PublishRequest = {
        topic,
        payload: parsedPayload,
        attributes: { ...attributes, ...parsedAttributes }
      };
      const response = await messageBusService.publishMessage(request);
      if (response.success) {
        setLastMessageId(response.messageId);
        onPublish?.(response.messageId);
        Alert.alert('成功', `消息已发布\nID: ${response.messageId}`);
      } else {
        throw new Error(response.errorMessage || '发布失败');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '发布消息失败';
      onError?.(error instanceof Error ? error : new Error(errorMessage));
      Alert.alert('发布失败', errorMessage);
    } finally {
      setIsPublishing(false);
    }
  }, [topic, payload, customAttributes, attributes, onPublish, onError]);
  const handleClear = useCallback() => {setPayload(typeof defaultPayload === 'string' ? defaultPayload : JSON.stringify(defaultPayload, null, 2));
    setCustomAttributes(JSON.stringify(attributes, null, 2));
    setLastMessageId(null);
  }, [defaultPayload, attributes]);
  return (
    <View style={[styles.container, style]}>
      <Text style={styles.title}>发布消息到主题: {topic}</Text>
      <ScrollView style={styles.scrollView}>
        {// 消息内容输入}
        <View style={styles.section}>
          <Text style={styles.label}>消息内容 (JSON或文本):</Text>
          <TextInput;
            style={styles.textInput}
            value={payload}
            onChangeText={setPayload}
            placeholder="输入消息内容..."
            multiline;
            numberOfLines={6}
            textAlignVertical="top"
          />
        </View>
        {// 属性输入}
        <View style={styles.section}>
          <Text style={styles.label}>消息属性 (JSON):</Text>
          <TextInput;
            style={styles.attributesInput}
            value={customAttributes}
            onChangeText={setCustomAttributes}
            placeholder='{"key": "value"}'
            multiline;
            numberOfLines={3}
            textAlignVertical="top"
          />
        </View>
        {// 最后发布的消息ID}
        {lastMessageId && (
        <View style={styles.section}>
            <Text style={styles.label}>最后发布的消息ID:</Text>
            <Text style={styles.messageId}>{lastMessageId}</Text>
          </View>
        )}
      </ScrollView>
      {// 操作按钮}
      <View style={styles.buttonContainer}>
        <TouchableOpacity;
          style={[styles.button, styles.clearButton]}
          onPress={handleClear}
          disabled={isPublishing}
        >
          <Text style={styles.clearButtonText}>清空</Text>;
        </TouchableOpacity>;
;
        <TouchableOpacity;
          style={[styles.button, styles.publishButton, isPublishing && styles.disabledButton]};
          onPress={handlePublish};
          disabled={isPublishing};
        >;
          {isPublishing ? (;
            <ActivityIndicator color="#fff" size="small" />;
          ) : (;
            <Text style={styles.publishButtonText}>发布消息</Text>;
          )};
        </TouchableOpacity>;
      </View>;
    </View>;
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5'
  },
  title: {,
  fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333'
  },
  scrollView: {,
  flex: 1;
  },
  section: {,
  marginBottom: 16;
  },
  label: {,
  fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    color: '#555'
  },
  textInput: {,
  borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    backgroundColor: '#fff',
    fontSize: 14,
    minHeight: 120;
  },
  attributesInput: {,
  borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    backgroundColor: '#fff',
    fontSize: 14,
    minHeight: 80;
  },
  messageId: {,
  fontSize: 12,
    color: '#666',
    backgroundColor: '#e8f4f8',
    padding: 8,
    borderRadius: 4,
    fontFamily: 'monospace'
  },
  buttonContainer: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16;
  },
  button: {,
  flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: 4;
  },
  clearButton: {,
  backgroundColor: '#6c757d'
  },
  clearButtonText: {
      color: "#fff",
      fontSize: 16,fontWeight: '600';
  },publishButton: {backgroundColor: '#007bff';
  },publishButtonText: {
      color: "#fff",
      fontSize: 16,fontWeight: '600';
  },disabledButton: {backgroundColor: '#ccc';
  };
});
export default MessagePublisher;
