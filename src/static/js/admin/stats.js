// static/js/admin/stats.js
async function loadStats() {
    try {
        const response = await fetch('{{ url_for("admin.get_stats") }}');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        // Update stat cards
        document.getElementById('stat-members').textContent     = data.leden?.toLocaleString()         || '—';
        document.getElementById('stat-performances').textContent = data.voorstellingen?.toLocaleString() || '—';
        document.getElementById('stat-roles').textContent       = data.rollen?.toLocaleString()         || '—';
        document.getElementById('stat-media').textContent       = data.media?.toLocaleString()          || '—';

        // Media breakdown
        const breakdownDiv = document.getElementById('media-breakdown');
        if (!breakdownDiv) return;

        breakdownDiv.innerHTML = '';

        if (Array.isArray(data.media_breakdown) && data.media_breakdown.length > 0) {
            data.media_breakdown.forEach(item => {
                const row = document.createElement('div');
                row.className = 'd-flex justify-content-between py-2 border-bottom';
                row.innerHTML = `
                    <span class="text-capitalize">${item.type_media}</span>
                    <span class="fw-bold">${item.count.toLocaleString()}</span>
                `;
                breakdownDiv.appendChild(row);
            });
        } else {
            breakdownDiv.innerHTML = '<p class="text-muted">Geen data beschikbaar</p>';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        const el = document.getElementById('media-breakdown');
        if (el) {
            el.innerHTML = '<p class="text-danger">Fout bij laden van statistieken</p>';
        }
    }
}

// Auto-load stats when the page is ready (most dashboard pages want this)
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
});