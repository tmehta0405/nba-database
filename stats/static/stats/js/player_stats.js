document.addEventListener('DOMContentLoaded', function() {
    const selectedSeasons = new Set();
    const seasonRows = document.querySelectorAll('.content-table tbody .season-stat');
    
    let summaryDiv = document.querySelector('.stats-summary');
    if (!summaryDiv) {
        summaryDiv = document.createElement('div');
        summaryDiv.className = 'stats-summary';
        summaryDiv.innerHTML = `
            <span class="summary-close">&times;</span>
            <h3>Selected Seasons Summary</h3>
            <div class="summary-content"></div>
        `;
        document.body.appendChild(summaryDiv);
    }

    const summaryContent = summaryDiv.querySelector('.summary-content');
    const closeBtn = summaryDiv.querySelector('.summary-close');

    closeBtn.addEventListener('click', function() {
        selectedSeasons.clear();
        seasonRows.forEach(row => row.classList.remove('selected-season'));
        summaryDiv.classList.remove('active');
    });

    seasonRows.forEach(row => {
        row.addEventListener('click', function() {
            const seasonText = this.cells[0].textContent;
            
            if (selectedSeasons.has(seasonText)) {
                selectedSeasons.delete(seasonText);
                this.classList.remove('selected-season');
            } else {
                selectedSeasons.add(seasonText);
                this.classList.add('selected-season');
            }

            if (selectedSeasons.size > 0) {
                updateSummary();
                summaryDiv.classList.add('active');
            } else {
                summaryDiv.classList.remove('active');
            }
        });
    });

    function updateSummary() {
        const stats = {
            'Games': 0,
            'Minutes': 0,
            'Points': 0,
            'Rebounds': 0,
            'Assists': 0,
            'Steals': 0,
            'Blocks': 0,
            'FGM': 0,
            'FGA': 0,
            '3PM': 0,
            '3PA': 0
        };

        seasonRows.forEach(row => {
            if (row.classList.contains('selected-season')) {
                stats['Games'] += parseFloat(row.cells[4].textContent) || 0;
                stats['Minutes'] += parseFloat(row.cells[6].textContent) || 0;
                stats['FGM'] += parseFloat(row.cells[7].textContent) || 0;
                stats['FGA'] += parseFloat(row.cells[8].textContent) || 0;
                stats['3PM'] += parseFloat(row.cells[10].textContent) || 0;
                stats['3PA'] += parseFloat(row.cells[11].textContent) || 0;
                stats['Rebounds'] += parseFloat(row.cells[18].textContent) || 0;
                stats['Assists'] += parseFloat(row.cells[19].textContent) || 0;
                stats['Steals'] += parseFloat(row.cells[20].textContent) || 0;
                stats['Blocks'] += parseFloat(row.cells[21].textContent) || 0;
                stats['Points'] += parseFloat(row.cells[24].textContent) || 0;
            }
        });

        const fgPct = stats['FGA'] > 0 ? (stats['FGM'] / stats['FGA'] * 100).toFixed(1) : '0.0';
        const fg3Pct = stats['3PA'] > 0 ? (stats['3PM'] / stats['3PA'] * 100).toFixed(1) : '0.0';

        summaryContent.innerHTML = `
            <div class="summary-stat"><span>Seasons Selected:</span>${selectedSeasons.size}</div>
            <div class="summary-stat"><span>Total Games:</span>${stats['Games'].toFixed(0)}</div>
            <div class="summary-stat"><span>Total Points:</span>${stats['Points'].toFixed(0)}</div>
            <div class="summary-stat"><span>Total Rebounds:</span>${stats['Rebounds'].toFixed(0)}</div>
            <div class="summary-stat"><span>Total Assists:</span>${stats['Assists'].toFixed(0)}</div>
            <div class="summary-stat"><span>FG%:</span>${fgPct}%</div>
            <div class="summary-stat"><span>3P%:</span>${fg3Pct}%</div>
            <div class="summary-stat"><span>Total Steals:</span>${stats['Steals'].toFixed(0)}</div>
            <div class="summary-stat"><span>Total Blocks:</span>${stats['Blocks'].toFixed(0)}</div>
        `;
    }
});