import type { PluginConfig, ToolSpec } from "./types.js";
import { createSpotTools } from "./tools/spot.js";
import { createFuturesTools } from "./tools/futures.js";
import { createWalletTools } from "./tools/wallet.js";

function buildTools(config?: PluginConfig): ToolSpec[] {
  return [
    ...createSpotTools(config),
    ...createFuturesTools(config),
    ...createWalletTools(config)
  ];
}

export default function (api: any) {
  const config: PluginConfig =
    api?.config ||
    api?.getConfig?.() ||
    {};

  const tools = buildTools(config);

  for (const tool of tools) {
    api.registerTool({
      name: tool.name,
      description: tool.description,
      parameters: tool.inputSchema,
      async execute(_id: string, params: Record<string, any>) {
        return await tool.execute(params);
      }
    });
  }
}
