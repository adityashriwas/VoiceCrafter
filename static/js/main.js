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
                model_path: 'default_voice'  // Using default voice since we're using gTTS
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