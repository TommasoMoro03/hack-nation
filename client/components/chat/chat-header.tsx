import React from "react";
import { Separator } from "../ui/separator";
import { ChevronLeft } from "lucide-react";
import { Button } from "../ui/button";

function ChatHeader() {
	return (
		<div className="px-4 pt-4">
			<div className="flex items-center gap-3 mb-4">
				<Button
					variant={"outline"}
					onClick={() => window.location.reload()}
					size={"icon"}>
					<ChevronLeft className="size-5" />
				</Button>
				<h1 className="text-3xl font-bold mt-2">Chat</h1>
			</div>
			<Separator />
		</div>
	);
}

export default ChatHeader;
