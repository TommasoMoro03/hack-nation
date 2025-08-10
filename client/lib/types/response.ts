import z from "zod";
import { chartSchema } from "./chart";

export const responseSchema = z.object({
	content: z.string(),
	title: z.string().nullable(),
	charts: z.array(chartSchema).nullable(),
});
