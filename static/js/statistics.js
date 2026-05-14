/**
 * Statistics Dashboard JavaScript
 * Handles data fetching, chart rendering, and UI interactions
 */

let charts = {};
const SLA_THRESHOLD_HOURS = 48;

$(document).ready(function() {
    // Set default date range (last 30 days)
    const today = new Date();
    const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));
    
    $('#end_date').val(formatDateForInput(today));
    $('#start_date').val(formatDateForInput(thirtyDaysAgo));
    
    // Event listeners
    $('#btn_apply_filter').click(loadAllStats);
    $('#btn_reset_filter').click(resetFilter);
    $('#operators_container').on('click', '.operator-card', function(event) {
        if ($(event.target).closest('a, button').length) {
            return;
        }

        const index = $(this).data('operatorIndex');
        toggleOperator(index);
    });
    $('#operators_container').on('keydown', '.operator-card', function(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            const index = $(this).data('operatorIndex');
            toggleOperator(index);
        }
    });
    
    // Initial load
    loadAllStats();
});


/**
 * Format date for HTML5 date input (YYYY-MM-DD)
 */
function formatDateForInput(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}


/**
 * Format minutes to human-readable format
 */
function formatMinutes(minutes) {
    if (minutes === null || minutes === undefined) return '-';
    if (minutes < 60) {
        return Math.round(minutes) + 'm';
    }
    const hours = minutes / 60;
    if (hours < 24) {
        return hours.toFixed(1) + 'h';
    }
    const days = hours / 24;
    return days.toFixed(1) + 'd';
}


/**
 * Get query parameters for API calls
 */
function getDateParams() {
    return {
        start_date: $('#start_date').val(),
        end_date: $('#end_date').val()
    };
}


/**
 * Load all statistics
 */
function loadAllStats() {
    loadGlobalStats();
    loadCategoryStats();
    loadTrendStats();
    loadOperatorStats();
    loadSLAViolations();
}


/**
 * Load and render global statistics
 */
function loadGlobalStats() {
    const params = getDateParams();
    
    $.ajax({
        url: '/admin/api/stats/global',
        data: params,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            $('#kpi_total').text(data.total_tickets);
            $('#kpi_resolution').text(formatMinutes(data.avg_resolution_time_minutes));
            $('#kpi_response').text(formatMinutes(data.avg_response_time_minutes));
            $('#kpi_resolution_rate').text(data.resolution_rate_percent + '%');
            
            renderStatusChart(data.status_breakdown);
        },
        error: function(err) {
            console.error('Error loading global stats:', err);
            showError('Errore nel caricamento delle statistiche globali');
        }
    });
}


/**
 * Render status distribution pie chart
 */
function renderStatusChart(data) {
    const ctx = document.getElementById('chart_status');
    
    // Destroy existing chart if it exists
    if (charts['status']) {
        charts['status'].destroy();
    }
    
    charts['status'] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['NUOVO', 'IN LAVORAZIONE', 'RISOLTO'],
            datasets: [{
                data: [data.NUOVO, data.IN_LAVORAZIONE, data.RISOLTO],
                backgroundColor: [
                    '#0d6efd',  // Blue for NUOVO
                    '#fd7e14',  // Orange for IN_LAVORAZIONE
                    '#198754'   // Green for RISOLTO
                ],
                borderColor: '#ffffff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}


/**
 * Load and render category/priority statistics
 */
function loadCategoryStats() {
    $.ajax({
        url: '/admin/api/stats/categories',
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            renderCategoryChart(data);
        },
        error: function(err) {
            console.error('Error loading category stats:', err);
        }
    });
}


/**
 * Render categories bar chart (top anomalies + priorities)
 */
function renderCategoryChart(data) {
    const ctx = document.getElementById('chart_categories');
    
    // Combine and sort categories
    const allCategories = {
        ...data.mezzo_anomalies,
        ...data.tecnico_priorities
    };
    
    // Get top 8 categories
    const sorted = Object.entries(allCategories)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);
    
    const labels = sorted.map(x => x[0]);
    const counts = sorted.map(x => x[1]);
    
    // Destroy existing chart if it exists
    if (charts['categories']) {
        charts['categories'].destroy();
    }
    
    charts['categories'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Numero Ticket',
                data: counts,
                backgroundColor: [
                    '#0d6efd',
                    '#6f42c1',
                    '#e83e8c',
                    '#fd7e14',
                    '#ffc107',
                    '#28a745',
                    '#20c997',
                    '#17a2b8'
                ],
                borderRadius: 5,
                borderSkipped: false
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Ticket: ' + context.parsed.x;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}


/**
 * Load and render trend statistics
 */
function loadTrendStats() {
    const params = getDateParams();
    
    $.ajax({
        url: '/admin/api/stats/trends',
        data: params,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            renderTrendChart(data);
        },
        error: function(err) {
            console.error('Error loading trend stats:', err);
        }
    });
}


/**
 * Render trend line chart
 */
function renderTrendChart(data) {
    const ctx = document.getElementById('chart_trend');
    
    const labels = data.map(d => d.date);
    const nuovoData = data.map(d => d.nuovo);
    const inLavorazioneData = data.map(d => d.in_lavorazione);
    const risaltoData = data.map(d => d.risolto);
    
    // Destroy existing chart if it exists
    if (charts['trend']) {
        charts['trend'].destroy();
    }
    
    charts['trend'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'NUOVO',
                    data: nuovoData,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.3,
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: 'IN LAVORAZIONE',
                    data: inLavorazioneData,
                    borderColor: '#fd7e14',
                    backgroundColor: 'rgba(253, 126, 20, 0.1)',
                    tension: 0.3,
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: 'RISOLTO',
                    data: risaltoData,
                    borderColor: '#198754',
                    backgroundColor: 'rgba(25, 135, 84, 0.1)',
                    tension: 0.3,
                    borderWidth: 2,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}


/**
 * Load operator statistics
 */
function loadOperatorStats() {
    const params = getDateParams();
    
    $.ajax({
        url: '/admin/api/stats/operators',
        data: params,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            renderOperators(data);
        },
        error: function(err) {
            console.error('Error loading operator stats:', err);
            $('#operators_container').html('<p class="text-danger">Errore nel caricamento</p>');
        }
    });
}


/**
 * Render operators section
 */
function renderOperators(data) {
    const container = $('#operators_container');
    
    if (!data || data.length === 0) {
        container.html('<p class="text-muted">Nessun operatore con ticket assegnati</p>');
        return;
    }
    
    let html = '<div class="row">';
    
    data.forEach((op, index) => {
        const resolved = op.resolved_tickets || 0;
        const unresolved = op.open_tickets ?? (op.total_tickets - resolved);
        const resolvedTickets = op.recent_resolved_tickets || [];
        const statusBreakdown = op.status_breakdown || {};
        
        html += `
            <div class="col-md-6 mb-3">
                <div class="operator-card" data-operator-index="${index}" role="button" tabindex="0" aria-expanded="false">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">
                                <i class="bi bi-person-circle"></i> ${op.operator_username}
                            </h6>
                            <small class="text-muted">Total: ${op.total_tickets} ticket (${op.workload_percent}% workload)</small>
                        </div>
                        <div>
                            <span class="badge bg-primary">${op.total_tickets}</span>
                            <i class="bi bi-chevron-down" style="margin-left: 10px;"></i>
                        </div>
                    </div>
                    
                    <div class="operator-stats" id="operator-stats-${index}">
                        <div class="operator-metrics-grid">
                            <div class="stat-row">
                                <span class="stat-label">Tempo Medio Risoluzione:</span>
                                <span class="stat-value">${formatMinutes(op.avg_resolution_time_minutes)}</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Tempo Medio Risposta:</span>
                                <span class="stat-value">${formatMinutes(op.avg_response_time_minutes)}</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Ticket Risolti:</span>
                                <span class="stat-value">${resolved}</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Ticket Aperti:</span>
                                <span class="stat-value">${unresolved}</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Ticket Nuovi:</span>
                                <span class="stat-value">${statusBreakdown.NUOVO || 0}</span>
                            </div>
                            <div class="stat-row">
                                <span class="stat-label">Ticket In Lavorazione:</span>
                                <span class="stat-value">${statusBreakdown.IN_LAVORAZIONE || 0}</span>
                            </div>
                        </div>

                        <div class="resolved-tickets-section">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <strong>Ticket risolti recenti</strong>
                                <span class="badge bg-success">${resolvedTickets.length}</span>
                            </div>
                            ${renderResolvedTickets(resolvedTickets)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.html(html);
}


/**
 * Render resolved tickets list for an operator
 */
function renderResolvedTickets(tickets) {
    if (!tickets || tickets.length === 0) {
        return '<p class="text-muted mb-0">Nessun ticket risolto nel periodo selezionato.</p>';
    }

    let html = '<div class="resolved-tickets-list">';

    tickets.forEach(ticket => {
        html += `
            <div class="resolved-ticket-item">
                <div class="d-flex justify-content-between gap-3">
                    <div class="flex-grow-1">
                        <div class="d-flex flex-wrap align-items-center gap-2 mb-1">
                            <a href="/admin/ticket/${ticket.ticket_id}" target="_blank" rel="noopener noreferrer" class="resolved-ticket-link">#${ticket.ticket_id}</a>
                            <span class="badge bg-secondary">${ticket.ticket_type}</span>
                            <span class="text-muted small">${ticket.closed_at}</span>
                        </div>
                        <div class="resolved-ticket-title">${ticket.title}</div>
                        <div class="resolved-ticket-meta text-muted small">${ticket.requester_name} · ${ticket.description}</div>
                    </div>
                    <div class="text-end">
                        <div class="resolved-ticket-hours">${ticket.resolution_time_hours}h</div>
                        <div class="text-muted small">${ticket.resolution_time_minutes} min</div>
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    return html;
}


/**
 * Toggle operator details
 */
function toggleOperator(index) {
    const statsDiv = $(`#operator-stats-${index}`);
    const card = statsDiv.closest('.operator-card');
    const isExpanded = !statsDiv.hasClass('show');
    
    statsDiv.toggleClass('show');
    card.toggleClass('expanded');
    card.attr('aria-expanded', isExpanded ? 'true' : 'false');
}


/**
 * Load SLA violations
 */
function loadSLAViolations() {
    $.ajax({
        url: '/admin/api/stats/sla',
        data: { threshold: SLA_THRESHOLD_HOURS },
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            renderSLAViolations(data);
        },
        error: function(err) {
            console.error('Error loading SLA violations:', err);
            $('#sla_container').html('<p class="text-danger">Errore nel caricamento</p>');
        }
    });
}


/**
 * Render SLA violations table
 */
function renderSLAViolations(data) {
    const container = $('#sla_container');
    
    if (!data || data.length === 0) {
        container.html('<p class="text-success"><i class="bi bi-check-circle"></i> Nessuna violazione SLA!</p>');
        return;
    }
    
    let html = `
        <table class="table table-hover sla-table">
            <thead>
                <tr>
                    <th>Ticket ID</th>
                    <th>Tipo</th>
                    <th>Richiedente</th>
                    <th>Descrizione</th>
                    <th>Creato</th>
                    <th>Chiuso</th>
                    <th>Ore Impiegate</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    data.forEach(violation => {
        const rowClass = violation.resolution_time_hours > 24 ? 'sla-violation' : '';
        html += `
            <tr class="${rowClass}">
                <td>
                    <a href="/admin/ticket/${violation.ticket_id}" target="_blank" class="text-decoration-none">
                        #${violation.ticket_id}
                    </a>
                </td>
                <td>
                    <span class="badge bg-secondary">${violation.ticket_type}</span>
                </td>
                <td><small>${violation.requester_name}</small></td>
                <td><small>${violation.description}</small></td>
                <td><small>${violation.created_at}</small></td>
                <td><small>${violation.closed_at}</small></td>
                <td>
                    <strong class="text-danger">${violation.resolution_time_hours}h</strong>
                </td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    container.html(html);
}


/**
 * Reset filter to default (last 30 days)
 */
function resetFilter() {
    const today = new Date();
    const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));
    
    $('#end_date').val(formatDateForInput(today));
    $('#start_date').val(formatDateForInput(thirtyDaysAgo));
    
    loadAllStats();
}


/**
 * Show error message
 */
function showError(message) {
    alert(message);
}
