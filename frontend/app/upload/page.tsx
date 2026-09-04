import UploadForm from "@/components/UploadForm";

export default function UploadPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      <h1 className="text-2xl font-semibold text-center pt-10">
        Upload a Question Paper
      </h1>
      <UploadForm />
    </main>
  );
}
