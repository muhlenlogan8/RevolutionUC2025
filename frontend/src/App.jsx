import { useState, useEffect, useRef } from "react";
import axios from "axios";

function App() {
	const [imageSrc, setImageSrc] = useState("");
	const [loading, setLoading] = useState(false);
	const [aiText, setAiText] = useState("");
	const [audioUrl, setAudioUrl] = useState("");
	const audioRef = useRef(null); // Create a reference to the audio element

	const SERVER_IP = "192.168.4.138:5000";

	// Fetch the latest image from the backend
	const fetchImage = async () => {
		try {
			setLoading(true);
			const timestamp = new Date().getTime(); // Prevent caching
			setImageSrc(`http://${SERVER_IP}/image/latest.jpg?t=${timestamp}`);
		} catch (error) {
			console.error("Error fetching image:", error);
		} finally {
			setLoading(false);
		}
	};

	// Fetch AI-generated text and audio
	const fetchAiResponse = async () => {
		try {
			const response = await axios.get(`http://${SERVER_IP}/aitext`);
			const newText = response.data.text;

			// Update only if new text is different
			if (newText !== aiText) {
				setAiText(newText);

				// Force reload audio with a new timestamp to avoid caching
				const newAudioUrl = `http://${SERVER_IP}/audio/output.mp3?t=${new Date().getTime()}`;
				setAudioUrl(""); // Reset audio source first
				setTimeout(() => setAudioUrl(newAudioUrl), 50); // Small delay before setting new URL
			}
		} catch (error) {
			console.error("Error fetching AI response:", error);
		}
	};

	// Play audio automatically when audioUrl updates
	useEffect(() => {
		if (audioUrl && audioRef.current) {
			audioRef.current.load(); // Ensure it reloads the updated audio file
			audioRef.current.play().catch((error) => {
				console.error("Autoplay prevented:", error);
			});
		}
	}, [audioUrl]);

	// Poll for new image and AI text every 2 seconds
	useEffect(() => {
		fetchImage(); // Load image on start
		fetchAiResponse(); // Load AI text on start

		const interval = setInterval(() => {
			fetchImage();
			fetchAiResponse();
		}, 2000);

		return () => clearInterval(interval);
	}, [aiText]);

	return (
		<div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-4">
			<h1 className="text-3xl font-bold mb-4">SightSense Image</h1>

			{/* Display Latest Image */}
			<div className="relative border-4 border-white rounded-lg shadow-lg">
				{loading && (
					<div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
						<p className="text-xl">Loading...</p>
					</div>
				)}
				{imageSrc && !loading && (
					<img
						src={imageSrc}
						alt="Latest Capture"
						className="w-full h-auto max-w-sm rounded-lg"
					/>
				)}
			</div>

			{/* AI Response */}
			{aiText && (
				<div className="mt-4 p-4 bg-gray-800 rounded-lg text-center">
					<h2 className="text-xl font-bold">AI Response:</h2>
					<p className="text-lg">{aiText}</p>
				</div>
			)}

			{/* Play AI-generated Speech */}
			{audioUrl && (
				<div className="mt-4">
					<audio ref={audioRef} controls>
						<source src={audioUrl} type="audio/mp3" />
						Your browser does not support the audio element.
					</audio>
				</div>
			)}
		</div>
	);
}

export default App;
