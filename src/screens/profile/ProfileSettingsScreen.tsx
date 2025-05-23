import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
  Switch,
} from 'react-native';
import {
  Appbar,
  Card,
  Title,
  Paragraph,
  Button,
  TextInput,
  Text,
  Surface,
  List,
  Divider,
  Avatar,
  TouchableRipple,
  SegmentedButtons,
} from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useTheme } from 'react-native-paper';
import { useTranslation } from 'react-i18next';

interface ProfileSettingsScreenProps {
  navigation: any;
}

interface UserProfile {
  id: string;
  name: string;
  email: string;
  phone: string;
  avatar: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  height: number;
  weight: number;
  bloodType: string;
  allergies: string[];
  medicalHistory: string[];
  emergencyContact: {
    name: string;
    phone: string;
    relationship: string;
  };
}

interface AppSettings {
  notifications: {
    medication: boolean;
    exercise: boolean;
    checkup: boolean;
    articles: boolean;
  };
  privacy: {
    dataSharing: boolean;
    analytics: boolean;
    location: boolean;
  };
  preferences: {
    language: 'zh' | 'en';
    theme: 'light' | 'dark' | 'auto';
    units: 'metric' | 'imperial';
  };
}

const ProfileSettingsScreen: React.FC<ProfileSettingsScreenProps> = ({ navigation }) => {
  const theme = useTheme();
  const { t } = useTranslation();
  
  const [profile, setProfile] = useState<UserProfile>({
    id: '1',
    name: '张三',
    email: 'zhangsan@example.com',
    phone: '138****8888',
    avatar: '',
    age: 28,
    gender: 'male',
    height: 175,
    weight: 70,
    bloodType: 'A',
    allergies: ['花粉', '海鲜'],
    medicalHistory: ['高血压家族史'],
    emergencyContact: {
      name: '李四',
      phone: '139****9999',
      relationship: '配偶',
    },
  });

  const [settings, setSettings] = useState<AppSettings>({
    notifications: {
      medication: true,
      exercise: true,
      checkup: true,
      articles: false,
    },
    privacy: {
      dataSharing: false,
      analytics: true,
      location: true,
    },
    preferences: {
      language: 'zh',
      theme: 'auto',
      units: 'metric',
    },
  });

  const [editingProfile, setEditingProfile] = useState(false);
  const [tempProfile, setTempProfile] = useState(profile);

  const bloodTypes = ['A', 'B', 'AB', 'O', '未知'];
  const genderOptions = [
    { value: 'male', label: '男' },
    { value: 'female', label: '女' },
    { value: 'other', label: '其他' },
  ];

  const languageOptions = [
    { value: 'zh', label: '中文' },
    { value: 'en', label: 'English' },
  ];

  const themeOptions = [
    { value: 'light', label: '浅色' },
    { value: 'dark', label: '深色' },
    { value: 'auto', label: '跟随系统' },
  ];

  const handleSaveProfile = () => {
    setProfile(tempProfile);
    setEditingProfile(false);
    Alert.alert('成功', '个人资料已更新');
  };

  const handleCancelEdit = () => {
    setTempProfile(profile);
    setEditingProfile(false);
  };

  const updateNotificationSetting = (key: keyof AppSettings['notifications'], value: boolean) => {
    setSettings(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [key]: value,
      },
    }));
  };

  const updatePrivacySetting = (key: keyof AppSettings['privacy'], value: boolean) => {
    setSettings(prev => ({
      ...prev,
      privacy: {
        ...prev.privacy,
        [key]: value,
      },
    }));
  };

  const updatePreference = (category: keyof AppSettings['preferences'], value: any) => {
    setSettings(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [category]: value,
      },
    }));
  };

  const renderProfileSection = () => (
    <Card style={styles.card}>
      <Card.Content>
        <View style={styles.profileHeader}>
          <Avatar.Text size={64} label={profile.name.charAt(0)} />
          <View style={styles.profileInfo}>
            <Title>{profile.name}</Title>
            <Paragraph>{profile.email}</Paragraph>
            <Paragraph>{profile.phone}</Paragraph>
          </View>
          <Button
            mode={editingProfile ? 'contained' : 'outlined'}
            onPress={() => setEditingProfile(!editingProfile)}
            compact
          >
            {editingProfile ? '取消' : '编辑'}
          </Button>
        </View>

        {editingProfile && (
          <View style={styles.editForm}>
            <Divider style={styles.divider} />
            
            <TextInput
              label="姓名"
              value={tempProfile.name}
              onChangeText={(text) => setTempProfile({ ...tempProfile, name: text })}
              style={styles.input}
              mode="outlined"
            />

            <TextInput
              label="邮箱"
              value={tempProfile.email}
              onChangeText={(text) => setTempProfile({ ...tempProfile, email: text })}
              style={styles.input}
              mode="outlined"
              keyboardType="email-address"
            />

            <TextInput
              label="手机号"
              value={tempProfile.phone}
              onChangeText={(text) => setTempProfile({ ...tempProfile, phone: text })}
              style={styles.input}
              mode="outlined"
              keyboardType="phone-pad"
            />

            <View style={styles.row}>
              <TextInput
                label="年龄"
                value={tempProfile.age.toString()}
                onChangeText={(text) => setTempProfile({ ...tempProfile, age: parseInt(text) || 0 })}
                style={[styles.input, styles.halfInput]}
                mode="outlined"
                keyboardType="numeric"
              />
              
              <View style={styles.halfInput}>
                <Text style={styles.inputLabel}>性别</Text>
                <SegmentedButtons
                  value={tempProfile.gender}
                  onValueChange={(value) => setTempProfile({ ...tempProfile, gender: value as any })}
                  buttons={genderOptions}
                  style={styles.segmentedButtons}
                />
              </View>
            </View>

            <View style={styles.row}>
              <TextInput
                label="身高 (cm)"
                value={tempProfile.height.toString()}
                onChangeText={(text) => setTempProfile({ ...tempProfile, height: parseInt(text) || 0 })}
                style={[styles.input, styles.halfInput]}
                mode="outlined"
                keyboardType="numeric"
              />
              
              <TextInput
                label="体重 (kg)"
                value={tempProfile.weight.toString()}
                onChangeText={(text) => setTempProfile({ ...tempProfile, weight: parseInt(text) || 0 })}
                style={[styles.input, styles.halfInput]}
                mode="outlined"
                keyboardType="numeric"
              />
            </View>

            <View style={styles.actionButtons}>
              <Button
                mode="outlined"
                onPress={handleCancelEdit}
                style={styles.actionButton}
              >
                取消
              </Button>
              <Button
                mode="contained"
                onPress={handleSaveProfile}
                style={styles.actionButton}
              >
                保存
              </Button>
            </View>
          </View>
        )}
      </Card.Content>
    </Card>
  );

  const renderHealthInfoSection = () => (
    <Card style={styles.card}>
      <Card.Content>
        <Title style={styles.sectionTitle}>健康信息</Title>
        
        <List.Item
          title="血型"
          description={profile.bloodType}
          left={props => <List.Icon {...props} icon="water" />}
          right={props => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {/* 编辑血型 */}}
        />
        
        <List.Item
          title="过敏史"
          description={profile.allergies.join(', ') || '无'}
          left={props => <List.Icon {...props} icon="alert-circle" />}
          right={props => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {/* 编辑过敏史 */}}
        />
        
        <List.Item
          title="病史"
          description={profile.medicalHistory.join(', ') || '无'}
          left={props => <List.Icon {...props} icon="medical-bag" />}
          right={props => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {/* 编辑病史 */}}
        />
        
        <List.Item
          title="紧急联系人"
          description={`${profile.emergencyContact.name} (${profile.emergencyContact.relationship})`}
          left={props => <List.Icon {...props} icon="account-heart" />}
          right={props => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {/* 编辑紧急联系人 */}}
        />
      </Card.Content>
    </Card>
  );

  const renderNotificationSettings = () => (
    <Card style={styles.card}>
      <Card.Content>
        <Title style={styles.sectionTitle}>通知设置</Title>
        
        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>用药提醒</Text>
            <Text style={styles.settingDescription}>按时服药提醒</Text>
          </View>
          <Switch
            value={settings.notifications.medication}
            onValueChange={(value) => updateNotificationSetting('medication', value)}
          />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>运动提醒</Text>
            <Text style={styles.settingDescription}>每日运动提醒</Text>
          </View>
          <Switch
            value={settings.notifications.exercise}
            onValueChange={(value) => updateNotificationSetting('exercise', value)}
          />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>体检提醒</Text>
            <Text style={styles.settingDescription}>定期体检提醒</Text>
          </View>
          <Switch
            value={settings.notifications.checkup}
            onValueChange={(value) => updateNotificationSetting('checkup', value)}
          />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>文章推送</Text>
            <Text style={styles.settingDescription}>健康文章推荐</Text>
          </View>
          <Switch
            value={settings.notifications.articles}
            onValueChange={(value) => updateNotificationSetting('articles', value)}
          />
        </View>
      </Card.Content>
    </Card>
  );

  const renderPrivacySettings = () => (
    <Card style={styles.card}>
      <Card.Content>
        <Title style={styles.sectionTitle}>隐私设置</Title>
        
        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>数据共享</Text>
            <Text style={styles.settingDescription}>与医疗机构共享健康数据</Text>
          </View>
          <Switch
            value={settings.privacy.dataSharing}
            onValueChange={(value) => updatePrivacySetting('dataSharing', value)}
          />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>数据分析</Text>
            <Text style={styles.settingDescription}>允许匿名数据分析</Text>
          </View>
          <Switch
            value={settings.privacy.analytics}
            onValueChange={(value) => updatePrivacySetting('analytics', value)}
          />
        </View>

        <View style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>位置服务</Text>
            <Text style={styles.settingDescription}>获取位置信息提供服务</Text>
          </View>
          <Switch
            value={settings.privacy.location}
            onValueChange={(value) => updatePrivacySetting('location', value)}
          />
        </View>
      </Card.Content>
    </Card>
  );

  const renderPreferences = () => (
    <Card style={styles.card}>
      <Card.Content>
        <Title style={styles.sectionTitle}>偏好设置</Title>
        
        <View style={styles.preferenceItem}>
          <Text style={styles.preferenceLabel}>语言</Text>
          <SegmentedButtons
            value={settings.preferences.language}
            onValueChange={(value) => updatePreference('language', value)}
            buttons={languageOptions}
            style={styles.preferenceButtons}
          />
        </View>

        <View style={styles.preferenceItem}>
          <Text style={styles.preferenceLabel}>主题</Text>
          <SegmentedButtons
            value={settings.preferences.theme}
            onValueChange={(value) => updatePreference('theme', value)}
            buttons={themeOptions}
            style={styles.preferenceButtons}
          />
        </View>
      </Card.Content>
    </Card>
  );

  const renderAccountActions = () => (
    <Card style={styles.card}>
      <Card.Content>
        <Title style={styles.sectionTitle}>账户操作</Title>
        
        <List.Item
          title="修改密码"
          left={props => <List.Icon {...props} icon="lock" />}
          right={props => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {/* 修改密码 */}}
        />
        
        <List.Item
          title="数据导出"
          left={props => <List.Icon {...props} icon="download" />}
          right={props => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {/* 数据导出 */}}
        />
        
        <List.Item
          title="清除缓存"
          left={props => <List.Icon {...props} icon="delete-sweep" />}
          right={props => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {
            Alert.alert('确认', '确定要清除缓存吗？', [
              { text: '取消', style: 'cancel' },
              { text: '确定', onPress: () => Alert.alert('成功', '缓存已清除') },
            ]);
          }}
        />
        
        <List.Item
          title="注销账户"
          titleStyle={{ color: theme.colors.error }}
          left={props => <List.Icon {...props} icon="account-remove" color={theme.colors.error} />}
          right={props => <List.Icon {...props} icon="chevron-right" />}
          onPress={() => {
            Alert.alert(
              '警告',
              '注销账户将永久删除您的所有数据，此操作不可恢复。确定要继续吗？',
              [
                { text: '取消', style: 'cancel' },
                { text: '确定注销', style: 'destructive', onPress: () => {/* 注销账户 */} },
              ]
            );
          }}
        />
      </Card.Content>
    </Card>
  );

  return (
    <SafeAreaView style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="个人设置" />
      </Appbar.Header>

      <ScrollView style={styles.content}>
        {renderProfileSection()}
        {renderHealthInfoSection()}
        {renderNotificationSettings()}
        {renderPrivacySettings()}
        {renderPreferences()}
        {renderAccountActions()}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  card: {
    marginBottom: 16,
    borderRadius: 12,
  },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  profileInfo: {
    flex: 1,
    marginLeft: 16,
  },
  editForm: {
    marginTop: 16,
  },
  divider: {
    marginBottom: 16,
  },
  input: {
    marginBottom: 16,
  },
  row: {
    flexDirection: 'row',
    gap: 16,
  },
  halfInput: {
    flex: 1,
  },
  inputLabel: {
    fontSize: 12,
    marginBottom: 8,
    color: '#666',
  },
  segmentedButtons: {
    marginBottom: 16,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 16,
    marginTop: 16,
  },
  actionButton: {
    flex: 1,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
  },
  settingInfo: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 12,
    color: '#666',
  },
  preferenceItem: {
    marginBottom: 16,
  },
  preferenceLabel: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 8,
  },
  preferenceButtons: {
    marginBottom: 8,
  },
});

export default ProfileSettingsScreen;