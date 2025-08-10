/* eslint-disable @typescript-eslint/no-explicit-any */
import { DataKey } from "recharts/types/util/types";
import z from "zod";
import { useChartStore } from "../stores/chart-store";

export interface ChartDataPoint {
	[key: string]: string | number | Date | null;
}

export interface ChartConfig {
	id: string;
	type: "line" | "bar" | "pie" | "area";
	title: string;
	data: ChartDataPoint[];
	xKey?: DataKey<any>;
	yKey?: DataKey<any>;
	dataKeys?: DataKey<any>[];
	colors?: string[];
	timeRange?: "1W" | "1M" | "3M" | "6M" | "1Y";
}
const dataKeySchema = z.union([z.string(), z.number()]);

const chartDataPointSchema = z.record(
	z.string(),
	z.union([z.string(), z.number(), z.string(), z.null()])
);

export const chartSchema = z.object({
	id: z.string(),
	type: z.enum(["line", "bar", "pie", "area"]),
	title: z.string(),
	data: z.array(chartDataPointSchema),
	xKey: dataKeySchema.optional(),
	yKey: dataKeySchema.optional(),
	dataKeys: z.array(dataKeySchema).optional(),
	colors: z.array(z.string()).optional(),
	timeRange: z.enum(["1W", "1M", "3M", "6M", "1Y"]).optional(),
});

export type ChartSchemaType = z.infer<typeof chartSchema>;

export const isCompleteChart = (chart: any): chart is ChartSchemaType => {
	return chartSchema.safeParse(chart).success;
};

const isEqual = (a: any, b: any): boolean => {
	if (a === b) return true;
	if (a == null || b == null) return false;
	if (typeof a !== typeof b) return false;

	if (Array.isArray(a) && Array.isArray(b)) {
		if (a.length !== b.length) return false;
		return a.every((item, index) => isEqual(item, b[index]));
	}

	if (typeof a === "object") {
		const keysA = Object.keys(a);
		const keysB = Object.keys(b);
		if (keysA.length !== keysB.length) return false;
		return keysA.every((key) => isEqual(a[key], b[key]));
	}

	return false;
};

// Function to merge partial chart data with existing chart
const mergeChartData = (existingChart: any, newPartialChart: any) => {
	const merged = { ...existingChart };
	let hasChanges = false;

	// Check each field for changes
	Object.keys(newPartialChart).forEach((key) => {
		const newValue = newPartialChart[key];
		const existingValue = existingChart[key];

		if (newValue !== undefined && !isEqual(existingValue, newValue)) {
			merged[key] = newValue;
			hasChanges = true;
		}
	});

	return { merged, hasChanges };
};

// Main function to handle chart updates
interface ChartHandlerActions {
	addChart: (chart: ChartSchemaType) => void;
	updateChart: (index: number, chart: ChartSchemaType) => void;
}

// Main function to handle chart updates
export const handleChartUpdates = (
	charts: any[],
	addChart: ChartHandlerActions["addChart"],
	updateChart: ChartHandlerActions["updateChart"]
): void => {
	if (!charts) return;

	charts.forEach((partialChart) => {
		if (!partialChart) return;

		// Generate chart identifier
		const chartId =
			partialChart.id || partialChart.title || `chart_${Date.now()}`;

		// Get current charts from store
		const currentCharts = useChartStore.getState().charts;
		const existingChartIndex = currentCharts.findIndex(
			(existingChart) => (existingChart.id || existingChart.title) === chartId
		);

		if (existingChartIndex !== -1) {
			// Chart exists, check for updates
			const existingChart = currentCharts[existingChartIndex];
			const { merged, hasChanges } = mergeChartData(
				existingChart,
				partialChart
			);

			if (hasChanges) {
				updateChart(existingChartIndex, merged);
			}
		} else {
			// Chart doesn't exist, add it if it has minimum required fields
			const hasMinimumFields =
				partialChart.type && (partialChart.id || partialChart.title);

			if (hasMinimumFields) {
				// Ensure chart has an ID
				const chartToAdd = {
					...partialChart,
					id: partialChart.id || partialChart.title || `chart_${Date.now()}`,
					data: partialChart.data || [],
				};

				console.log(`Adding new chart:`, chartToAdd);
				addChart(chartToAdd as ChartSchemaType);
			}
		}
	});
};
