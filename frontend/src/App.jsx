import { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [imageSrc, setImageSrc] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchImage = async () => {
    setLoading(true);
    try {
      const timestamp = new Date().getTime(); // Prevent caching
      setImageSrc(`http://localhost:5000/image/latest.jpg?t=${timestamp}`);
    } catch (error) {
      console.error("Error fetching image:", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchImage(); // Load image on start
    const interval = setInterval(fetchImage, 5000); // Refresh every 5 sec
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
      <h1 className="text-3xl font-bold mb-4">Nicla Vision Camera</h1>

      <div className="relative w-96 h-96 border-4 border-white rounded-lg shadow-lg">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
            <p className="text-xl">Loading...</p>
          </div>
        )}
        {imageSrc && !loading && (
          <img
            src={imageSrc}
            alt="Latest Capture"
            className="w-full h-full object-cover rounded-lg"
          />
        )}
      </div>

      <button
        onClick={fetchImage}
        className="mt-4 px-6 py-2 bg-blue-500 hover:bg-blue-700 text-white font-bold rounded-lg"
      >
        Refresh Image
      </button>
    </div>
  );
}

export default App;
