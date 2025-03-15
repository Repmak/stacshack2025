"use client";
import { useState } from "react";
import { extractTextFromPdfs } from "../utils/pdfUtils";
import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.NEXT_PUBLIC_GEMINI_API_KEY);

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

      await generateSnippets(extracted);
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
      const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

      const prompt = `Extract five **distinct** 150-word educational snippets from the following text.
      Each snippet should focus on a **separate topic**, avoiding redundancy.
      Ensure the format follows this structure:
      
      **[Topic Title]**  
      [150-word explanation]  
      
      **[Topic Title]**  
      [150-word explanation]  
      
      Continue this pattern for all five snippets.
  
      Here is the text:
      ${text}`;

      const result = await model.generateContent(prompt);
      const response = await result.response;
      const generatedText = await response.text();

      const snippetsWithTitles = generatedText
        .split(/\n\n(?=\*\*.+?\*\*)/)
        .slice(0, 5)
        .map((snippet, index) => ({
          [`Snippet ${index + 1}`]: snippet.replace(/^\*\*\d+\. .*?\*\* /, ""),
        }));

      const snippetsJson = snippetsWithTitles.reduce((acc, snippet) => {
        return { ...acc, ...snippet };
      }, {});

      console.log(snippetsJson);
      setSnippets(JSON.stringify(snippetsJson));

      fetch("http://localhost:5000/api/upload_data", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(snippetsJson),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok.");
          }
          return response.json();
        })
        .then((data) => {
          console.log("Predictions received:", data);
        })
        .catch((error) => {
          console.error("Error fetching predictions from Flask:", error);
        });
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
      </main>
    </main>
  );
}
