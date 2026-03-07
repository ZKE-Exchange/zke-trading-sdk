export type JsonSchema = Record<string, unknown>;

export type ToolSpec = {
  name: string;
  description: string;
  inputSchema: JsonSchema;
  dangerous?: boolean;
  execute: (input: Record<string, any>, ctx?: any) => Promise<any>;
};

export type PluginConfig = {
  tradingHome?: string;
  pythonBin?: string;
  autoApproveTrading?: boolean;
};
