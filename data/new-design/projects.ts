import type { IconName } from "@/components/new-design/PixelIcon";

export type Project = {
	id: string;
	name: string;
	icon: IconName;
	// Lines of source I wrote, from git history. Excludes lockfiles, data and
	// vendored code, and counts only my own commits on forks.
	lines: number;
	summary: string;
	details: string;
	status: string;
	stack: string[];
	links: { label: string; href: string }[];
	image?: { src: string; alt: string; width: number; height: number };
};

// Ordered by most recent work.
export const projects: Project[] = [
	{
		id: "hanja-chain",
		name: "Hanja Chain",
		icon: "hanja",
		lines: 8420,
		summary: "Learn Hanja through the Korean words that use them.",
		details:
			"Every Korean word is a chain of characters, and every character links to more words. Tap a syllable, jump to other words that share its Hanja, and keep branching. The app runs offline on a database I built from Korean dictionaries: 1,799 characters and 312,000 compound words.",
		status: "In active development",
		stack: ["Expo", "React Native", "SQLite", "Python"],
		links: [
			{ label: "App source", href: "https://github.com/ckearl/hanja-chain-app" },
			{ label: "Data pipeline", href: "https://github.com/ckearl/hanja-chain-data" },
		],
		image: {
			src: "/projects/hanja-chain.png",
			alt: "Hanja Chain's Chains screen, branching from the word 학교 to 입학",
			width: 323,
			height: 700,
		},
	},
	{
		id: "listening-stats",
		name: "Listening Stats",
		icon: "chart",
		lines: 8247,
		summary: "Spotify Wrapped for any date range, any day of the year.",
		details:
			"A serverless tracker logs every song I play, and a dashboard explores about 88,000 plays going back to 2020. Spotify's API only remembers your last 50 plays, so this keeps its own history and stays inside the AWS free tier.",
		status: "Running daily",
		stack: ["AWS Lambda", "DynamoDB", "TypeScript"],
		links: [
			{ label: "Tracker source", href: "https://github.com/ckearl/spotify_stats" },
			{ label: "Dashboard source", href: "https://github.com/ckearl/spotify-stats-dashboard" },
		],
	},
	{
		id: "spotifast",
		name: "Spotifast",
		icon: "music",
		lines: 9178,
		summary: "A native Spotify client with a Winamp mini player.",
		details:
			"My fork of Carmine Paolino's Spotifast, a fast Rust client with no browser engine. I've been building out its mini player with a Windows 98 look: keyboard control, FIND search, lyrics, a device picker and a wide spectrum visualizer.",
		status: "In active development",
		stack: ["Rust", "egui", "librespot"],
		links: [
			{ label: "My fork", href: "https://github.com/ckearl/spotifast" },
			{ label: "Original project", href: "https://github.com/crmne/spotifast" },
		],
		image: {
			src: "/projects/spotifast-winamp.png",
			alt: "The Spotifast mini player with main, playlist and FIND windows in a Windows 98 style",
			width: 596,
			height: 916,
		},
	},
	{
		id: "memory-graph",
		name: "Memory Graph",
		icon: "graph",
		lines: 2345,
		summary: "A life's memories, drawn as a connected graph.",
		details:
			"Type a band's name and every memory connected to it lights up across the decades. This is a phone prototype for testing that one moment before building the real app. Everything stays on the device.",
		status: "Prototype, private for now",
		stack: ["Expo", "Skia", "d3-force", "SQLite"],
		links: [],
	},
	{
		id: "patchbay",
		name: "Patchbay",
		icon: "cable",
		lines: 5731,
		summary: "Send each Mac app's audio to its own output and volume.",
		details:
			"macOS has no per-app output routing, so this menu bar utility builds it on Core Audio process taps. Discord can go to a USB hub, Teams to headphones and a browser to speakers, each at its own level. Routing is built and unit-tested, and real-hardware testing is next.",
		status: "In progress",
		stack: ["Swift", "Core Audio"],
		links: [],
	},
	{
		id: "voice-counter",
		name: "Twitch Voice Counter",
		icon: "mic",
		lines: 1678,
		summary: "Counts a streamer's filler words and reports back in chat.",
		details:
			"Type !dude in chat and get the tally for this stream and all time. It transcribes Twitch's public audio with Whisper, so nothing runs on the streamer's machine. Adding a new word replays the whole archive instead of starting from zero.",
		status: "Working",
		stack: ["Python", "Whisper", "SQLite"],
		links: [],
	},
	{
		id: "chat-peggle",
		name: "Chat Peggle",
		icon: "game",
		lines: 4057,
		summary: "Peggle, where Twitch chat aims the cannon together.",
		details:
			"Chat types left and right, the cannon swings, and every 30 seconds it fires whether they agreed or not. There's nothing to install or log into: open one HTML file and start streaming.",
		status: "Playable",
		stack: ["JavaScript", "Twitch chat"],
		links: [],
	},
	{
		id: "star-shot",
		name: "Star Shot",
		icon: "camera",
		lines: 3504,
		summary: "A retro photo booth that can't see your photos.",
		details:
			"The booth encrypts each set of four photos, uploads only the ciphertext and prints a QR code. Decryption happens in your browser, and the key lives only in that link. Lose the link and the photos are gone, by design.",
		status: "Live",
		stack: ["Next.js", "WebCrypto", "Python"],
		links: [{ label: "Visit starshot.photo", href: "https://starshot.photo" }],
	},
	{
		id: "conference-scraper",
		name: "General Conference Scraper",
		icon: "book",
		lines: 2377,
		summary: "Turns General Conference talks into Markdown and analysis.",
		details:
			"Point it at a year and month, and it saves each talk as Markdown with a JSON analysis alongside it. The analysis uses deterministic NLP and no LLM, so every result can be reproduced.",
		status: "Finished",
		stack: ["Python", "NLP"],
		links: [{ label: "Source", href: "https://github.com/ckearl/general-conference-scraper" }],
	},
	{
		id: "kearl",
		name: "kearl",
		icon: "terminal",
		lines: 6203,
		summary: "curl, rebuilt to be nicer to use.",
		details:
			"A command-line HTTP client with highlighted output, jq-style filtering and a Vim-like JSON explorer. It also keeps profiles and request history, compares requests side by side and speaks GraphQL.",
		status: "Working",
		stack: ["Go"],
		links: [],
	},
	{
		id: "lecture-transcriber",
		name: "Lecture Transcriber",
		icon: "lecture",
		lines: 2095,
		summary: "Otter.ai-style transcripts for MBA lectures.",
		details:
			"A FastAPI service that transcribes recordings with Whisper, identifies speakers, then pulls out summaries, keywords and study questions with Gemini.",
		status: "Finished",
		stack: ["Python", "FastAPI", "Whisper", "Gemini"],
		links: [{ label: "Source", href: "https://github.com/ckearl/lecture-transcriber" }],
	},
	{
		id: "intercontinentle",
		name: "Intercontinentle",
		icon: "globe",
		lines: 1316,
		summary: "A country trivia game for the browser.",
		details:
			"A country trivia game I built with Corban Procuniar. It started as a console game and grew into a React site.",
		status: "Live",
		stack: ["React", "TypeScript"],
		links: [
			{ label: "Play it", href: "https://intercontinentle.corbanpro.net" },
			{ label: "Source", href: "https://github.com/ckearl/intercontinentle" },
		],
	},
];
