import { NextResponse } from "next/server";
import pdfParse from "pdf-parse";

export async function POST(req) {
  try {
    const formData = await req.formData();
    const files = formData.getAll("files");

    if (!files.length) {
      return NextResponse.json({ error: "No files uploaded" }, { status: 400 });
    }

    let extractedTexts = [];

    for (const file of files) {
      const buffer = await file.arrayBuffer();
      const data = await pdfParse(Buffer.from(buffer)); // Extract text
      extractedTexts.push({ name: file.name, text: data.text });
    }

    return NextResponse.json({ extractedTexts });
  } catch (error) {
    console.error("Error extracting text:", error);
    return NextResponse.json(
      { error: "Failed to process files" },
      { status: 500 }
    );
  }
}
