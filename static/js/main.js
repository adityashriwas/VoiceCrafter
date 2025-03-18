let currentModelPath = 'default_voice';
let currentAudioPath = null;

function showAlert(message, isError = false) {
    const toast = document.getElementById('alertToast');
    const toastBody = toast.querySelector('.toast-body');
    toastBody.textContent = message;
    toast.classList.toggle('bg-danger', isError);
    toast.classList.toggle('text-white', isError);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

function showProgress(elementId, show = true) {
    const progress = document.getElementById(elementId);
    if (show) {
        progress.classList.remove('d-none');
        progress.querySelector('.progress-bar').style.width = '100%';
    } else {
        progress.classList.add('d-none');
        progress.querySelector('.progress-bar').style.width = '0%';
    }
}

async function uploadVoice() {
    const fileInput = document.getElementById('audioFile');
    const file = fileInput.files[0];

    if (!file) {
        showAlert('Please select a file first', true);
        return;
    }

    const formData = new FormData();
    formData.append('audio', file);

    try {
        showProgress('uploadProgress');
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            currentModelPath = data.model_path;
            showAlert('Voice profile created successfully');
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        showAlert(error.message || 'Error uploading file', true);
        currentModelPath = 'default_voice';
    } finally {
        showProgress('uploadProgress', false);
    }
}

async function generateAudio() {
    const text = document.getElementById('inputText').value.trim();

    if (!text) {
        showAlert('Please enter some text', true);
        return;
    }

    try {
        showProgress('generateProgress');
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                model_path: currentModelPath
            })
        });

        const data = await response.json();

        if (response.ok) {
            currentAudioPath = data.audio_path;
            const audioOutput = document.getElementById('audioOutput');
            const audioPlayer = document.getElementById('audioPlayer');

            audioOutput.classList.remove('d-none');
            audioPlayer.src = `/download/${encodeURIComponent(currentAudioPath)}`;
            showAlert('Audio generated successfully');
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        showAlert(error.message || 'Error generating audio', true);
    } finally {
        showProgress('generateProgress', false);
    }
}

function downloadAudio() {
    if (currentAudioPath) {
        window.location.href = `/download/${encodeURIComponent(currentAudioPath)}`;
    }
}