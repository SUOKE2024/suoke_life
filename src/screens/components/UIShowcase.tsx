import {   ScrollView, StyleSheet, View   } from 'react-native';
import { colors, spacing } from '../../constants/theme'/importColorPreview from './ColorPreview';/;
// 索克生活 - UI组件展示页面   展示所有UI组件的使用示例
importReact,{ useState } from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor'/  Button,;
  Text,
  Input,
  Card,
  Container,
  Avatar,
  Badge,
  Loading,
  Modal,
  AgentAvatar,
  Divider,
  Switch,
  Checkbox,
  Radio,
  { Slider } from '../../components/ui'/const UIShowcase: React.FC = () => {
  // 性能监控 *   const performanceMonitor = usePerformanceMonitor('UIShowcase', { */
    trackRender: true,
    trackMemory: true,
    warnThreshold: 50, // ms *   ;};); */
  const [modalVisible, setModalVisible] = useState<boolean>(fals;e;)
  const [inputValue, setInputValue] = useState<string>(';';);
  const [switchValue, setSwitchValue] = useState<boolean>(fals;e;);
  const [checkboxValue, setCheckboxValue] = useState<boolean>(fals;e;)
  const [radioValue, setRadioValue] = useState<string>('option1;';);
  const [sliderValue, setSliderValue] = useState<number>(5;0;);
  const [showColorPreview, setShowColorPreview] = useState<boolean>(fals;e;);
  if (showColorPreview) {
    return <ColorPreview onBack={() = /> setShowColorPreview(false)} ;/;>;/  }
  // 记录渲染性能 *  */
  performanceMonitor.recordRender()
  return (
    <ScrollView style={styles.container} />/      <Container padding="lg" />/        <Text variant="h1" style={styles.title} />/          索克生活 UI 组件库
        </Text>/
        {// 颜色预览按钮 }/        <View style={styles.colorPreviewSection} />/          <Button
            title="查看品牌色彩"
            variant="secondary"
            onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> setShowColorPreview(true)}/            style={styles.colorPreviewButton} />/          <Text variant="caption" style={styles.colorPreviewText} />/            查看更新后的索克绿和索克橙品牌色彩
          </Text>/        </View>/
        <Divider margin="lg" />/
        {// 文本组件 }/        <Card style={styles.section} />/          <Text variant="h3" style={styles.sectionTitle} />文本组件</Text>/          <Text variant="h1" />标题 H1</Text>/          <Text variant="h2" />标题 H2</Text>/          <Text variant="h3" />标题 H3</Text>/          <Text variant="body1" />正文 Body1</Text>/          <Text variant="body2" />正文 Body2</Text>/          <Text variant="caption" />说明文字 Caption</Text>/          <Text variant="overline" />上标文字 OVERLINE</Text>/        </Card>/
        {// 按钮组件 }/        <Card style={styles.section} />/          <Text variant="h3" style={styles.sectionTitle} />按钮组件</Text>/          <View style={styles.buttonRow} />/            <Button variant="primary" size="small" title="小按钮" / accessibilityLabel="TODO: 添加无障碍标签" />/            <Button variant="secondary" size="medium" title="中按钮" / accessibilityLabel="TODO: 添加无障碍标签" />/            <Button variant="outline" size="large" title="大按钮" / accessibilityLabel="TODO: 添加无障碍标签" />/          </View>/          <View style={styles.buttonRow} />/            <Button variant="ghost" title="幽灵按钮" / accessibilityLabel="TODO: 添加无障碍标签" />/            <Button variant="danger" title="危险按钮" / accessibilityLabel="TODO: 添加无障碍标签" />/            <Button disabled title="禁用按钮" / accessibilityLabel="TODO: 添加无障碍标签" />/          </View>/        </Card;>;/{// 输入框组件 }/        <Card style={styles.section} />/          <Text variant="h3" style={styles.sectionTitle} />输入框组件</Text>/          <Input
            label="用户名"
            placeholder="请输入用户名"
            value={inputValue}
            onChangeText={setInputValue}
            helperText="用户名长度为3-20个字符"
          />/          <Input
            label="密码"
            type="password"
            placeholder="请输入密码"
            variant="filled"
          />/          <Input
            label="邮箱"
            type="email"
            placeholder="请输入邮箱"
            variant="underlined"
          />/        </Card>/
        {// 表单组件 }/        <Card style={styles.section} />/          <Text variant="h3" style={styles.sectionTitle} />表单组件</Text>/
          <Text variant="body2" style={styles.subTitle} />开关 Switch</Text>/          <Switch
            value={switchValue}
            onValueChange={setSwitchValue}
            label="启用通知"
            description="接收健康提醒和建议"
          />/
          <Text variant="body2" style={styles.subTitle} />复选框 Checkbox</Text>/          <Checkbox
            checked={checkboxValue}
            onPress={setCheckboxValue}
            label="同意用户协议"
            description="我已阅读并同意《用户服务协议》"
          />/
          <Text variant="body2" style={styles.subTitle} />单选框 Radio</Text>/          <View style={styles.radioGroup} />/            <Radio
              selected={radioValue === 'option1'}
              onPress={() = /> setRadioValue('option1')}/              label="选项一"
              description="这是第一个选项"
            />/            <Radio
              selected={radioValue === 'option2'}
              onPress={() = /> setRadioValue('option2')}/              label="选项二"
              description="这是第二个选项"
            />/          </View>/
          <Text variant="body2" style={styles.subTitle} />滑块 Slider</Text>/          <Slider
            value={sliderValue}
            onValueChange={setSliderValue}
            minimumValue={0}
            maximumValue={100}
            step={1}
            label="健康指数"
            showValue
          />/        </Card>/
        {// 头像组件 }/        <Card style={styles.section} />/          <Text variant="h3" style={styles.sectionTitle} />头像组件</Text>/          <View style={styles.avatarRow} />/            <Avatar size="small" />/            <Avatar size="medium" name="张三" />/            <Avatar size="large" source={{ uri: 'https:// via.placeholder.com * 64'}}  *// > * < *//View>/        </Card>/
        {// 智能体头像 }/        <Card style={styles.section} />/          <Text variant="h3" style={styles.sectionTitle} />智能体头像</Text>/          <View style={styles.avatarRow} />/            <AgentAvatar agent="xiaoai" size="medium" online={true} />/            <AgentAvatar agent="xiaoke" size="medium" online={false} />/            <AgentAvatar agent="laoke" size="medium" />/            <AgentAvatar agent="soer" size="medium" online={true} />/          </View>/        </Card>/
        {// 徽章组件 }/        <Card style={styles.section} />/          <Text variant="h3" style={styles.sectionTitle} />徽章组件</Text>/          <View style={styles.badgeRow} />/            <Badge variant="primary" count={5} />/            <Badge variant="success" count={99} />/            <Badge variant="warning" count={999} />/            <Badge variant="error" dot />/            <Badge variant="default" />NEW</Badge>/          </View>/        </Card>/
        {// 加载组件 }/        <Card style={styles.section} />/          <Text variant="h3" style={styles.sectionTitle} />加载组件</Text>/          <Loading text="正在加载..." />/        </Card>/
        {// 模态框 }/        <Card style={styles.section} />/          <Text variant="h3" style={styles.sectionTitle} />模态框组件</Text>/          <Button title="打开模态框" onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> setModalVisible(true)} />/        </Card>/
        {// 分割线 }/        <Card style={styles.section} />/          <Text variant="h3" style={styles.sectionTitle} />分割线组件</Text>/          <Text />上方内容</Text>/          <Divider margin="md" />/          <Text />下方内容</Text>/          <Divider text="或者" margin="md" />/          <Text />带文字的分割线</Text>/        </Card>/      </Container>/
      {// 模态框示例 }/      <Modal
        visible={modalVisible}
        onClose={() = /> setModalVisible(false)}/        size="medium"
      >
        <Text variant="h3" style={styles.modalTitle} />模态框标题</Text>/        <Text variant="body1" style={styles.modalContent} />/          这是一个模态框的示例内容。您可以在这里放置任何内容。
        </Text>/        <View style={styles.modalButtons} />/          <Button
            title="取消"
            variant="outline"
            onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> setModalVisible(false)}/            style={styles.modalButton} />/          <Button
            title="确认"
            variant="primary"
            onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> setModalVisible(false)}/            style={styles.modalButton} />/        </View>/      </Modal>/    </ScrollView>/  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  title: {
    textAlign: 'center',
    marginBottom: spacing.lg,
  },
  section: { marginBottom: spacing.lg  },
  sectionTitle: {
    marginBottom: spacing.md,
    color: colors.primary,
  },
  subTitle: {
    marginTop: spacing.md,
    marginBottom: spacing.sm,
    fontWeight: '600',
    color: colors.textSecondary,
  },
  buttonRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  avatarRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  radioGroup: { gap: spacing.xs  },
  modalTitle: {
    marginBottom: spacing.md,
    textAlign: 'center',
  },
  modalContent: {
    marginBottom: spacing.lg,
    textAlign: 'center',
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  modalButton: {
    flex: 1,
    marginHorizontal: spacing.xs,
  },
  colorPreviewSection: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  colorPreviewButton: { marginRight: spacing.sm  },
;
  colorPreviewText: { color: colors.textSecondary  };};);
export default React.memo(UIShowcase);