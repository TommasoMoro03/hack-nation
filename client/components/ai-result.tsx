import React from "react";
import { experimental_useObject as useObject } from "@ai-sdk/react";
import { responseSchema } from "@/lib/types/response";
import { Button } from "./ui/button";
import { MemoizedMarkdown } from "./memoized-markdown";
function AiResult() {
	const { object, submit, isLoading } = useObject({
		api: "http://localhost:8000/api/chat",
		schema: responseSchema,
	});

	console.log("AiResult object:", object);

	return (
		<div className="prose">
			<Button
				onClick={() => {
					console.log("Submitting data to API");
					submit("");
				}}
				disabled={isLoading}>
				{isLoading ? "Loading..." : "Generate"}
			</Button>
			{object?.content && (
				<MemoizedMarkdown
					content={object?.content}
					id={"ai-result-markdown"}
				/>
			)}
		</div>
	);
}

export default AiResult;
