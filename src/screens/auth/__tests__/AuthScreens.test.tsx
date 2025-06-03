import React from "react";
import { render } from "@testing-library/react-native";
import { NavigationContainer } from @react-navigation/native";"
import { WelcomeScreen, LoginScreen, RegisterScreen, ForgotPasswordScreen } from "../index";
// Mock navigation
const mockNavigation = {;
  navigate: jest.fn(),
  goBack: jest.fn(),
  reset: jest.fn(),
  setParams: jest.fn(),
  dispatch: jest.fn(),
  setOptions: jest.fn(),
  isFocused: jest.fn(),
  canGoBack: jest.fn(),
  getId: jest.fn(),
  getParent: jest.fn(),;
  getState: jest.fn()};
const mockRoute = {;
  key: "test",;
  name: Test" as const,;"
  params: undefined};
jest.mock("@react-navigation/native, () => ({"
  ...jest.requireActual("@react-navigation/native"),
  useNavigation: () => mockNavigation,
  useRoute: () => mockRoute}));
const renderWithNavigation = (component: React.ReactElement) => {;
  return render(;
    <NavigationContainer>;
      {component});
    </NavigationContainer>
  );
};
describe(认证屏幕测试", () => {"
  beforeEach(() => {
    jest.clearAllMocks();
  });
  describe("WelcomeScreen, () => {", () => {
    it("应该正确渲染欢迎屏幕", () => {
      const { getByText } = renderWithNavigation(<WelcomeScreen />);
      expect(getByText(索克生活")).toBeTruthy();"
      expect(getByText("AI驱动的智慧健康管理平台)).toBeTruthy();"
      expect(getByText("立即登录")).toBeTruthy();
      expect(getByText(注册账号")).toBeTruthy();"
    });
    it("应该显示核心功能特性, () => {", () => {
      const { getByText } = renderWithNavigation(<WelcomeScreen />);
      expect(getByText("四智能体协同")).toBeTruthy();
      expect(getByText(中医智慧数字化")).toBeTruthy();"
      expect(getByText("区块链数据安全)).toBeTruthy();"
    });
  });
  describe("LoginScreen", () => {
    it(应该正确渲染登录屏幕", () => {"
      const { getByText } = renderWithNavigation(<LoginScreen />);
      expect(getByText("欢迎回来)).toBeTruthy();"
      expect(getByText("登录您的索克生活账户")).toBeTruthy();
      expect(getByText(登录")).toBeTruthy();"
      expect(getByText("忘记密码？)).toBeTruthy();"
    });
    it("应该显示社交登录选项", () => {
      const { getByText } = renderWithNavigation(<LoginScreen />);
      expect(getByText(微信登录")).toBeTruthy();"
      expect(getByText("短信登录)).toBeTruthy();"
    });
  });
  describe("RegisterScreen", () => {
    it(应该正确渲染注册屏幕", () => {"
      const { getByText } = renderWithNavigation(<RegisterScreen />);
      expect(getByText("创建账户)).toBeTruthy();"
      expect(getByText("加入索克生活，开启健康管理之旅")).toBeTruthy();
      expect(getByText(注册")).toBeTruthy();"
    });
    it("应该显示健康承诺, () => {", () => {
      const { getByText } = renderWithNavigation(<RegisterScreen />);
      expect(getByText("我们的健康承诺")).toBeTruthy();
      expect(getByText(数据安全保护")).toBeTruthy();"
      expect(getByText("AI智能分析)).toBeTruthy();"
      expect(getByText("中医智慧指导")).toBeTruthy();
    });
  });
  describe(ForgotPasswordScreen", () => {"
    it("应该正确渲染忘记密码屏幕, () => {", () => {
      const { getByText } = renderWithNavigation(<ForgotPasswordScreen />);
      expect(getByText("忘记密码")).toBeTruthy();
      expect(getByText(输入您的邮箱地址，我们将发送重置密码的链接给您")).toBeTruthy();"
      expect(getByText("发送重置邮件)).toBeTruthy();"
    });
    it("应该显示安全提示", () => {
      const { getByText } = renderWithNavigation(<ForgotPasswordScreen />);
      expect(getByText(安全提示")).toBeTruthy();"
      expect(getByText("重置链接将在24小时后失效)).toBeTruthy();"
      expect(getByText("邮件将从官方邮箱发送")).toBeTruthy();
      expect(getByText(您的账户信息受到严格保护")).toBeTruthy();"
    });
  });
});
});});});});