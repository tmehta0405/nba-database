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


function createFish() {
    const fish = document.createElement('i');
    fish.className = 'fas fa-fish fish';
    fish.style.top = Math.random() * 100 + '%';
    fish.style.setProperty('--wave', (Math.random() * 100 - 50) + 'px');
    const duration = Math.random() * 4 + 6;
    fish.style.animationDuration = duration + 's';
    fish.style.animationDelay = Math.random() * 2 + 's';
    fish.style.fontSize = (Math.random() * 15 + 10) + 'px';
    fish.style.color = Math.random() > 0.5 ? '#272729' : '#3f4045';
    
    if (Math.random() > 0.5) {
        fish.style.animationName = 'swim';
    } else {
        fish.style.animationName = 'swimReverse';
    }
    
    document.body.appendChild(fish);
    
    setTimeout(() => {
        fish.remove();
    }, (duration + 2) * 1000 + 2000);
}

document.addEventListener('DOMContentLoaded', function() {
    setInterval(createFish, 400);
    
    for (let i = 0; i < 10; i++) {
        setTimeout(createFish, i * 400);
    }
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
