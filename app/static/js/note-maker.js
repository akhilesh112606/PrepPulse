document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const noteForm = document.getElementById('note-form');
    const generateBtn = document.getElementById('generate-btn');
    const previewContent = document.getElementById('preview-content');
    const wordCount = document.getElementById('word-count');
    const pdfSection = document.getElementById('pdf-section');
    const pdfTitle = document.getElementById('pdf-title');
    const pdfMeta = document.getElementById('pdf-meta');
    const pdfViewer = document.getElementById('pdf-viewer');
    const downloadBtn = document.getElementById('download-btn');
    const shareBtn = document.getElementById('share-btn');
    
    // Upload Modal Elements
    const uploadModal = document.getElementById('upload-modal');
    const uploadForm = document.getElementById('upload-form');
    const cancelUpload = document.getElementById('cancel-upload');
    const confirmUpload = document.getElementById('confirm-upload');
    
    // State
    let currentNotes = '';
    let currentPdfBlob = null;
    
    // Utility Functions
    function showError(message) {
        // Create and show error notification
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #dc2626;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(220, 38, 38, 0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div>Error</div>
                <div>${message}</div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    function showSuccess(message) {
        const notification = document.createElement('div');
        notification.className = 'success-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(16, 185, 129, 0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div>Success</div>
                <div>${message}</div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    function updateWordCount(text) {
        const words = text.trim().split(/\s+/).filter(word => word.length > 0).length;
        wordCount.textContent = `${words} words`;
    }
    
    function setLoadingState(loading) {
        const btnText = generateBtn.querySelector('.btn-text');
        
        if (loading) {
            generateBtn.disabled = true;
            btnText.innerHTML = '<span class="loading-spinner"></span>Generating Notes...';
        } else {
            generateBtn.disabled = false;
            btnText.innerHTML = '<svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14"/><path d="M5 12h14"/></svg>Generate Notes';
        }
    }
    
    function setPdfLoadingState(loading) {
        if (loading) {
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '<span class="loading-spinner"></span>Creating PDF...';
        } else {
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = '<svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>Download PDF';
        }
    }
    
    function setUploadLoadingState(loading) {
        if (loading) {
            confirmUpload.disabled = true;
            confirmUpload.innerHTML = '<span class="loading-spinner"></span>Uploading...';
        } else {
            confirmUpload.disabled = false;
            confirmUpload.innerHTML = '<svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>Upload for Approval';
        }
    }
    
    // Note Generation
    async function generateNotes(formData) {
        try {
            setLoadingState(true);
            
            const response = await fetch('/api/notes/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    subject: formData.get('subject'),
                    topic: formData.get('topic'),
                    pages: parseInt(formData.get('pages'))
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate notes');
            }
            
            // Keep only status text here; the real preview is the PDF viewer below.
            currentNotes = data.content;
            if (previewContent) {
                previewContent.innerHTML = `
                    <div class="preview-empty">
                        <div class="preview-empty-icon">
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="13" y2="17"/></svg>
                        </div>
                        <div>Notes generated successfully</div>
                        <div style="font-size: 0.9rem; margin-top: 0.5rem;">Scroll down to preview the generated PDF.</div>
                    </div>
                `;
            }
            if (wordCount) {
                updateWordCount(currentNotes);
            }
            
            // Auto-generate PDF
            await createPDF(formData.get('subject'), formData.get('topic'));
            
            showSuccess('Notes generated successfully!');
            
        } catch (error) {
            console.error('Error generating notes:', error);
            showError(error.message || 'Failed to generate notes. Please try again.');
        } finally {
            setLoadingState(false);
        }
    }
    
    // PDF Creation
    async function createPDF(subject, topic) {
        try {
            setPdfLoadingState(true);
            
            const response = await fetch('/api/notes/create-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    subject: subject,
                    topic: topic,
                    content: currentNotes
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to create PDF');
            }
            
            // Get PDF blob
            currentPdfBlob = await response.blob();
            
            // Create object URL for preview
            const pdfUrl = URL.createObjectURL(currentPdfBlob);
            
            // Update PDF preview
            pdfTitle.textContent = `${subject} - ${topic}`;
            pdfMeta.textContent = `Generated on ${new Date().toLocaleDateString()} | ${Math.ceil(currentNotes.length / 2000)} pages`;
            pdfViewer.src = pdfUrl;
            
            // Show PDF section
            pdfSection.classList.remove('hidden');
            pdfSection.scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            console.error('Error creating PDF:', error);
            showError(error.message || 'Failed to create PDF. Please try again.');
        } finally {
            setPdfLoadingState(false);
        }
    }
    
    // PDF Download
    function downloadPDF() {
        if (!currentPdfBlob) {
            showError('No PDF available for download');
            return;
        }
        
        const subject = document.getElementById('subject').value;
        const topic = document.getElementById('topic').value;
        const filename = `${subject}_${topic}_Notes.pdf`.replace(/[^a-zA-Z0-9_-]/g, '_');
        
        const url = URL.createObjectURL(currentPdfBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showSuccess('PDF downloaded successfully!');
    }
    
    // Upload to Resources
    async function uploadToResources(formData) {
        try {
            setUploadLoadingState(true);
            
            const subject = document.getElementById('subject').value;
            const topic = document.getElementById('topic').value;
            
            const uploadData = new FormData();
            uploadData.append('file', currentPdfBlob, `${subject}_${topic}_Notes.pdf`);
            uploadData.append('subject', subject);
            uploadData.append('topic', topic);
            uploadData.append('branch', formData.get('branch'));
            uploadData.append('year', formData.get('year'));
            uploadData.append('academic_year', formData.get('academic_year'));
            
            const response = await fetch('/api/notes/upload-to-resources', {
                method: 'POST',
                body: uploadData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to upload notes');
            }
            
            hideUploadModal();
            showSuccess('Notes submitted for admin approval! They will be available to other students once approved.');
            
        } catch (error) {
            console.error('Error uploading notes:', error);
            showError(error.message || 'Failed to upload notes. Please try again.');
        } finally {
            setUploadLoadingState(false);
        }
    }
    
    // Modal Functions
    function showUploadModal() {
        uploadModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
    
    function hideUploadModal() {
        uploadModal.classList.add('hidden');
        document.body.style.overflow = 'auto';
        uploadForm.reset();
    }
    
    // Event Listeners
    noteForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        await generateNotes(formData);
    });
    
    downloadBtn.addEventListener('click', downloadPDF);
    
    shareBtn.addEventListener('click', function() {
        if (!currentPdfBlob) {
            showError('No PDF available to share');
            return;
        }
        showUploadModal();
    });
    
    cancelUpload.addEventListener('click', hideUploadModal);
    
    confirmUpload.addEventListener('click', async function() {
        const formData = new FormData(uploadForm);
        
        // Validate form
        if (!formData.get('branch') || !formData.get('year') || !formData.get('academic_year')) {
            showError('Please fill all fields');
            return;
        }
        
        await uploadToResources(formData);
    });
    
    // Close modal on backdrop click
    uploadModal.addEventListener('click', function(e) {
        if (e.target === uploadModal) {
            hideUploadModal();
        }
    });
    
    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !uploadModal.classList.contains('hidden')) {
            hideUploadModal();
        }
    });
    
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .upload-modal {
            backdrop-filter: blur(5px);
        }
        
        .upload-modal-content {
            animation: modalSlideIn 0.3s ease-out;
        }
        
        @keyframes modalSlideIn {
            from {
                transform: scale(0.9);
                opacity: 0;
            }
            to {
                transform: scale(1);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
});