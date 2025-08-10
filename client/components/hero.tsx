"use client";

import { motion } from "framer-motion";
import React from "react";
import Image from "next/image";

function Hero() {
	return (
		<>
			<motion.h1
				initial={{ opacity: 0 }}
				animate={{ opacity: 1 }}
				transition={{ delay: 0.4 }}
				className="text-3xl font-bold tracking-tight text-center flex items-end justify-center gap-2">
				FinDocGPT
				<Image
					src="/logo.png"
					alt="FinDocGPT"
					width={40}
					height={40}
				/>
			</motion.h1>
			<motion.p
				initial={{ opacity: 0 }}
				animate={{ opacity: 1 }}
				transition={{ delay: 0.5 }}
				className="text-sm text-center text-gray-500 mb-8 mt-2">
				FinDocGPT is your go-to AI for financial document analysis and insights.
			</motion.p>
		</>
	);
}

export default Hero;
