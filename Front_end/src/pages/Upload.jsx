import { useState } from 'react';
import axios from 'axios';
import PDFPreview from '../components/PDFPreview';
import toast from 'react-hot-toast';
import { UploadCloud } from 'lucide-react';

const Upload = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return toast.error('Please select a file!');
    setIsLoading(true);

    const formData = new FormData();
    formData.append('pdf', file);

    try {
      const res = await axios.post('http://localhost:5000/extract', formData);
      setResult(res.data);
      toast.success('Upload successful!');
    } catch (err) {
      console.error('Upload error:', err);
      toast.error('Upload failed!');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Upload box */}
      <div
        className="border-2 border-dashed border-pink-400 dark:border-pink-500 rounded-2xl p-10 flex flex-col items-center justify-center
                   bg-white/60 dark:bg-black/30 backdrop-blur-md shadow-lg hover:shadow-pink-400 transition-all duration-300"
      >
        <UploadCloud className="text-pink-500 dark:text-pink-400 mb-4" size={48} />
        <p className="mb-4 text-gray-700 dark:text-gray-300 font-medium">Drop your PDF here or click to select</p>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          className="cursor-pointer"
        />
      </div>

      {/* Upload Button */}
      <div className="text-center mt-6">
        <button
          onClick={handleUpload}
          disabled={!file || isLoading}
          className={`px-6 py-3 rounded-full font-semibold transition-all duration-300 
            ${file
              ? 'bg-gradient-to-r from-pink-500 to-red-500 text-white hover:scale-105 shadow-lg'
              : 'bg-gray-300 dark:bg-gray-700 text-gray-500 cursor-not-allowed'}`}
        >
          {isLoading ? 'Uploading...' : 'Upload & Extract'}
        </button>
      </div>

      {/* Preview PDF */}
      {file && (
        <div className="mt-10">
          <h2 className="text-xl font-bold text-pink-500 mb-2">PDF Preview</h2>
          <PDFPreview file={file} />
        </div>
      )}

      {/* Show Extracted Outline */}
      {result && (
        <div className="mt-10 bg-white dark:bg-gray-900 p-6 rounded-xl shadow-md">
          <h2 className="text-2xl font-bold mb-4 text-red-500">📄 {result.title}</h2>
          <div className="space-y-2">
            {result.outline.map((h, i) => (
              <div
                key={i}
                className="border-l-4 pl-4 py-2 hover:bg-pink-50 dark:hover:bg-gray-800 rounded-md transition-all duration-200
                  border-pink-400 dark:border-pink-500"
              >
                <p>
                  <strong>{h.level}</strong> – {h.text} <span className="text-sm text-gray-500">(Page {h.page})</span>
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Upload;

