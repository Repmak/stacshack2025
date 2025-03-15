import { writeFile } from 'fs/promises';
import dotenv from 'dotenv';
import fetch from 'node-fetch';
dotenv.config();
// Using Groq API which offers free credits
const GROQ_API_KEY = process.env.GROQ_API_KEY || ""; // Add your GROQ_API_KEY to .env
export async function generateCleanSrt(
	transcript: string[],
	srt: { content: string; fileName: string }[]
) {
	const promises = [];
	for (let i = 0; i < transcript.length; i++) {
		promises.push(cleanSrt(transcript[i], srt[i].content, i));
	}
	const responses = await Promise.all(promises);
	for (let i = 0; i < srt.length; i++) {
		const response = responses.find((response) => response.i === i);
		if (response) {
			await writeFile(srt[i].fileName, response.content ?? '', 'utf8');
		}
	}
}
async function cleanSrt(transcript: string, srt: string, i: number) {
	try {
		console.log(`Processing SRT file #${i}...`);
		const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${GROQ_API_KEY}`
			},
			body: JSON.stringify({
				messages: [
					{
						role: 'system',
						content: `The first item I will give you is the correct text, and the next will be the SRT generated from this text which is not totally accurate. Sometimes the srt files just doesn't have words so if this is the case add the missing words to the SRT file which are present in the transcript. Based on the accurate transcript, and the possibly inaccurate SRT file, return the SRT text corrected for inaccurate spelling and such. Make sure you keep the format and the times the same.
							transcript:
							${transcript}
							srt file text:
							${srt}`
					}
				],
				model: 'llama3-70b-8192', // Updated to current Groq model
				temperature: 0.3
			})
		});
		if (!response.ok) {
			const errorData = await response.text();
			console.error(`Error from Groq API (file #${i}):`, errorData);
			return { content: srt, i }; // Return original if there's an error
		}
		const data = await response.json();
		const content = data.choices[0].message.content;
		console.log(`Successfully processed SRT file #${i}`);
		return { content, i };
	} catch (error) {
		console.error(`Error processing SRT file #${i}:`, error);
		return { content: srt, i }; // Return original if there's an error
	}
}
