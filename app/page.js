import { useState } from "react";
import { extractTextFromPdfs } from "../utils/pdfUtils";
import { OpenAI } from "openai";

const openai = new OpenAI({
  apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY, // Store in environment variables
  dangerouslyAllowBrowser: true, // Remove for backend API calls
});

export default function Home() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [files, setFiles] = useState([]);
  const [extractedText, setExtractedText] = useState("");
  const [snippets, setSnippets] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleModalToggle = () => setIsModalOpen(!isModalOpen);

  const handleFileChange = (event) => {
    setFiles(event.target.files);
  };

  const handleSubmit = async () => {
    if (files.length === 0) {
      alert("Please upload at least one file.");
      return;
    }

    setLoading(true);
    try {
      const extractedTexts = await extractTextFromPdfs(files);
      const extracted = extractedTexts
        .map(({ fileName, text }) => `📄 ${fileName}:\n${text}\n\n`)
        .join("");
      setExtractedText(extracted);

      await generateSnippets(extracted); // Generate snippets after extraction
    } catch (error) {
      console.error("Text extraction failed:", error);
      alert("Something went wrong while extracting text.");
    } finally {
      setLoading(false);
    }
    handleModalToggle();
  };

  const generateSnippets = async (text) => {
    try {
      const response = await openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content:
              "You are an AI that extracts educational content from uploaded text and summarizes it into 5 distinct 150-word educational snippets.",
          },
          {
            role: "user",
            content: `Extract five distinct 150-word educational snippets from the following text. Each snippet should cover a unique topic:\n\n${text}`,
          },
        ],
        max_tokens: 1000,
      });

      const generatedSnippets =
        response.choices[0].message.content.split("\n\n");
      setSnippets(generatedSnippets);
    } catch (error) {
      console.error("Snippet generation failed:", error);
      alert("Failed to generate educational snippets.");
    }
  };

  return (
    <main className="bg-base-300">
      <nav className="p-4">
        <h1 className="font-bold text-xl">
          <span className="text-primary">Study </span>
          <span className="text-white">Reels</span>
        </h1>
      </nav>
      <main className="bg-base-300 min-h-screen flex flex-col items-center justify-center">
        <button className="btn btn-primary mt-8" onClick={handleModalToggle}>
          Upload
        </button>
        {isModalOpen && (
          <div className="modal modal-open text-white">
            <div className="modal-box">
              <h2 className="font-bold text-lg text-primary">Upload Modal</h2>
              <p className="py-4">
                Upload your lecture notes, lecture slides etc. here.
              </p>
              <input
                type="file"
                multiple
                className="file-input file-input-bordered w-full max-w-xs"
                onChange={handleFileChange}
                accept="application/pdf"
              />
              <div className="modal-action">
                <button className="btn btn-primary" onClick={handleModalToggle}>
                  Close
                </button>
                <button className="btn btn-secondary" onClick={handleSubmit}>
                  Submit
                </button>
              </div>
            </div>
          </div>
        )}
        {extractedText && (
          <div className="mt-8 p-4 bg-gray-800 text-white rounded-lg w-3/4">
            <h2 className="text-lg font-bold text-primary">Extracted Text:</h2>
            <pre className="whitespace-pre-wrap max-h-96 overflow-auto">
              {extractedText}
            </pre>
          </div>
        )}
        {snippets.length > 0 && (
          <div className="mt-8 p-4 bg-gray-800 text-white rounded-lg w-3/4">
            <h2 className="text-lg font-bold text-primary">
              Educational Snippets:
            </h2>
            {snippets.map((snippet, index) => (
              <div key={index} className="p-2 my-2 bg-gray-700 rounded">
                <p>{snippet}</p>
              </div>
            ))}
          </div>
        )}
      </main>
    </main>
  );
}
