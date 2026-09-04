const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export interface UploadResponse {
  document_id: string;
  file_url: string;
  status: string;
}

export async function uploadDocument(params: {
  file: File;
  exam: "JEE" | "NEET" | "OTHER";
  studentClass: "11" | "12";
  userId: string; // placeholder until auth is wired in
}): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", params.file);
  formData.append("exam", params.exam);
  formData.append("class", params.studentClass);
  formData.append("user_id", params.userId);

  const res = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Upload failed with status ${res.status}`);
  }

  return res.json();
}

export interface ExtractResponse {
  document_id: string;
  status: string;
  char_count: number;
  text_preview: string;
}

export async function extractText(documentId: string): Promise<ExtractResponse> {
  const res = await fetch(`${API_BASE_URL}/api/documents/${documentId}/extract-text`, {
    method: "POST",
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Extraction failed with status ${res.status}`);
  }

  return res.json();
}
