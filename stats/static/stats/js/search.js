document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const suggestionsDiv = document.getElementById('suggestions');
    let debounceTimer;
    let currentFocus = -1;
    let currentFetchController = null;

    if (!searchInput || !suggestionsDiv) {
        console.error('Search elements not found');
        return;
    }

    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const query = this.value.trim();

        if (query.length < 2) {
            hideSuggestions();
            return;
        }

        debounceTimer = setTimeout(() => {
            fetchSuggestions(query);
        }, 250);
    });

    function fetchSuggestions(query) {
        if (currentFetchController) currentFetchController.abort();

        currentFetchController = new AbortController();
        const { signal } = currentFetchController;

        fetch(`/search/suggestions/?q=${encodeURIComponent(query)}`, { signal })
            .then(response => response.json())
            .then(data => {
                if (!signal.aborted) displaySuggestions(data.suggestions);
            })
            .catch(error => {
                if (error.name !== 'AbortError') {
                    console.error('Error:', error);
                }
                hideSuggestions();
            });
    }

    function displaySuggestions(suggestions) {
        if (!suggestions || suggestions.length === 0) {
            hideSuggestions();
            return;
        }

        suggestionsDiv.innerHTML = suggestions.map(item => {
            const [name, career] = item.text.split(" — ");
            return `
                <div class="suggestion-item" data-value="${name}">
                    <span class="player-name">${name}</span>
                    <span class="player-career">${career || ""}</span>
                </div>
            `;
        }).join('');

        showSuggestions();
        currentFocus = -1;

        document.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const playerName = this.getAttribute('data-value');
                searchInput.value = playerName;
                hideSuggestions();
                window.location.href = `/player/${encodeURIComponent(playerName)}/`;
            });
        });
    }

    function showSuggestions() {
        suggestionsDiv.classList.remove('show');
        void suggestionsDiv.offsetWidth; 
        requestAnimationFrame(() => {
            suggestionsDiv.classList.add('show');
        });
    }

    function hideSuggestions() {
        suggestionsDiv.classList.remove('show');
    }

    searchInput.addEventListener('keydown', function(e) {
        const items = suggestionsDiv.querySelectorAll('.suggestion-item');

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            currentFocus++;
            if (currentFocus >= items.length) currentFocus = 0;
            setActive(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            currentFocus--;
            if (currentFocus < 0) currentFocus = items.length - 1;
            setActive(items);
        } else if (e.key === 'Enter') {
            if (currentFocus > -1 && items[currentFocus]) {
                e.preventDefault();
                items[currentFocus].click();
            }
        } else if (e.key === 'Escape') {
            hideSuggestions();
        }
    });

    function setActive(items) {
        items.forEach(item => item.classList.remove('active'));
        if (items[currentFocus]) {
            items[currentFocus].classList.add('active');
            items[currentFocus].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-box')) {
            hideSuggestions();
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("searchInput");
  const suggestionsBox = document.getElementById("suggestions");

  input.addEventListener("input", () => {
    const query = input.value.trim();
    if (query.length < 2) {
      suggestionsBox.innerHTML = "";
      return;
    }

    fetch(`/search/suggestions/?q=${encodeURIComponent(query)}`)
      .then((res) => res.json())
      .then((data) => {
        suggestionsBox.innerHTML = "";

        data.suggestions.forEach((item) => {
          const [name, years] = item.text.split(" — ");
          const suggestion = document.createElement("div");
          suggestion.classList.add("suggestion-item");

          suggestion.innerHTML = `
            <span class="player-name">${name}</span>
            <span class="player-years">${years || ""}</span>
          `;

          suggestion.addEventListener("click", () => {
            input.value = name;
            suggestionsBox.innerHTML = "";
          });

          suggestionsBox.appendChild(suggestion);
        });
      })
      .catch(() => {
        suggestionsBox.innerHTML = "";
      });
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".search-input-wrapper")) {
      suggestionsBox.innerHTML = "";
    }
  });
});

function revealPlayer() {
    fetch('/api/birthday-player')
        .then(response => response.json())
        .then(data => {
            const revealDiv = document.getElementById('player-reveal');
            const playersList = revealDiv.querySelector('.players-list');
            
            if (data.success && data.players && data.players.length > 0) {
                playersList.innerHTML = data.players.map(player => `
                    <a href="/player/${encodeURIComponent(player.player_name)}/" class="player-item">
                        <strong>${player.player_name}</strong>
                        <span class="bday">${player.birthday.substring(0, 4)}</span>
                    </a>
                `).join('');
                
                revealDiv.style.display = 'block';
                requestAnimationFrame(() => {
                    revealDiv.classList.add('show');
                    revealDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });          
                });
            } else {
                playersList.innerHTML = `<div class="player-item"><strong>${data.message || 'No birthdays today'}</strong></div>`;
                revealDiv.style.display = 'block';
                requestAnimationFrame(() => {
                    revealDiv.classList.add('show');
                });
            }
        });
}