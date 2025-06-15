import { USER_PROFILE, AGENT_INTERACTIONS, HEALTH_ACHIEVEMENTS, MEMBER_BENEFITS, SETTINGS_SECTIONS, HEALTH_STATS, ACTIVITY_RECORDS } from "../profileData";

describe("profileData", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("USER_PROFILE", () => {
    it("should be defined", () => {
      expect(USER_PROFILE).toBeDefined();
    });

    it("should have required properties", () => {
      expect(USER_PROFILE).toHaveProperty('id');
      expect(USER_PROFILE).toHaveProperty('name');
    });
  });

  describe("AGENT_INTERACTIONS", () => {
    it("should be defined", () => {
      expect(AGENT_INTERACTIONS).toBeDefined();
    });

    it("should be an array", () => {
      expect(Array.isArray(AGENT_INTERACTIONS)).toBe(true);
    });
  });

  describe("HEALTH_ACHIEVEMENTS", () => {
    it("should be defined", () => {
      expect(HEALTH_ACHIEVEMENTS).toBeDefined();
    });
  });

  describe("MEMBER_BENEFITS", () => {
    it("should be defined", () => {
      expect(MEMBER_BENEFITS).toBeDefined();
    });
  });

  describe("SETTINGS_SECTIONS", () => {
    it("should be defined", () => {
      expect(SETTINGS_SECTIONS).toBeDefined();
    });
  });

  describe("HEALTH_STATS", () => {
    it("should be defined", () => {
      expect(HEALTH_STATS).toBeDefined();
    });
  });

  describe("ACTIVITY_RECORDS", () => {
    it("should be defined", () => {
      expect(ACTIVITY_RECORDS).toBeDefined();
    });
  });
});