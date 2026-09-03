import { useParams, useSearchParams } from "react-router-dom";
import { useEffect, useRef, useState } from "react";

function formatTimestamp(seconds) {
  if (!seconds || isNaN(seconds)) return "0:00";

  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);

  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

function AudioViewer() {
  const { documentId } = useParams();
  const [searchParams] = useSearchParams();

  const startTime = Number(searchParams.get("t")) || 0;
  const highlight = searchParams.get("highlight") || "";

  const audioRef = useRef(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(startTime);
  const [duration, setDuration] = useState(0);

  const audioUrl = `${
    import.meta.env.VITE_API_URL
  }/documents/${documentId}/view/audio`;

  // Set starting timestamp when audio metadata loads
  useEffect(() => {
    const audio = audioRef.current;

    if (!audio) return;

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);

      if (startTime > 0 && startTime < audio.duration) {
        audio.currentTime = startTime;
        setCurrentTime(startTime);
      }
    };

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };

    const handlePlay = () => {
      setIsPlaying(true);
    };

    const handlePause = () => {
      setIsPlaying(false);
    };

    audio.addEventListener("loadedmetadata", handleLoadedMetadata);
    audio.addEventListener("timeupdate", handleTimeUpdate);
    audio.addEventListener("play", handlePlay);
    audio.addEventListener("pause", handlePause);

    return () => {
      audio.removeEventListener("loadedmetadata", handleLoadedMetadata);
      audio.removeEventListener("timeupdate", handleTimeUpdate);
      audio.removeEventListener("play", handlePlay);
      audio.removeEventListener("pause", handlePause);
    };
  }, [startTime]);

  // Play / Pause
  const togglePlay = () => {
    const audio = audioRef.current;

    if (!audio) return;

    if (audio.paused) {
      audio.play();
    } else {
      audio.pause();
    }
  };

  // Jump forward/backward
  const skip = (seconds) => {
    const audio = audioRef.current;

    if (!audio) return;

    audio.currentTime = Math.max(
      0,
      Math.min(audio.currentTime + seconds, audio.duration || Infinity)
    );
  };

  // Seek using progress bar
  const handleSeek = (e) => {
    const audio = audioRef.current;

    if (!audio) return;

    const value = Number(e.target.value);

    audio.currentTime = value;
    setCurrentTime(value);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto w-full max-w-4xl">

        {/* Header */}
        <div className="mb-4 rounded-xl bg-white p-5 shadow">
          <h1 className="text-xl font-semibold text-gray-800">
            🎧 Audio Source
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            Starting at {formatTimestamp(startTime)}
          </p>
        </div>

        {/* Audio Player */}
        <div className="rounded-xl bg-white p-6 shadow">

          {/* Hidden native audio */}
          <audio
            ref={audioRef}
            src={audioUrl}
            preload="metadata"
          />

          {/* Progress */}
          <input
            type="range"
            min="0"
            max={duration || 0}
            step="0.01"
            value={currentTime}
            onChange={handleSeek}
            className="w-full cursor-pointer"
          />

          {/* Time */}
          <div className="mt-2 flex justify-between text-xs text-gray-500">
            <span>{formatTimestamp(currentTime)}</span>
            <span>{formatTimestamp(duration)}</span>
          </div>

          {/* Controls */}
          <div className="mt-5 flex items-center justify-center gap-4">

            <button
              onClick={() => skip(-10)}
              className="rounded-lg bg-gray-200 px-4 py-2 text-sm font-medium hover:bg-gray-300"
            >
              ↶ 10s
            </button>

            <button
              onClick={togglePlay}
              className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-600 text-xl text-white hover:bg-blue-700"
            >
              {isPlaying ? "❚❚" : "▶"}
            </button>

            <button
              onClick={() => skip(10)}
              className="rounded-lg bg-gray-200 px-4 py-2 text-sm font-medium hover:bg-gray-300"
            >
              10s ↷
            </button>

          </div>
        </div>

        {/* Transcript */}
        <div className="mt-6 rounded-xl bg-white p-6 shadow">

          <h2 className="mb-4 text-lg font-semibold text-gray-800">
            SOURCE TRANSCRIPT
          </h2>

          <p className="whitespace-pre-wrap text-sm leading-7 text-gray-700">
            {highlight || "No transcript available."}
          </p>

        </div>

      </div>
    </div>
  );
}

export default AudioViewer;