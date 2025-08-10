import { create } from "zustand";
import type { ChartConfig } from "@/lib/types";

interface ChartState {
	charts: ChartConfig[];
	isGenerating: boolean;
	addChart: (chart: ChartConfig) => void;
	updateChart: (id: string, config: Partial<ChartConfig>) => void;
	setGenerating: (isGenerating: boolean) => void;
	clearCharts: () => void;
}

export const useChartStore = create<ChartState>((set) => ({
	charts: [],
	activeChartId: null,
	isGenerating: false,

	addChart: (chart) => {
		set((state) => ({
			charts: [...state.charts, chart],
			activeChartId: chart.id,
		}));
	},

	setGenerating: (isGenerating) => {
		set({ isGenerating });
	},

	updateChart: (id, config) => {
		set((state) => ({
			charts: state.charts.map((chart) =>
				chart.id === id ? { ...chart, ...config } : chart
			),
		}));
	},

	clearCharts: () => {
		set({ charts: [] });
	},
}));
