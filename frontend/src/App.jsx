import { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [message, setMessage] = useState("");

  const uploadFile = async () => {
    if (!file) {
      setMessage("Please select a PDF first.");
      return;
    }

    const formData = new FormData();
    formData.append("pdf", file);

    setUploading(true);
    setMessage("");

    try {
      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      setMessage(
        `Uploaded successfully. ${data.total_chunks} chunks stored.`
      );
    } catch (error) {
      setMessage(error.message);
    } finally {
      setUploading(false);
    }
  };

  const askQuestion = async () => {
    if (!query.trim()) {
      return;
    }

    setAsking(true);
    setAnswer("");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/chat?query=${encodeURIComponent(query)}`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong");
      }

      if (typeof data.answer === "string") {
          setAnswer(data.answer);
        } else {
          setAnswer(data.answer.text || JSON.stringify(data.answer));
        }
    } catch (error) {
      setAnswer(`Error: ${error.message}`);
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="app">
      <h1>Private PDF Chatbot</h1>

      <div className="upload-section">
        <h2>Upload PDF</h2>

        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <button onClick={uploadFile} disabled={uploading}>
          {uploading ? "Uploading..." : "Upload PDF"}
        </button>

        {message && <p>{message}</p>}
      </div>

      <div className="chat-section">
        <h2>Ask about your PDF</h2>

        <input
          type="text"
          placeholder="Ask a question..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              askQuestion();
            }
          }}
        />

        <button onClick={askQuestion} disabled={asking}>
          {asking ? "Thinking..." : "Ask"}
        </button>

        {answer && (
          <div className="answer">
            <h3>Answer</h3>
            <p>{answer}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;