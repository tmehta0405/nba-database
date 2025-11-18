document.addEventListener('DOMContentLoaded', function() {
    const typewriterElement = document.getElementById('typewriter-search');
    const text = typewriterElement.textContent.trim(); 
    typewriterElement.textContent = ''; 
    let index = 0;

    function typeWriter() {
        if (index < text.length) {
            typewriterElement.innerHTML += text.charAt(index);
            typewriterElement.classList.add('typewriter-search');
            index++;
            setTimeout(typeWriter, 100);
        }
    }
    setTimeout(typeWriter, 300);
    const selectedSeasons = new Set();
    let currentTable = null;
    const tables = document.querySelectorAll('.content-table');
    
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
        clearAllSelections();
    });

    function clearAllSelections() {
        selectedSeasons.clear();
        tables.forEach(table => {
            const rows = table.querySelectorAll('tbody .season-stat');
            rows.forEach(row => row.classList.remove('selected-season'));
        });
        summaryDiv.classList.remove('active');
        currentTable = null;
    }

    function isAwardsTable(table) {
        const headers = table.querySelectorAll('thead th');
        return headers.length === 2 && 
               headers[0].textContent.trim() === 'Season' && 
               headers[1].textContent.trim() === 'Awards';
    }

    tables.forEach(table => {
        const seasonRows = table.querySelectorAll('tbody .season-stat');
        
        seasonRows.forEach(row => {
            row.addEventListener('click', function() {
                if (currentTable && currentTable !== table) {
                    clearAllSelections();
                }
                
                currentTable = table;
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
    });

    function updateSummary() {
        if (isAwardsTable(currentTable)) {
            updateAwardsSummary();
        } else {
            updateStatsSummary();
        }
    }

    function updateAwardsSummary() {
        const selectedRows = currentTable.querySelectorAll('tbody .season-stat.selected-season');
        const awardCounts = {};
        
        selectedRows.forEach(row => {
            const awardsText = row.cells[1].textContent.trim();
            const awards = awardsText.split(',').map(a => a.trim());
            
            awards.forEach(award => {
                if (award) {
                    awardCounts[award] = (awardCounts[award] || 0) + 1;
                }
            });
        });

        let html = `<div class="summary-stat"><span>Seasons Selected:</span><span>${selectedSeasons.size}</span></div>`;
        
        const sortedAwards = Object.keys(awardCounts).sort();
        
        sortedAwards.forEach(award => {
            html += `<div class="summary-stat"><span>${award}:</span><span>${awardCounts[award]}</span></div>`;
        });

        summaryContent.innerHTML = html;
    }
    function updateStatsSummary() {
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

        const selectedRows = currentTable.querySelectorAll('tbody .season-stat.selected-season');
        
        selectedRows.forEach(row => {
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
        });

        const fgPct = stats['FGA'] > 0 ? (stats['FGM'] / stats['FGA'] * 100).toFixed(1) : '0.0';
        const fg3Pct = stats['3PA'] > 0 ? (stats['3PM'] / stats['3PA'] * 100).toFixed(1) : '0.0';

        summaryContent.innerHTML = `
            <div class="summary-stat"><span>Seasons Selected:</span><span>${selectedSeasons.size}</span></div>
            <div class="summary-stat"><span>Total Games:</span><span>${stats['Games'].toFixed(0)}</span></div>
            <div class="summary-stat"><span>Total Points:</span><span>${stats['Points'].toFixed(0)}</span></div>
            <div class="summary-stat"><span>Total Rebounds:</span><span>${stats['Rebounds'].toFixed(0)}</span></div>
            <div class="summary-stat"><span>Total Assists:</span><span>${stats['Assists'].toFixed(0)}</span></div>
            <div class="summary-stat"><span>FG%:</span><span>${fgPct}%</span></div>
            <div class="summary-stat"><span>3P%:</span><span>${fg3Pct}%</span></div>
            <div class="summary-stat"><span>Total Steals:</span><span>${stats['Steals'].toFixed(0)}</span></div>
            <div class="summary-stat"><span>Total Blocks:</span><span>${stats['Blocks'].toFixed(0)}</span></div>
        `;
    }
});