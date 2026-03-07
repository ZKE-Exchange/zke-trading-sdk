import type { PluginConfig, ToolSpec } from "./types.js";
import { createSpotTools } from "./tools/spot.js";
import { createFuturesTools } from "./tools/futures.js";
import { createWalletTools } from "./tools/wallet.js";

async function registerTool(api: any, tool: ToolSpec) {
  const registerFn =
    api?.registerAgentTool ||
    api?.tools?.registerAgentTool ||
    api?.agentTools?.register ||
    api?.tools?.register;

  if (typeof registerFn !== "function") {
    throw new Error(
      "Could not find an agent tool registration function on the OpenClaw plugin runtime API."
    );
  }

  const payload = {
    name: tool.name,
    description: tool.description,
    dangerous: !!tool.dangerous,
    inputSchema: tool.inputSchema,
    execute: async (input: Record<string, any>, ctx?: any) => {
      return await tool.execute(input, ctx);
    }
  };

  await registerFn.call(api?.tools || api?.agentTools || api, payload);
}

function buildTools(config?: PluginConfig): ToolSpec[] {
  return [
    ...createSpotTools(config),
    ...createFuturesTools(config),
    ...createWalletTools(config)
  ];
}

export async function register(api: any) {
  const config: PluginConfig =
    api?.config ||
    api?.getConfig?.() ||
    {};

  const tools = buildTools(config);

  for (const tool of tools) {
    await registerTool(api, tool);
  }
}

export async function activate(api: any) {
  return register(api);
}

export default {
  register,
  activate
};
