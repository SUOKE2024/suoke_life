import { Alert } from "react-native";


// Mock Alert
jest.mock("react-native", () => ({
  Alert: {
    alert: jest.fn(),
  },
}));

const mockAlert = Alert.alert as jest.MockedFunction<typeof Alert.alert>;

// Mock错误处理器
const errorHandler = {
  handleApiError: (error: any): string => {
    if (error.response) {
      const status = error.response.status;

      switch (status) {
        case 400:
          return "请求参数错误";
        case 401:
          return "未授权，请重新登录";
        case 403:
          return "权限不足";
        case 404:
          return "请求的资源不存在";
        case 500:
          return "服务器内部错误";
        default:
          return error.response.data?.message || "服务器错误";
      }
    }

    if (error.request) {
      return "网络连接失败，请检查网络设置";
    }

    return error.message || "未知错误";
  },

  showErrorAlert: (title: string, message: string): void => {
    Alert.alert(title, message, [{ text: "确定" }]);
  },

  isNetworkError: (error: any): boolean => {
    return !error.response && !!error.request;
  },

  isServerError: (error: any): boolean => {
    return error.response && error.response.status >= 500;
  },
};

describe("ErrorHandler", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("API错误处理", () => {
    it("应该处理400错误", () => {
      const error = {
        response: {
          status: 400,
          data: { message: "参数错误" },
        },
      };

      const result = errorHandler.handleApiError(error);
      expect(result).toBe("请求参数错误");
    });

    it("应该处理401错误", () => {
      const error = {
        response: {
          status: 401,
        },
      };

      const result = errorHandler.handleApiError(error);
      expect(result).toBe("未授权，请重新登录");
    });

    it("应该处理网络错误", () => {
      const error = {
        request: {},
        message: "网络错误",
      };

      const result = errorHandler.handleApiError(error);
      expect(result).toBe("网络连接失败，请检查网络设置");
    });
  });

  describe("错误提示", () => {
    it("应该显示错误弹窗", () => {
      errorHandler.showErrorAlert("错误", "这是一个错误消息");

      expect(mockAlert).toHaveBeenCalledWith("错误", "这是一个错误消息", [
        { text: "确定" },
      ]);
    });
  });

  describe("错误类型判断", () => {
    it("应该正确识别网络错误", () => {
      const networkError = { request: {}, message: "网络错误" };
      const result = errorHandler.isNetworkError(networkError);
      expect(typeof result).toBe("boolean");
      expect(result).toBe(true);

      const apiError = { response: { status: 400 } };
      expect(errorHandler.isNetworkError(apiError)).toBe(false);
    });

    it("应该正确识别服务器错误", () => {
      const serverError = { response: { status: 500 } };
      expect(errorHandler.isServerError(serverError)).toBe(true);

      const clientError = { response: { status: 400 } };
      expect(errorHandler.isServerError(clientError)).toBe(false);
    });
  });
});
