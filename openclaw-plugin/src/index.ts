import type { PluginConfig, ToolSpec } from "./types.js";
import { createSpotTools } from "./tools/spot.js";
import { createFuturesTools } from "./tools/futures.js";
import { createWalletTools } from "./tools/wallet.js";

/**
 * 兼容层：
 * 不同 OpenClaw 版本公开的 runtime API 可能略有差异。
 * 这里只把差异收敛到 registerTool()。
 */
async function registerTool(api: any, tool: ToolSpec) {
  const register =
    api?.registerAgentTool ||
    api?.agentTools?.register ||
    api?.tools?.registerAgentTool ||
    api?.tools?.register;

  if (!register) {
    throw new Error(
      "Could not find an agent tool registration function on the OpenClaw plugin runtime API."
    );
  }

  const payload = {
    name: tool.name,
    description: tool.description,
    dangerous: !!tool.dangerous,
    inputSchema: tool.inputSchema,
    execute: async (input: Record<string, any>, ctx?: any) =>
      await tool.execute(input, ctx)
  };

  return await register.call(api?.agentTools || api?.tools || api, payload);
}

function buildTools(config?: PluginConfig): ToolSpec[] {
  return [
    ...createSpotTools(config),
    ...createFuturesTools(config),
    ...createWalletTools(config)
  ];
}

export async function setup(api: any) {
  const config: PluginConfig =
    api?.config ||
    api?.getConfig?.() ||
    {};

  const tools = buildTools(config);

  for (const tool of tools) {
    await registerTool(api, tool);
  }
}

export default {
  setup
};
