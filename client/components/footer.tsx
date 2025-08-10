import React from "react";
import Image from "next/image";
import Link from "next/link";
import { GithubIcon, Video } from "lucide-react";

function Footer() {
	return (
		<footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">
			<Link
				className="flex items-center gap-2 hover:underline hover:underline-offset-4"
				href="https://github.com/TommasoMoro03/hack-nation"
				target="_blank"
				rel="noopener noreferrer">
				<Image
					aria-hidden
					src="/file.svg"
					alt="File icon"
					width={16}
					height={16}
				/>
				Learn
			</Link>
			<Link
				className="flex items-center gap-2 hover:underline hover:underline-offset-4"
				href="https://github.com/TommasoMoro03/hack-nation"
				target="_blank"
				rel="noopener noreferrer">
				<Video className="size-4 text-muted-foreground" />
				Demo
			</Link>
			<Link
				className="flex items-center gap-2 hover:underline hover:underline-offset-4"
				href="https://github.com/TommasoMoro03/hack-nation"
				target="_blank"
				rel="noopener noreferrer">
				<GithubIcon className="size-4 text-muted-foreground" />
				GitHub
			</Link>
		</footer>
	);
}

export default Footer;
