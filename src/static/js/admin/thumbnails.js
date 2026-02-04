// static/js/admin/thumbnails.js
async function regenerateThumbnails() {
    const btn = document.getElementById('regenerate-btn');
    const resultDiv = document.getElementById('thumbnail-result');

    if (!btn || !resultDiv) return;

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> Bezig...';

    try {
        const response = await fetch('{{ url_for("admin.regenerate_thumbnails") }}', {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            resultDiv.innerHTML = `
                <div class="alert alert-success mt-3">
                    ✓ ${result.count} thumbnails succesvol gegenereerd
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger mt-3">
                    ✗ ${result.error || 'Onbekende fout'}
                </div>
            `;
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="alert alert-danger mt-3">
                ✗ Verbinding mislukt: ${error.message}
            </div>
        `;
    } finally {
        btn.disabled = false;
        btn.textContent = 'Regenereer Thumbnails';
    }
}