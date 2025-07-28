// import { Document, Page } from 'react-pdf';
// import 'react-pdf/dist/esm/Page/AnnotationLayer.css';

// const PDFPreview = ({ file }) => {
//   return (
//     <div className="my-4">
//       {file && (
//         <Document file={file}>
//           <Page pageNumber={1} />
//         </Document>
//       )}
//     </div>
//   );
// };

// export default PDFPreview;
import { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const PDFPreview = ({ file }) => {
  const [numPages, setNumPages] = useState(null);
  const [fileUrl, setFileUrl] = useState(null);

  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setFileUrl(url);
      return () => URL.revokeObjectURL(url); // Clean up memory leak
    }
  }, [file]);

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
  };

  return (
    <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
      {fileUrl ? (
        <Document
          file={fileUrl}
          onLoadSuccess={onDocumentLoadSuccess}
          onLoadError={(error) => console.error('PDF load error:', error)}
        >
          {Array.from(new Array(numPages), (el, index) => (
            <div key={`page_${index + 1}`} className="mb-4 shadow-lg">
              <Page pageNumber={index + 1} />
            </div>
          ))}
        </Document>
      ) : (
        <p className="text-gray-500">No file selected yet.</p>
      )}
    </div>
  );
};

export default PDFPreview;
