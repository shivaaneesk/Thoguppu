document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('audio_file');
    const fileNameDisplay = document.getElementById('file-name');
    const form = document.getElementById('upload-form');
    const themeBtn = document.getElementById('theme-switcher');

    // --- Theme Switcher ---
    themeBtn.addEventListener('click', () => {
        const body = document.body;
        if (body.classList.contains('light-theme')) {
            body.classList.replace('light-theme', 'dark-theme');
        } else {
            body.classList.replace('dark-theme', 'light-theme');
        }
    });

    // --- File Name Display ---
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            fileNameDisplay.textContent = fileInput.files[0].name;
            fileNameDisplay.style.fontWeight = "bold";
        } else {
            fileNameDisplay.textContent = "No file chosen";
        }
    });

    // --- Form Submission ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (fileInput.files.length === 0) {
            alert("Please select a file first!");
            return;
        }

        // 1. Reset UI
        document.getElementById('results').classList.add('hidden');
        document.getElementById('error').classList.add('hidden');

        // 2. Show Loading & Progress Bar
        document.getElementById('loading').classList.remove('hidden');
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = "Processing...";

        const formData = new FormData();
        formData.append('audio_file', fileInput.files[0]);

        try {
            // 3. Send to Backend
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Processing failed");
            }

            // 4. Show Results
            document.getElementById('transcript-text').textContent = data.transcript;
            document.getElementById('summary-text').textContent = data.summary;
            document.getElementById('results').classList.remove('hidden');

        } catch (error) {
            // Handle Errors
            document.getElementById('error-text').textContent = "Error: " + error.message;
            document.getElementById('error').classList.remove('hidden');
        } finally {
            // 5. Hide Loading & Reset Button
            document.getElementById('loading').classList.add('hidden');
            submitBtn.disabled = false;
            submitBtn.textContent = "Process Audio";
        }
    });
});