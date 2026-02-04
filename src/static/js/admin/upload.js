// static/js/admin/upload.js
// Handles file upload, validation, result display and data loading

let selectedFile = null;
let currentStep = 1;

// DOM elements cache
const elements = {
    dropZone: document.getElementById('drop-zone'),
    fileInput: document.getElementById('file-upload'),
    fileInfo: document.getElementById('file-info'),
    fileNameEl: document.getElementById('file-name'),
    fileSizeEl: document.getElementById('file-size'),
    validateBtn: document.getElementById('validate-btn'),
    uploadSection: document.getElementById('upload-section'),
    validationSection: document.getElementById('validation-section'),
    validationResults: document.getElementById('validation-results'),
    loadBtnContainer: document.getElementById('load-btn-container'),
    loadBtn: document.getElementById('load-btn'),
    loadSection: document.getElementById('load-section'),
    loadResults: document.getElementById('load-results'),
    stepIndicators: [
        document.getElementById('step1-indicator'),
        document.getElementById('step2-indicator'),
        document.getElementById('step3-indicator')
    ]
};

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function updateStepIndicator(step) {
    elements.stepIndicators.forEach((el, idx) => {
        if (idx < step - 1) {
            el.className = 'rounded-circle bg-success text-white d-flex align-items-center justify-content-center fw-bold mx-auto mb-2';
            el.textContent = '✓';
        } else if (idx === step - 1) {
            el.className = 'rounded-circle bg-primary text-white d-flex align-items-center justify-content-center fw-bold mx-auto mb-2';
            el.textContent = step;
        } else {
            el.className = 'rounded-circle bg-secondary text-white d-flex align-items-center justify-content-center fw-bold mx-auto mb-2';
            el.textContent = idx + 1;
        }
    });
}

function resetUI() {
    selectedFile = null;
    currentStep = 1;
    updateStepIndicator(1);

    elements.fileInfo.classList.add('d-none');
    elements.validateBtn.disabled = true;
    elements.uploadSection.classList.remove('d-none');
    elements.validationSection.classList.add('d-none');
    elements.loadSection.classList.add('d-none');
    elements.validationResults.innerHTML = '';
    elements.loadResults.innerHTML = '';

    if (elements.fileInput) elements.fileInput.value = '';
}

function showError(message) {
    elements.validationResults.innerHTML = `
        <div class="alert alert-danger">
            <strong>Fout:</strong> ${message}
        </div>
    `;
    elements.loadBtnContainer.classList.add('d-none');
}

function showValidationSuccess(validation) {
    let html = '<div class="alert alert-success mb-4">Bestandstructuur is geldig ✓</div>';

    if (validation.summary) {
        html += `
            <div class="card mb-3">
                <div class="card-header bg-light">
                    <strong>Samenvatting</strong>
                </div>
                <div class="card-body">
                    <ul class="list-group list-group-flush">
        `;
        if (validation.summary.sheets) {
            html += `<li class="list-group-item">Bladen: <strong>${validation.summary.sheets.join(', ')}</strong></li>`;
        }
        if (validation.summary.rows !== undefined) {
            html += `<li class="list-group-item">Rijen (excl. header): <strong>${validation.summary.rows}</strong></li>`;
        }
        if (validation.summary.expected_columns) {
            html += `<li class="list-group-item">Verwachte kolommen: <strong>${validation.summary.expected_columns}</strong></li>`;
        }
        html += '</ul></div></div>';
    }

    // Warnings (if any)
    if (validation.warnings?.length > 0) {
        html += `
            <div class="alert alert-warning mt-3">
                <strong>Waarschuwingen (${validation.warnings.length})</strong>
                <ul class="mb-0">
                    ${validation.warnings.map(w => `<li>${w}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    elements.validationResults.innerHTML = html;
    elements.loadBtnContainer.classList.remove('d-none');
}

function showValidationErrors(errors) {
    let html = `
        <div class="alert alert-danger">
            <strong>Validatie mislukt (${errors.length} ${errors.length === 1 ? 'fout' : 'fouten'})</strong>
            <ul class="mb-0 mt-2">
                ${errors.map(err => `<li>${err}</li>`).join('')}
            </ul>
        </div>
    `;
    elements.validationResults.innerHTML = html;
    elements.loadBtnContainer.classList.add('d-none');
}

async function validateFile() {
    if (!selectedFile) return;

    elements.validateBtn.disabled = true;
    elements.validateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Valideren...';

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/admin/upload/validate', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok || !result.valid) {
            showValidationErrors(result.errors || ['Onbekende validatiefout']);
            return;
        }

        // Success → go to step 2
        currentStep = 2;
        updateStepIndicator(2);
        elements.uploadSection.classList.add('d-none');
        elements.validationSection.classList.remove('d-none');

        showValidationSuccess(result);

    } catch (err) {
        console.error(err);
        showError('Verbinding met server mislukt: ' + err.message);
    } finally {
        elements.validateBtn.disabled = false;
        elements.validateBtn.textContent = 'Valideer bestand';
    }
}

async function loadData() {
    elements.loadBtn.disabled = true;
    elements.loadBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Bezig met laden...';

    try {
        const response = await fetch('/admin/upload/load', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const result = await response.json();

        elements.loadSection.classList.remove('d-none');
        elements.validationSection.classList.add('d-none');
        currentStep = 3;
        updateStepIndicator(3);

        if (result.success) {
            elements.loadResults.innerHTML = `
                <div class="alert alert-success">
                    <h5>Succes!</h5>
                    <p>${result.message}</p>
                    ${result.stats ? `
                        <ul class="list-group mt-3">
                            ${Object.entries(result.stats).map(([k, v]) => `
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>${k}</span>
                                    <strong>${v}</strong>
                                </li>
                            `).join('')}
                        </ul>
                    ` : ''}
                </div>
            `;
        } else {
            elements.loadResults.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Fout bij laden:</strong><br>
                    ${result.error || 'Onbekende fout'}
                </div>
            `;
        }

    } catch (err) {
        console.error(err);
        elements.loadResults.innerHTML = `
            <div class="alert alert-danger">
                Verbinding mislukt: ${err.message}
            </div>
        `;
    } finally {
        elements.loadBtn.disabled = false;
        elements.loadBtn.textContent = 'Data laden in database';
    }
}

function cancelUpload() {
    fetch('/admin/upload/cancel', { method: 'POST' })
        .catch(err => console.warn('Cancel request failed', err))
        .finally(() => {
            resetUI();
        });
}

// ────────────────────────────────────────────────
// Event listeners
// ────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    if (!elements.dropZone) return;

    // Drag & drop
    ['dragenter', 'dragover'].forEach(event => {
        elements.dropZone.addEventListener(event, e => {
            e.preventDefault();
            e.stopPropagation();
            elements.dropZone.classList.add('border-primary', 'bg-primary-subtle');
        });
    });

    ['dragleave', 'drop'].forEach(event => {
        elements.dropZone.addEventListener(event, e => {
            e.preventDefault();
            e.stopPropagation();
            elements.dropZone.classList.remove('border-primary', 'bg-primary-subtle');
        });
    });

    elements.dropZone.addEventListener('drop', e => {
        if (e.dataTransfer.files.length > 0) {
            selectedFile = e.dataTransfer.files[0];
            showSelectedFile();
        }
    });

    elements.fileInput.addEventListener('change', () => {
        if (elements.fileInput.files.length > 0) {
            selectedFile = elements.fileInput.files[0];
            showSelectedFile();
        }
    });

    function showSelectedFile() {
        if (!selectedFile) return;
        elements.fileNameEl.textContent = selectedFile.name;
        elements.fileSizeEl.textContent = formatFileSize(selectedFile.size);
        elements.fileInfo.classList.remove('d-none');
        elements.validateBtn.disabled = false;
    }

    elements.validateBtn.addEventListener('click', validateFile);
    elements.loadBtn.addEventListener('click', loadData);

    // Cancel buttons (there might be more than one in future)
    document.querySelectorAll('[onclick="cancelUpload()"]').forEach(btn => {
        btn.addEventListener('click', cancelUpload);
    });
});