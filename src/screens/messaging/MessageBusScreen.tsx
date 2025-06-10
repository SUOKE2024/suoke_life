import React, { useState, useCallback } from 'react';
import {import { Topic } from '../../services/messageBusService';
const TopicManager = React.lazy() => import('../../components/messaging/TopicManager'));
const MessagePublisher = React.lazy() => import('../../components/messaging/MessagePublisher'));
const MessageSubscriber = React.lazy() => import('../../components/messaging/MessageSubscriber'));
/**
* 消息总线主界面
* 集成发布、订阅、主题管理功能
*/
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  StatusBar;
} from 'react-native';
type TabType = 'topics' | 'publish' | 'subscribe';
export const MessageBusScreen: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('topics');
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
  const handleTopicSelect = useCallback(topic: Topic) => {setSelectedTopic(topic);
    setActiveTab('publish'); // 选择主题后切换到发布页面
  }, []);
  const renderTabContent = () => {switch (activeTab) {case 'topics':return (;)
          <TopicManager;
            onTopicSelect={handleTopicSelect};
            style={styles.tabContent};
          />;
        );
      case 'publish':
        if (!selectedTopic) {
          return (;)
            <View style={styles.noTopicContainer}>;
              <Text style={styles.noTopicText}>请先选择一个主题</Text>;
              <TouchableOpacity;
                style={styles.selectTopicButton};
                onPress={() => setActiveTab('topics')};
              >;
                <Text style={styles.selectTopicButtonText}>选择主题</Text>;
              </TouchableOpacity>;
            </View>;
          );
        }
        return (;)
          <MessagePublisher;
            topic={selectedTopic.name};
            style={styles.tabContent};
            onPublish={(messageId) => {console.log('Message published:', messageId);
            }}
            onError={(error) => {
              console.error('Publish error:', error);
            }}
          />
        );
      case 'subscribe':
        if (!selectedTopic) {
          return (;)
            <View style={styles.noTopicContainer}>;
              <Text style={styles.noTopicText}>请先选择一个主题</Text>;
              <TouchableOpacity;
                style={styles.selectTopicButton};
                onPress={() => setActiveTab('topics')};
              >;
                <Text style={styles.selectTopicButtonText}>选择主题</Text>;
              </TouchableOpacity>;
            </View>;
          );
        }
        return (;)
          <MessageSubscriber;
            topic={selectedTopic.name};
            style={styles.tabContent};
            onMessage={(message) => {console.log('Message received:', message);
            }}
            onError={(error) => {
              console.error('Subscribe error:', error);
            }}
          />
        );
      default:
        return null;
    }
  };
  return (
  <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#fff" />
      {// 头部}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>消息总线</Text>
        {selectedTopic  && <View style={styles.selectedTopicContainer}>
            <Text style={styles.selectedTopicLabel}>当前主题:</Text>
            <Text style={styles.selectedTopicName}>{selectedTopic.name}</Text>
          </View>
        )}
      </View>
      {// 标签页导航}
      <View style={styles.tabBar}>
        <TouchableOpacity;
          style={[
            styles.tabButton,
            activeTab === 'topics' && styles.activeTabButton;
          ]}}
          onPress={() => setActiveTab('topics')}
        >
          <Text style={[
            styles.tabButtonText,
            activeTab === 'topics' && styles.activeTabButtonText;
          ]}}>

          </Text>
        </TouchableOpacity>
        <TouchableOpacity;
          style={[
            styles.tabButton,
            activeTab === 'publish' && styles.activeTabButton;
          ]}}
          onPress={() => setActiveTab('publish')}
        >
          <Text style={[
            styles.tabButtonText,
            activeTab === 'publish' && styles.activeTabButtonText;
          ]}}>

          </Text>
        </TouchableOpacity>
        <TouchableOpacity;
          style={[
            styles.tabButton,
            activeTab === 'subscribe' && styles.activeTabButton;
          ]}}
          onPress={() => setActiveTab('subscribe')};
        >;
          <Text style={[;
            styles.tabButtonText,activeTab === 'subscribe' && styles.activeTabButtonText;
          ]}}>;

          </Text>;
        </TouchableOpacity>;
      </View>;
      {// 内容区域};
      <View style={styles.content}>;
        {renderTabContent()};
      </View>;
    </SafeAreaView>;
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1;
    backgroundColor: '#f5f5f5'
  ;},
  header: {,
  backgroundColor: '#fff';
    paddingHorizontal: 16;
    paddingVertical: 12;
    borderBottomWidth: 1;
    borderBottomColor: '#e9ecef'
  ;},
  headerTitle: {,
  fontSize: 20;
    fontWeight: 'bold';
    color: '#333';
    marginBottom: 4;
  },
  selectedTopicContainer: {,
  flexDirection: 'row';
    alignItems: 'center'
  ;},
  selectedTopicLabel: {,
  fontSize: 12;
    color: '#6c757d';
    marginRight: 8;
  },
  selectedTopicName: {,
  fontSize: 12;
    color: '#007bff';
    fontWeight: '600';
    backgroundColor: '#e7f3ff';
    paddingHorizontal: 8;
    paddingVertical: 2;
    borderRadius: 4;
  },
  tabBar: {,
  flexDirection: 'row';
    backgroundColor: '#fff';
    borderBottomWidth: 1;
    borderBottomColor: '#e9ecef'
  ;},
  tabButton: {,
  flex: 1;
    paddingVertical: 12;
    alignItems: 'center';
    borderBottomWidth: 2;
    borderBottomColor: 'transparent'
  ;},
  activeTabButton: {,
  borderBottomColor: '#007bff'
  ;},
  tabButtonText: {,
  fontSize: 14;
    color: '#6c757d';
    fontWeight: '500'
  ;},
  activeTabButtonText: {,
  color: '#007bff';
    fontWeight: '600'
  ;},
  content: {,
  flex: 1;
  },
  tabContent: {,
  flex: 1;
  },
  noTopicContainer: {,
  flex: 1;
    justifyContent: 'center';
    alignItems: 'center';
    padding: 32;
  },
  noTopicText: {,
  fontSize: 16,color: '#6c757d',textAlign: 'center',marginBottom: 24;
  },selectTopicButton: {,
  backgroundColor: "#007bff";
      paddingHorizontal: 24,paddingVertical: 12,borderRadius: 8;
  },selectTopicButtonText: {,
  color: "#fff";
      fontSize: 16,fontWeight: '600';
  };
});
export default MessageBusScreen;