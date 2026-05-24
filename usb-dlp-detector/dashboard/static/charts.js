/* ============================================================
   USB DLP Dashboard – Data Fetch & Chart Rendering
   "If your chart doesn't have a gradient, does it even security?"
   ============================================================ */

// ─── THEME-AWARE CHART DEFAULTS ───
function getThemeColors() {
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    return {
        text: isDark ? '#94a3b8' : '#64748b',
        grid: isDark ? 'rgba(148,163,184,.08)' : 'rgba(0,0,0,.06)',
        gridFine: isDark ? 'rgba(148,163,184,.06)' : 'rgba(0,0,0,.04)',
        cardBg: isDark ? '#1a2236' : '#ffffff',
        accentLine: isDark ? '#818cf8' : '#6366f1',
        accentFillTop: isDark ? 'rgba(99,102,241,.3)' : 'rgba(99,102,241,.15)',
        accentFillBot: isDark ? 'rgba(99,102,241,0)' : 'rgba(99,102,241,0)',
        pointBorder: isDark ? '#1a2236' : '#ffffff',
    };
}

function applyChartDefaults() {
    const c = getThemeColors();
    Chart.defaults.color = c.text;
    Chart.defaults.borderColor = c.grid;
    Chart.defaults.font.family = "'Inter', sans-serif";
}

applyChartDefaults();

// ─── DATA LOADERS ───

async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        const stats = await res.json();
        animateNumber('stat-connections', stats.usb_connections);
        animateNumber('stat-files', stats.files_transferred);
        animateNumber('stat-alerts', stats.total_alerts);
        document.getElementById('alert-badge').textContent = stats.total_alerts;
    } catch (e) {
        console.error('Error loading stats:', e);
    }
}

async function loadAlerts() {
    try {
        const res = await fetch('/api/alerts');
        const alerts = await res.json();
        const tbody = document.querySelector('#table-alerts tbody');
        if (!alerts.length) {
            tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><div class="empty-icon">🛡️</div><p>No alerts detected — system secure</p></div></td></tr>';
            return;
        }
        tbody.innerHTML = alerts.map(a => {
            const sev = (a.severity || 'Unknown').toLowerCase();
            const riskClass = a.risk_score >= 80 ? 'high' : (a.risk_score >= 40 ? 'medium' : 'low');
            return `<tr>
                <td class="mono">${formatTime(a.timestamp)}</td>
                <td>${esc(a.username || 'Unknown')}</td>
                <td class="mono" title="${esc(a.device_id)}">${esc(truncate(a.device_id, 20))}</td>
                <td><span class="risk-pill ${riskClass}">${a.risk_score}</span></td>
                <td><span class="severity-badge ${sev}">${esc(a.severity || 'Unknown')}</span></td>
                <td>${esc(a.reason)}</td>
            </tr>`;
        }).join('');
    } catch (e) {
        console.error('Error loading alerts:', e);
    }
}

async function loadDevices() {
    try {
        const res = await fetch('/api/usb_devices');
        const devices = await res.json();
        const tbody = document.querySelector('#table-devices tbody');
        if (!devices.length) {
            tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><div class="empty-icon">🔌</div><p>No USB connections detected</p></div></td></tr>';
            return;
        }
        tbody.innerHTML = devices.map(d => {
            const wl = d.is_whitelisted ? '<span class="trust-badge positive">✓ Trusted</span>' : '<span class="trust-badge negative">✕ Unknown</span>';
            return `<tr>
                <td class="mono" title="${esc(d.device_id)}">${esc(truncate(d.device_id, 22))}</td>
                <td>${esc(d.vendor || 'Unknown')}</td>
                <td>${esc(d.username || 'Unknown')}</td>
                <td class="mono">${formatTime(d.connect_time)}</td>
                <td class="mono">${esc(d.mount_path || 'N/A')}</td>
                <td>${wl}</td>
            </tr>`;
        }).join('');
    } catch (e) {
        console.error('Error loading devices:', e);
    }
}

async function loadActivity() {
    try {
        const res = await fetch('/api/file_activity');
        const activity = await res.json();
        const tbody = document.querySelector('#table-activity tbody');
        if (!activity.length) {
            tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><div class="empty-icon">📁</div><p>No file transfers logged</p></div></td></tr>';
            return;
        }
        tbody.innerHTML = activity.map(f => `<tr>
            <td class="mono">${formatTime(f.timestamp)}</td>
            <td>${esc(f.username || 'Unknown')}</td>
            <td title="${esc(f.file_name)}">${esc(truncate(f.file_name, 30))}</td>
            <td>${formatSize(f.size)}</td>
            <td class="mono" title="${esc(f.file_hash || '')}">${f.file_hash ? esc(f.file_hash.substring(0, 16)) + '…' : 'N/A'}</td>
            <td>${f.speed_mbps ? f.speed_mbps.toFixed(2) + ' MB/s' : '—'}</td>
        </tr>`).join('');
    } catch (e) {
        console.error('Error loading activity:', e);
    }
}

async function loadTrust() {
    try {
        const res = await fetch('/api/device_trust');
        const trusts = await res.json();
        const tbody = document.querySelector('#table-trust tbody');
        if (!trusts.length) {
            tbody.innerHTML = '<tr><td colspan="4"><div class="empty-state"><div class="empty-icon">🔌</div><p>No USB devices registered</p></div></td></tr>';
            return;
        }
        tbody.innerHTML = trusts.map(t => {
            const cls = t.trust_score >= 20 ? 'positive' : (t.trust_score >= 0 ? 'neutral' : 'negative');
            return `<tr>
                <td class="mono" title="${esc(t.device_id)}">${esc(truncate(t.device_id, 24))}</td>
                <td class="mono">${formatTime(t.first_seen)}</td>
                <td><span class="trust-badge ${cls}">${t.trust_score}</span></td>
                <td>${esc(t.status || 'Unknown')}</td>
            </tr>`;
        }).join('');
    } catch (e) {
        console.error('Error loading trust:', e);
    }
}

async function loadHeatmap() {
    try {
        const res = await fetch('/api/heatmap_data');
        const data = await res.json();
        const container = document.getElementById('heatmap-container');
        container.innerHTML = '';

        const hoursMap = {};
        for (let i = 0; i < 24; i++) hoursMap[i.toString().padStart(2, '0')] = 0;
        data.forEach(d => { if (d.hour) hoursMap[d.hour] = d.avg_risk; });

        Object.keys(hoursMap).forEach(hour => {
            const risk = hoursMap[hour];
            let bg = 'var(--bg-card-hover)';
            let clr = 'var(--text-muted)';
            if (risk > 60) { bg = 'rgba(239,68,68,.7)'; clr = '#fff'; }
            else if (risk > 30) { bg = 'rgba(245,158,11,.6)'; clr = '#000'; }
            else if (risk > 0) { bg = 'rgba(34,197,94,.5)'; clr = '#fff'; }
            container.innerHTML += `<div class="heatmap-hour" style="background:${bg};color:${clr}" title="Hour ${hour}:00 — Avg Risk: ${risk.toFixed(0)}">${hour}</div>`;
        });
    } catch (e) {
        console.error('Error loading heatmap:', e);
    }
}

async function loadTimeline() {
    try {
        const res = await fetch('/api/timeline');
        const events = await res.json();
        const list = document.getElementById('timeline-list');
        if (!events.length) {
            list.innerHTML = '<li><div class="empty-state"><div class="empty-icon">🕒</div><p>No events recorded yet</p></div></li>';
            return;
        }
        list.innerHTML = events.map(evt => {
            const isAlert = evt.type === 'Alert';
            const dotClass = isAlert ? 'alert' : 'activity';
            const tagClass = isAlert ? 'alert' : 'activity';
            const riskStr = evt.risk_score ? `<span class="risk-pill ${evt.risk_score >= 60 ? 'high' : 'medium'}" style="margin-left:8px;font-size:.72rem">Risk: ${evt.risk_score}</span>` : '';
            return `<li class="timeline-item">
                <span class="timeline-dot ${dotClass}"></span>
                <div class="timeline-content">
                    <div class="time">${formatTime(evt.timestamp)}</div>
                    <div class="detail">
                        <span class="type-tag ${tagClass}">${evt.type}</span>
                        ${esc(evt.detail || 'N/A')}${riskStr}
                    </div>
                </div>
            </li>`;
        }).join('');
    } catch (e) {
        console.error('Error loading timeline:', e);
    }
}

async function loadAvgRisk() {
    try {
        const res = await fetch('/api/chart_data');
        const data = await res.json();
        if (data.risk_scores && data.risk_scores.length > 0) {
            const avg = data.risk_scores.reduce((a, b) => a + b, 0) / data.risk_scores.length;
            document.getElementById('stat-avgrisk').textContent = avg.toFixed(0);
        } else {
            document.getElementById('stat-avgrisk').textContent = '—';
        }
    } catch (e) {
        console.error('Error loading avg risk:', e);
    }
}

// ─── CHARTS ───

let filesChart, alertsChart, riskScoreChart;

async function loadCharts() {
    try {
        const res = await fetch('/api/chart_data');
        const data = await res.json();
        renderCharts(data);
    } catch (e) {
        console.error('Error loading charts:', e);
    }
}

function renderCharts(data) {
    applyChartDefaults();
    const tc = getThemeColors();

    if (filesChart) filesChart.destroy();
    if (alertsChart) alertsChart.destroy();
    if (riskScoreChart) riskScoreChart.destroy();

    // File Transfers Line Chart
    const ctxFiles = document.getElementById('filesChart').getContext('2d');
    const fileGradient = ctxFiles.createLinearGradient(0, 0, 0, 220);
    fileGradient.addColorStop(0, tc.accentFillTop);
    fileGradient.addColorStop(1, tc.accentFillBot);

    filesChart = new Chart(ctxFiles, {
        type: 'line',
        data: {
            labels: data.files_per_day.map(d => d.date).reverse(),
            datasets: [{
                label: 'Files / Day',
                data: data.files_per_day.map(d => d.count).reverse(),
                borderColor: tc.accentLine,
                backgroundColor: fileGradient,
                tension: 0.4,
                fill: true,
                borderWidth: 2,
                pointRadius: 4,
                pointBackgroundColor: tc.accentLine,
                pointBorderColor: tc.pointBorder,
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false } },
                y: { beginAtZero: true, grid: { color: tc.gridFine } }
            }
        }
    });

    // Alerts Bar Chart
    const ctxAlerts = document.getElementById('alertsChart').getContext('2d');
    alertsChart = new Chart(ctxAlerts, {
        type: 'bar',
        data: {
            labels: data.alerts_per_day.map(d => d.date).reverse(),
            datasets: [{
                label: 'Alerts / Day',
                data: data.alerts_per_day.map(d => d.count).reverse(),
                backgroundColor: 'rgba(239,68,68,.6)',
                hoverBackgroundColor: 'rgba(239,68,68,.85)',
                borderRadius: 6,
                borderSkipped: false,
                barPercentage: 0.6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false } },
                y: { beginAtZero: true, grid: { color: tc.gridFine } }
            }
        }
    });

    // Risk Distribution Doughnut
    const rb = { '0–20': 0, '21–40': 0, '41–60': 0, '61–80': 0, '81–100+': 0 };
    data.risk_scores.forEach(s => {
        if (s <= 20) rb['0–20']++;
        else if (s <= 40) rb['21–40']++;
        else if (s <= 60) rb['41–60']++;
        else if (s <= 80) rb['61–80']++;
        else rb['81–100+']++;
    });

    const ctxRisk = document.getElementById('riskScoreChart').getContext('2d');
    riskScoreChart = new Chart(ctxRisk, {
        type: 'doughnut',
        data: {
            labels: Object.keys(rb),
            datasets: [{
                data: Object.values(rb),
                backgroundColor: [
                    'rgba(34,197,94,.7)',
                    'rgba(59,130,246,.7)',
                    'rgba(245,158,11,.7)',
                    'rgba(249,115,22,.7)',
                    'rgba(239,68,68,.7)'
                ],
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 16,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        font: { size: 11 }
                    }
                }
            }
        }
    });
}

// ─── UTILITIES ───

function formatTime(timestamp) {
    if (!timestamp) return '—';
    try {
        const d = new Date(timestamp);
        if (isNaN(d.getTime())) return timestamp;
        return d.toLocaleString(undefined, {
            month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit'
        });
    } catch {
        return timestamp;
    }
}

function formatSize(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + units[i];
}

function truncate(str, len) {
    if (!str) return 'N/A';
    return str.length > len ? str.substring(0, len) + '…' : str;
}

// HTML escape to prevent XSS from DB data
function esc(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}

function animateNumber(elId, target) {
    const el = document.getElementById(elId);
    if (!el) return;
    const current = parseInt(el.textContent) || 0;
    if (current === target) return;
    const diff = target - current;
    const steps = 20;
    const increment = diff / steps;
    let step = 0;
    const timer = setInterval(() => {
        step++;
        el.textContent = Math.round(current + increment * step);
        if (step >= steps) {
            el.textContent = target;
            clearInterval(timer);
        }
    }, 30);
}

// ─── EXPOSE GLOBALLY ───
window.loadAlerts = loadAlerts;
window.loadStats = loadStats;
window.reloadCharts = loadCharts;

async function fetchAllData() {
    await Promise.all([
        loadStats(),
        loadAlerts(),
        loadDevices(),
        loadActivity(),
        loadTrust(),
        loadHeatmap(),
        loadTimeline(),
        loadCharts(),
        loadAvgRisk()
    ]);
}

window.fetchAllData = fetchAllData;

fetchAllData();
setInterval(fetchAllData, 5000);
