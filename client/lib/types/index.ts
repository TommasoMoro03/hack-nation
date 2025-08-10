import { ChartConfig } from "./chart";
export * from "./chart";
export * from "./response";

export interface Message {
	id: string;
	role: "user" | "assistant";
	content: string;
	timestamp: Date;
	isStreaming?: boolean;
	attachedFiles?: UploadedFile[];
}

export interface FinancialMetric {
	symbol: string;
	price: number;
	change: number;
	changePercent: number;
	volume?: number;
	marketCap?: number;
	pe?: number;
}

export interface StreamResponse {
	type: "text" | "chart" | "metric" | "complete";
	content?: string;
	chartConfig?: ChartConfig;
	metrics?: FinancialMetric[];
}

export interface UploadedFile {
	id: string;
	name: string;
	size: number;
	type: string;
	uploadDate: Date;
	status: "uploading" | "processing" | "ready" | "error";
	url?: string;
	extractedText?: string;
	summary?: string;
}

export interface FileUploadProgress {
	fileId: string;
	progress: number;
	status: "uploading" | "processing" | "complete" | "error";
}
