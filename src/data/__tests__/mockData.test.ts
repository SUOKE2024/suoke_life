import { MOCK_CHAT_CHANNELS, MOCK_CONTACTS, MOCK_MESSAGES, AGENT_CONFIGS } from "../mockData";

describe("mockData", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("MOCK_CHAT_CHANNELS", () => {
    it("should be defined", () => {
      expect(MOCK_CHAT_CHANNELS).toBeDefined();
    });

    it("should be an array", () => {
      expect(Array.isArray(MOCK_CHAT_CHANNELS)).toBe(true);
    });
  });

  describe("MOCK_CONTACTS", () => {
    it("should be defined", () => {
      expect(MOCK_CONTACTS).toBeDefined();
    });

    it("should be an array", () => {
      expect(Array.isArray(MOCK_CONTACTS)).toBe(true);
    });
  });

  describe("MOCK_MESSAGES", () => {
    it("should be defined", () => {
      expect(MOCK_MESSAGES).toBeDefined();
    });

    it("should be an array", () => {
      expect(Array.isArray(MOCK_MESSAGES)).toBe(true);
    });
  });

  describe("AGENT_CONFIGS", () => {
    it("should be defined", () => {
      expect(AGENT_CONFIGS).toBeDefined();
    });

    it("should be an object", () => {
      expect(typeof AGENT_CONFIGS).toBe('object');
    });
  });
});