/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import type { ChartConfig } from "@/lib/types";
import {
	LineChart,
	Line,
	BarChart,
	Bar,
	PieChart,
	Pie,
	AreaChart,
	Area,
	XAxis,
	YAxis,
	CartesianGrid,
	Tooltip,
	Legend,
	ResponsiveContainer,
	Cell,
} from "recharts";

interface DynamicChartProps {
	config: ChartConfig;
}

const COLORS = [
	"#3b82f6",
	"#10b981",
	"#f59e0b",
	"#ef4444",
	"#8b5cf6",
	"#06b6d4",
];

export function DynamicChart({ config }: DynamicChartProps) {
	const { type, data, xKey, yKey, dataKeys, colors = COLORS } = config;
	console.log("DynamicChart rendered with config:", config);

	const formatValue = (value: any) => {
		if (typeof value === "number") {
			if (value > 1000000) {
				return `$${(value / 1000000).toFixed(1)}M`;
			} else if (value > 1000) {
				return `$${(value / 1000).toFixed(1)}K`;
			}
			return `$${value.toFixed(2)}`;
		}
		return value;
	};

	const CustomTooltip = ({ active, payload, label }: any) => {
		if (active && payload && payload.length) {
			return (
				<div className="bg-card border border-border rounded-lg p-3 shadow-lg">
					<p className="font-medium text-sm mb-2">{label}</p>
					{payload.map((entry: any, index: number) => (
						<div
							key={index}
							className="flex items-center gap-2 text-sm">
							<div
								className="w-3 h-3 rounded-full"
								style={{ backgroundColor: entry.color }}
							/>
							<span className="text-muted-foreground">{entry.dataKey}:</span>
							<span className="font-medium">{formatValue(entry.value)}</span>
						</div>
					))}
				</div>
			);
		}
		return null;
	};

	const renderChart = () => {
		switch (type) {
			case "line":
				return (
					<LineChart data={data}>
						<CartesianGrid
							strokeDasharray="3 3"
							className="opacity-30"
						/>
						<XAxis
							dataKey={xKey}
							className="text-xs"
							tick={{ fontSize: 12 }}
						/>
						<YAxis
							className="text-xs"
							tick={{ fontSize: 12 }}
							tickFormatter={formatValue}
						/>
						<Tooltip content={<CustomTooltip />} />
						<Legend />
						{dataKeys ? (
							dataKeys.map((key, index) => (
								<Line
									key={key.toString()}
									type="monotone"
									dataKey={key}
									stroke={colors[index % colors.length]}
									strokeWidth={2}
									dot={{ r: 4 }}
									activeDot={{ r: 6 }}
								/>
							))
						) : (
							<Line
								type="monotone"
								dataKey={yKey}
								stroke={colors[0]}
								strokeWidth={2}
								dot={{ r: 4 }}
								activeDot={{ r: 6 }}
							/>
						)}
					</LineChart>
				);

			case "bar":
				return (
					<BarChart data={data}>
						<CartesianGrid
							strokeDasharray="3 3"
							className="opacity-30"
						/>
						<XAxis
							dataKey={xKey}
							className="text-xs"
							tick={{ fontSize: 12 }}
						/>
						<YAxis
							className="text-xs"
							tick={{ fontSize: 12 }}
							tickFormatter={formatValue}
						/>
						<Tooltip content={<CustomTooltip />} />
						<Legend />
						{dataKeys ? (
							dataKeys.map((key, index) => (
								<Bar
									key={key.toString()}
									dataKey={key}
									fill={colors[index % colors.length]}
									radius={[2, 2, 0, 0]}
								/>
							))
						) : (
							<Bar
								dataKey={yKey!}
								fill={colors[0]}
								radius={[2, 2, 0, 0]}
							/>
						)}
					</BarChart>
				);

			case "area":
				return (
					<AreaChart data={data}>
						<CartesianGrid
							strokeDasharray="3 3"
							className="opacity-30"
						/>
						<XAxis
							dataKey={xKey}
							className="text-xs"
							tick={{ fontSize: 12 }}
						/>
						<YAxis
							className="text-xs"
							tick={{ fontSize: 12 }}
							tickFormatter={formatValue}
						/>
						<Tooltip content={<CustomTooltip />} />
						<Legend />
						{dataKeys ? (
							dataKeys.map((key, index) => (
								<Area
									key={key.toString()}
									type="monotone"
									dataKey={key}
									stackId="1"
									stroke={colors[index % colors.length]}
									fill={colors[index % colors.length]}
									fillOpacity={0.6}
								/>
							))
						) : (
							<Area
								type="monotone"
								dataKey={yKey!}
								stroke={colors[0]}
								fill={colors[0]}
								fillOpacity={0.6}
							/>
						)}
					</AreaChart>
				);

			case "pie":
				return (
					<PieChart>
						<Pie
							data={data}
							cx="50%"
							cy="50%"
							labelLine={false}
							label={({ name, percent }) =>
								`${name} ${(percent * 100).toFixed(0)}%`
							}
							outerRadius={80}
							fill="#8884d8"
							dataKey={yKey!}>
							{data.map((entry, index) => (
								<Cell
									key={`cell-${index}`}
									fill={colors[index % colors.length]}
								/>
							))}
						</Pie>
						<Tooltip content={<CustomTooltip />} />
					</PieChart>
				);
				return (
					<div className="text-center text-muted-foreground">
						Unsupported chart type
					</div>
				);
		}
	};

	return (
		<div className="w-full h-80">
			<ResponsiveContainer
				width="100%"
				height="100%">
				{renderChart()}
			</ResponsiveContainer>
		</div>
	);
}
