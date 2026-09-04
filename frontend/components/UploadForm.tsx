"use client";

import { useState } from "react";
import { uploadDocument, extractText, ExtractResponse } from "@/lib/api";

// TEMPORARY: replace with the real logged-in user's id once Supabase Auth (phone/OTP) is wired in.
const PLACEHOLDER_USER_ID = "00000000-0000-0000-0000-000000000000";

export default function UploadForm() {
  const [exam, setExam] = useState<"JEE" | "NEET" | "OTHER">("JEE");
  const [studentClass, setStudentClass] = useState<"11" | "12">("11");
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<
    "idle" | "uploading" | "extracting" | "done" | "error"
  >("idle");
  const [message, setMessage] = useState<string>("");
  const [extraction, setExtraction] = useState<ExtractResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setMessage("Please choose a file first.");
      return;
    }

    setStatus("uploading");
    setMessage("");

    try {
      const uploadResult = await uploadDocument({
        file,
        exam,
        studentClass,
        userId: PLACEHOLDER_USER_ID,
      });

      setStatus("extracting");
      setMessage("Extracting text...");

      const extractResult = await extractText(uploadResult.document_id);
      setExtraction(extractResult);

      if (extractResult.status === "text_extracted") {
        setStatus("done");
        setMessage(`Extracted ${extractResult.char_count} characters.`);
      } else {
        setStatus("error");
        setMessage("No text could be extracted from this file.");
      }
    } catch (err: any) {
      setStatus("error");
      setMessage(err.message || "Something went wrong.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-6 space-y-5">
      <div>
        <label className="block text-sm font-medium mb-1">Exam</label>
        <select
          value={exam}
          onChange={(e) =>
            setExam(e.target.value as "JEE" | "NEET" | "OTHER")
          }
          className="w-full border rounded-md p-2"
        >
          <option value="JEE">JEE</option>
          <option value="NEET">NEET</option>
          <option value="OTHER">Other</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Class</label>
        <select
          value={studentClass}
          onChange={(e) => setStudentClass(e.target.value as "11" | "12")}
          className="w-full border rounded-md p-2"
        >
          <option value="11">11</option>
          <option value="12">12</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">
          Question paper (PDF, JPG, or PNG)
        </label>

        {/* capture="environment" opens the rear camera directly on mobile browsers */}
        <input
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          capture="environment"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="w-full border rounded-md p-2"
        />
      </div>

      <button
        type="submit"
        disabled={status === "uploading" || status === "extracting"}
        className="w-full bg-black text-white rounded-md py-2 disabled:opacity-50"
      >
        {status === "uploading"
          ? "Uploading..."
          : status === "extracting"
            ? "Extracting..."
            : "Upload"}
      </button>

      {message && (
        <p
          className={`text-sm ${
            status === "error" ? "text-red-600" : "text-green-700"
          }`}
        >
          {message}
        </p>
      )}

      {extraction && extraction.status === "text_extracted" && (
        <div className="border rounded-md p-3 bg-white text-sm text-gray-700 whitespace-pre-wrap">
          {extraction.text_preview}
        </div>
      )}
    </form>
  );
}