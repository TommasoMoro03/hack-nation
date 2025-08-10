"use client";

import { motion } from "framer-motion";
import React from "react";

function Features() {
	return (
		<div className="justify-center items-center w-full hidden md:flex">
			<motion.div
				initial={{ opacity: 0, y: 10 }}
				animate={{ opacity: 1, y: 0 }}
				transition={{ delay: 0.6 }}
				className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-2xl mb-8">
				{[
					{
						icon: "📊",
						title: "Market Analysis",
						desc: "Real-time market data and trends",
					},
					{
						icon: "📄",
						title: "Document Analysis",
						desc: "Extract insights from financial docs",
					},
					{
						icon: "💡",
						title: "Investment Insights",
						desc: "AI-powered recommendations",
					},
				].map((feature, index) => (
					<motion.div
						key={feature.title}
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.7 + index * 0.1 }}
						className="p-4 rounded-lg bg-muted/30 border border-border/50">
						<div className="text-2xl mb-2">{feature.icon}</div>
						<h3 className="font-semibold text-sm mb-1">{feature.title}</h3>
						<p className="text-xs text-muted-foreground">{feature.desc}</p>
					</motion.div>
				))}
			</motion.div>
		</div>
	);
}

export default Features;
