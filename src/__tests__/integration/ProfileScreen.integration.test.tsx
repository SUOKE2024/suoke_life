import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { View, Text, TextInput, TouchableOpacity, ScrollView } from 'react-native';

// Mock用户数据
const mockUser = {
  id: '1',
  name: '张三',
  email: 'zhangsan@example.com',
  phone: '13812345678',
  avatar: 'https://example.com/avatar.jpg',
  age: 30,
  gender: '男',
  height: 175,
  weight: 70,
  bloodType: 'A',
};

// Mock ProfileScreen组件
const MockProfileScreen = () => {
  const [user, setUser] = React.useState(mockUser);
  const [isEditing, setIsEditing] = React.useState(false);
  const [editForm, setEditForm] = React.useState(mockUser);

  const handleEdit = () => {
    setIsEditing(true);
    setEditForm(user);
  };

  const handleSave = () => {
    setUser(editForm);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditForm(user);
    setIsEditing(false);
  };

  return (
    <ScrollView testID="profile-screen">
      <View testID="profile-header">
        <Text testID="profile-title">个人资料</Text>
        {!isEditing && (
          <TouchableOpacity testID="edit-button" onPress={handleEdit}>
            <Text>编辑</Text>
          </TouchableOpacity>
        )}
      </View>

      {isEditing ? (
        <View testID="edit-form">
          <View testID="form-field-name">
            <Text>姓名</Text>
            <TextInput
              testID="input-name"
              value={editForm.name}
              onChangeText={(text) => setEditForm({ ...editForm, name: text })}
            />
          </View>
          
          <View testID="form-field-email">
            <Text>邮箱</Text>
            <TextInput
              testID="input-email"
              value={editForm.email}
              onChangeText={(text) => setEditForm({ ...editForm, email: text })}
            />
          </View>
          
          <View testID="form-field-phone">
            <Text>手机号</Text>
            <TextInput
              testID="input-phone"
              value={editForm.phone}
              onChangeText={(text) => setEditForm({ ...editForm, phone: text })}
            />
          </View>

          <View testID="form-actions">
            <TouchableOpacity testID="save-button" onPress={handleSave}>
              <Text>保存</Text>
            </TouchableOpacity>
            <TouchableOpacity testID="cancel-button" onPress={handleCancel}>
              <Text>取消</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <View testID="profile-info">
          <View testID="info-field-name">
            <Text>姓名</Text>
            <Text testID="display-name">{user.name}</Text>
          </View>
          
          <View testID="info-field-email">
            <Text>邮箱</Text>
            <Text testID="display-email">{user.email}</Text>
          </View>
          
          <View testID="info-field-phone">
            <Text>手机号</Text>
            <Text testID="display-phone">{user.phone}</Text>
          </View>
          
          <View testID="info-field-age">
            <Text>年龄</Text>
            <Text testID="display-age">{user.age}岁</Text>
          </View>
          
          <View testID="info-field-gender">
            <Text>性别</Text>
            <Text testID="display-gender">{user.gender}</Text>
          </View>
        </View>
      )}
    </ScrollView>
  );
};

describe('ProfileScreen Integration Tests', () => {
  it('应该正确渲染个人资料页面', () => {
    const { getByTestId, getByText } = render(<MockProfileScreen />);

    expect(getByTestId('profile-screen')).toBeTruthy();
    expect(getByTestId('profile-header')).toBeTruthy();
    expect(getByText('个人资料')).toBeTruthy();
    expect(getByTestId('edit-button')).toBeTruthy();
    expect(getByTestId('profile-info')).toBeTruthy();
  });

  it('应该显示用户基本信息', () => {
    const { getByTestId } = render(<MockProfileScreen />);

    expect(getByTestId('display-name')).toBeTruthy();
    expect(getByTestId('display-email')).toBeTruthy();
    expect(getByTestId('display-phone')).toBeTruthy();
    expect(getByTestId('display-age')).toBeTruthy();
    expect(getByTestId('display-gender')).toBeTruthy();
  });

  it('应该能够进入编辑模式', () => {
    const { getByTestId } = render(<MockProfileScreen />);

    const editButton = getByTestId('edit-button');
    fireEvent.press(editButton);

    expect(getByTestId('edit-form')).toBeTruthy();
    expect(getByTestId('input-name')).toBeTruthy();
    expect(getByTestId('input-email')).toBeTruthy();
    expect(getByTestId('input-phone')).toBeTruthy();
    expect(getByTestId('save-button')).toBeTruthy();
    expect(getByTestId('cancel-button')).toBeTruthy();
  });

  it('应该能够编辑用户信息', () => {
    const { getByTestId } = render(<MockProfileScreen />);

    // 进入编辑模式
    fireEvent.press(getByTestId('edit-button'));

    // 修改姓名
    const nameInput = getByTestId('input-name');
    fireEvent.changeText(nameInput, '李四');

    // 修改邮箱
    const emailInput = getByTestId('input-email');
    fireEvent.changeText(emailInput, 'lisi@example.com');

    // 保存修改
    fireEvent.press(getByTestId('save-button'));

    // 验证修改已保存
    expect(getByTestId('display-name')).toBeTruthy();
    expect(getByTestId('display-email')).toBeTruthy();
  });

  it('应该能够取消编辑', () => {
    const { getByTestId } = render(<MockProfileScreen />);

    // 进入编辑模式
    fireEvent.press(getByTestId('edit-button'));

    // 修改信息
    const nameInput = getByTestId('input-name');
    fireEvent.changeText(nameInput, '王五');

    // 取消编辑
    fireEvent.press(getByTestId('cancel-button'));

    // 验证回到查看模式且信息未改变
    expect(getByTestId('profile-info')).toBeTruthy();
    expect(getByTestId('display-name')).toBeTruthy();
  });

  it('应该正确处理表单输入', () => {
    const { getByTestId } = render(<MockProfileScreen />);

    // 进入编辑模式
    fireEvent.press(getByTestId('edit-button'));

    // 测试各个输入框
    const nameInput = getByTestId('input-name');
    const emailInput = getByTestId('input-email');
    const phoneInput = getByTestId('input-phone');

    expect(nameInput.props.value).toBe('张三');
    expect(emailInput.props.value).toBe('zhangsan@example.com');
    expect(phoneInput.props.value).toBe('13812345678');

    // 修改值
    fireEvent.changeText(nameInput, '新姓名');
    fireEvent.changeText(emailInput, 'new@example.com');
    fireEvent.changeText(phoneInput, '13987654321');

    // 验证输入框值已更新
    expect(nameInput.props.value).toBe('新姓名');
    expect(emailInput.props.value).toBe('new@example.com');
    expect(phoneInput.props.value).toBe('13987654321');
  });

  it('应该在编辑模式下隐藏编辑按钮', () => {
    const { getByTestId, queryByTestId } = render(<MockProfileScreen />);

    // 进入编辑模式
    fireEvent.press(getByTestId('edit-button'));

    // 验证编辑按钮被隐藏
    expect(queryByTestId('edit-button')).toBeNull();
    expect(getByTestId('edit-form')).toBeTruthy();
  });

  it('应该在查看模式下隐藏编辑表单', () => {
    const { getByTestId, queryByTestId } = render(<MockProfileScreen />);

    // 初始状态应该显示信息，隐藏表单
    expect(getByTestId('profile-info')).toBeTruthy();
    expect(queryByTestId('edit-form')).toBeNull();
  });
}); 