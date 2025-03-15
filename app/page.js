"use client";
import Image from "next/image";
import { useState } from "react";

export default function Home() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleModalToggle = () => {
    setIsModalOpen(!isModalOpen);
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
          <div className="modal modal-open">
            <div className="modal-box">
              <h2 className="font-bold text-lg">Upload Modal</h2>
              <p className="py-4">Your content goes here...</p>
              <div className="modal-action">
                <button className="btn" onClick={handleModalToggle}>
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
      );
    </main>
  );
}
