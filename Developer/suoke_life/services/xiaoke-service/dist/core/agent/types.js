"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AgentStatus = void 0;
/**
 * 智能体运行状态
 */
var AgentStatus;
(function (AgentStatus) {
    AgentStatus["INITIALIZING"] = "initializing";
    AgentStatus["READY"] = "ready";
    AgentStatus["BUSY"] = "busy";
    AgentStatus["ERROR"] = "error";
    AgentStatus["PAUSED"] = "paused";
    AgentStatus["TERMINATED"] = "terminated";
})(AgentStatus || (exports.AgentStatus = AgentStatus = {}));
