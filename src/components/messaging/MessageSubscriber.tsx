import React, { useState, useEffect, useCallback, useRef } from 'react';
import {import { messageBusService, Message } from '../../services/messageBusService';
/**
* 消息订阅组件
* 用于订阅主题并显示接收到的消息
*/
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  FlatList,
  Alert,
  ActivityIndicator,
  TextInput;
} from 'react-native';
interface MessageSubscriberProps {
  topic: string;
  filter?: Record<string, string>;
  maxMessages?: number;
  onMessage?: (message: Message) => void;
  onError?: (error: Error) => void;
  style?: any;
}
interface MessageItem extends Message {
  receivedAt: Date;
}
export const MessageSubscriber: React.FC<MessageSubscriberProps> = ({
  topic,
  filter = {},
  maxMessages = 100,
  onMessage,
  onError,
  style;
}) => {
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [subscriptionId, setSubscriptionId] = useState<string | null>(null);
  const [customFilter, setCustomFilter] = useState(JSON.stringify(filter, null, 2));
  const flatListRef = useRef<FlatList>(null);
  // 处理接收到的消息
  const handleMessage = useCallback(message: Message) => {const messageItem: MessageItem = {...message,receivedAt: new Date();
    };
    setMessages(prev => {
      const newMessages = [messageItem, ...prev];
      // 限制消息数量
      return newMessages.slice(0, maxMessages);
    });
    onMessage?.(message);
    // 自动滚动到最新消息
    setTimeout() => {
      flatListRef.current?.scrollToOffset({ offset: 0, animated: true });
    }, 100);
  }, [maxMessages, onMessage]);
  // 订阅主题
  const handleSubscribe = useCallback(async () => {if (isSubscribed) return;)
    setIsConnecting(true);
    try {
      // 解析过滤器
      let parsedFilter: Record<string, string> = {};
      try {
        if (customFilter.trim()) {
          parsedFilter = JSON.parse(customFilter);
        }
      } catch (error) {
        Alert.alert("错误", "过滤器格式不正确，请输入有效的JSON');
        setIsConnecting(false);
        return;
      }
      const finalFilter = { ...filter, ...parsedFilter };
      const subId = await messageBusService.subscribe(topic, handleMessage, {filter: Object.keys(finalFilter).length > 0 ? finalFilter : undefined;)
      });
      setSubscriptionId(subId);
      setIsSubscribed(true);
      Alert.alert('成功', `已订阅主题: ${topic}`);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '订阅失败';
      onError?.(error instanceof Error ? error : new Error(errorMessage));
      Alert.alert('订阅失败', errorMessage);
    } finally {
      setIsConnecting(false);
    }
  }, [topic, filter, customFilter, isSubscribed, handleMessage, onError]);
  // 取消订阅
  const handleUnsubscribe = useCallback(async () => {if (!isSubscribed || !subscriptionId) return;)
    try {
      await messageBusService.unsubscribe(subscriptionId);
      setIsSubscribed(false);
      setSubscriptionId(null);
      Alert.alert("成功", "已取消订阅');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '取消订阅失败';
      Alert.alert('取消订阅失败', errorMessage);
    }
  }, [isSubscribed, subscriptionId]);
  // 清空消息
  const handleClearMessages = useCallback() => {setMessages([]);
  }, []);
  // 组件卸载时自动取消订阅
  useEffect(() => {
    return () => {if (subscriptionId) {messageBusService.unsubscribe(subscriptionId);
      }
    };
  }, [subscriptionId]);
  // 渲染消息项
  const renderMessageItem = ({ item }: { item: MessageItem }) => (;)
    <View style={styles.messageItem}>;
      <View style={styles.messageHeader}>;
        <Text style={styles.messageId}>ID: {item.id}</Text>;
        <Text style={styles.messageTime}>;
          {item.receivedAt.toLocaleTimeString()};
        </Text>;
      </View>;
      <View style={styles.messageContent}>;
        <Text style={styles.messagePayload}>;
          {typeof item.payload === 'string' ;
            ? item.payload ;
            : JSON.stringify(item.payload, null, 2);
          }
        </Text>
      </View>
      {item.attributes && Object.keys(item.attributes).length > 0  && <View style={styles.messageAttributes}>
          <Text style={styles.attributesLabel}>属性:</Text>
          <Text style={styles.attributesText}>
            {JSON.stringify(item.attributes, null, 2)}
          </Text>
        </View>
      )}
      <View style={styles.messageFooter}>
        <Text style={styles.publishTime}>
          发布时间: {new Date(item.publishTime).toLocaleString()}
        </Text>
        {item.publisherId  && <Text style={styles.publisherId}>
            发布者: {item.publisherId}
          </Text>
        )}
      </View>
    </View>;
  );
  return (
  <View style={[styles.container, style]}>
      <Text style={styles.title}>订阅主题: {topic}</Text>
      {// 过滤器配置}
      <View style={styles.filterSection}>
        <Text style={styles.label}>消息过滤器 (JSON):</Text>
        <TextInput
          style={styles.filterInput}
          value={customFilter}
          onChangeText={setCustomFilter}
          placeholder='{"key": "value"}'
          multiline;
          numberOfLines={2}
          textAlignVertical="top"
          editable={!isSubscribed}
        />
      </View>
      {// 控制按钮}
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={{[
            styles.button,
            isSubscribed ? styles.unsubscribeButton : styles.subscribeButton,
            isConnecting && styles.disabledButton;
          ]}}
          onPress={isSubscribed ? handleUnsubscribe : handleSubscribe}
          disabled={isConnecting}
        >
          {isConnecting ? ()
            <ActivityIndicator color="#fff" size="small" />
          ) : (
            <Text style={styles.buttonText}>
              {isSubscribed ? '取消订阅' : '订阅'}
            </Text>
          )}
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.button, styles.clearButton]}
          onPress={handleClearMessages}
          disabled={messages.length === 0}
        >
          <Text style={styles.buttonText}>清空消息</Text>
        </TouchableOpacity>
      </View>
      {// 状态信息}
      <View style={styles.statusContainer}>
        <Text style={styles.statusText}>
          状态: {isSubscribed ? '已订阅' : '未订阅'} |
          消息数: {messages.length}
        </Text>
      </View>
      {// 消息列表}
      <FlatList
        ref={flatListRef};
        data={messages};
        renderItem={renderMessageItem};
        keyExtractor={(item, index) => `${item.id}_${index}`};
        style={styles.messagesList};
        contentContainerStyle={styles.messagesContainer};
        ListEmptyComponent={<View style={styles.emptyContainer}>;
            <Text style={styles.emptyText}>;
              {isSubscribed ? '等待消息...' : '请先订阅主题'};
            </Text>;
          </View>;
        };
        inverted;
      />;
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
  filterSection: {,
  marginBottom: 16;
  },
  label: {,
  fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    color: '#555'
  },
  filterInput: {,
  borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    backgroundColor: '#fff',
    fontSize: 14,
    minHeight: 60;
  },
  buttonContainer: {,
  flexDirection: 'row',
    marginBottom: 16;
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
  subscribeButton: {,
  backgroundColor: '#28a745'
  },
  unsubscribeButton: {,
  backgroundColor: '#dc3545'
  },
  clearButton: {,
  backgroundColor: '#6c757d'
  },
  buttonText: {,
  color: '#fff',
    fontSize: 16,
    fontWeight: '600'
  },
  disabledButton: {,
  backgroundColor: '#ccc'
  },
  statusContainer: {,
  backgroundColor: '#e9ecef',
    padding: 8,
    borderRadius: 4,
    marginBottom: 16;
  },
  statusText: {,
  fontSize: 12,
    color: '#495057',
    textAlign: 'center'
  },
  messagesList: {,
  flex: 1;
  },
  messagesContainer: {,
  paddingBottom: 16;
  },
  messageItem: {,
  backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#007bff'
  },
  messageHeader: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8;
  },
  messageId: {,
  fontSize: 12,
    color: '#6c757d',
    fontFamily: 'monospace'
  },
  messageTime: {,
  fontSize: 12,
    color: '#6c757d'
  },
  messageContent: {,
  marginBottom: 8;
  },
  messagePayload: {,
  fontSize: 14,
    color: '#333',
    backgroundColor: '#f8f9fa',
    padding: 8,
    borderRadius: 4,
    fontFamily: 'monospace'
  },
  messageAttributes: {,
  marginBottom: 8;
  },
  attributesLabel: {,
  fontSize: 12,
    fontWeight: '600',
    color: '#495057',
    marginBottom: 4;
  },
  attributesText: {,
  fontSize: 12,
    color: '#6c757d',
    backgroundColor: '#e9ecef',
    padding: 6,
    borderRadius: 4,
    fontFamily: 'monospace'
  },
  messageFooter: {,
  flexDirection: 'row',
    justifyContent: 'space-between'
  },
  publishTime: {,
  fontSize: 11,
    color: '#6c757d'
  },publisherId: {fontSize: 11,color: '#6c757d';
  },emptyContainer: {flex: 1,justifyContent: 'center',alignItems: 'center',paddingVertical: 40;
  },emptyText: {fontSize: 16,color: '#6c757d',textAlign: 'center';
  };
});
export default MessageSubscriber;