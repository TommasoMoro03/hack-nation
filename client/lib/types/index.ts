export interface Message {
	id: string;
	role: "user" | "assistant";
	content: string;
	timestamp: Date;
	isStreaming?: boolean;
	attachedFiles?: UploadedFile[];
}

export interface ChartDataPoint {
	[key: string]: string | number | Date | null;
}

export interface ChartConfig {
	id: string;
	type: "line" | "bar" | "pie" | "area" | "scatter";
	title: string;
	data: ChartDataPoint[];
	xKey?: string;
	yKey?: string;
	dataKeys?: string[];
	colors?: string[];
	timeRange?: "1W" | "1M" | "3M" | "6M" | "1Y";
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
