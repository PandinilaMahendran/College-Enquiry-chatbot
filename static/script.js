document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const micBtn = document.getElementById("mic-btn");
    const chatWindow = document.getElementById("chat-window");
    const typingIndicator = document.getElementById("typing-indicator");
    const btnLang = document.getElementById("btn-lang");
    const btnEligibility = document.getElementById("btn-eligibility");
    const btnDocs = document.getElementById("btn-docs");
    const suggestionChipsContainer = document.getElementById("suggestion-chips-container");
    const loadingOverlay = document.getElementById("loading-overlay");

    let currentLang = 'en-US'; // Default language

    function addMessage(message, sender, audioUrl = null) {
        const messageContainer = document.createElement("div");
        messageContainer.className = "flex items-start gap-3";

        const messageDiv = document.createElement("div");
        messageDiv.className = "p-3 rounded-lg max-w-xs shadow break-words flex items-center gap-2";
        messageDiv.textContent = message;

        if (sender === 'user') {
            messageContainer.classList.add("justify-end");
            messageDiv.classList.add("bg-slate-700", "text-white", "rounded-tr-none");
        } else {
            messageDiv.classList.add("bg-violet-600", "text-white", "rounded-tl-none");

            if (audioUrl) {
                const speakerBtn = document.createElement("button");
                speakerBtn.innerHTML = "🔊";
                speakerBtn.className = "ml-2 text-white hover:text-yellow-300";
                speakerBtn.onclick = () => {
                    const audio = new Audio(audioUrl);
                    audio.play();
                };
                messageDiv.appendChild(speakerBtn);
            }
        }

        messageContainer.appendChild(messageDiv);
        chatWindow.appendChild(messageContainer);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function addImageMessage(url) {
        const messageContainer = document.createElement("div");
        messageContainer.className = "flex items-start gap-3";
        const imgElement = document.createElement("img");
        imgElement.src = url;
        imgElement.className = "p-1 bg-violet-600 rounded-lg max-w-xs shadow";
        messageContainer.appendChild(imgElement);
        chatWindow.appendChild(messageContainer);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function clearSuggestionChips() {
        suggestionChipsContainer.innerHTML = '';
    }

    function displaySuggestionChips(suggestions) {
        clearSuggestionChips();
        suggestions.forEach(text => {
            const chip = document.createElement("button");
            chip.className = "suggestion-chip";
            chip.textContent = text;
            chip.onclick = () => {
                userInput.value = text;
                sendMessage();
            };
            suggestionChipsContainer.appendChild(chip);
        });
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === "") return;

        addMessage(message, "user");
        userInput.value = "";
        clearSuggestionChips();

        typingIndicator.classList.remove("hidden");
        loadingOverlay.classList.remove("hidden");

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, lang: currentLang })
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();

            typingIndicator.classList.add("hidden");
            loadingOverlay.classList.add("hidden");

            addMessage(data.response, "bot", data.audio_url || null);

            if (data.image_url) addImageMessage(data.image_url);
            if (data.suggestions?.length) displaySuggestionChips(data.suggestions);

        } catch (error) {
            typingIndicator.classList.add("hidden");
            loadingOverlay.classList.add("hidden");
            console.error("Error fetching chat response:", error);
            addMessage("ക്ഷമിക്കണം, കണക്ഷനിൽ പ്രശ്നമുണ്ട്. ദയവായി വീണ്ടും ശ്രമിക്കുക.", "bot");
        }
    }

    // Speech recognition
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = currentLang;
    recognition.interimResults = false;

    micBtn.addEventListener('click', () => {
        micBtn.classList.add("text-red-500");
        recognition.lang = currentLang; // Use selected language
        try {
            recognition.start();
        } catch (e) {
            console.error("Voice recognition could not be started: ", e);
            alert("Voice recognition is not available or is already active.");
            micBtn.classList.remove("text-red-500");
        }
    });

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        sendMessage();
    };

    recognition.onend = () => micBtn.classList.remove("text-red-500");

    // Welcome message
    async function getWelcomeMessage() {
        typingIndicator.classList.remove("hidden");
        loadingOverlay.classList.remove("hidden");

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: 'Initial greeting', lang: currentLang })
            });
            const data = await response.json();

            typingIndicator.classList.add("hidden");
            loadingOverlay.classList.add("hidden");

            addMessage(data.response, "bot", data.audio_url || null);
            if (data.suggestions?.length) displaySuggestionChips(data.suggestions);

        } catch (error) {
            typingIndicator.classList.add("hidden");
            loadingOverlay.classList.add("hidden");
            addMessage("സ്വാഗതം! ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കണം?", "bot");
        }
    }

    // Event listeners
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
    btnEligibility.addEventListener('click', () => {
        userInput.value = currentLang === 'ml-IN' ? "യോഗ്യത പരിശോധിക്കുക" : "Check eligibility";
        sendMessage();
    });
    btnDocs.addEventListener('click', () => {
        userInput.value = currentLang === 'ml-IN' ? "ബ്രോഷർ ഡൗൺലോഡ് ചെയ്യുക" : "Download brochure";
        sendMessage();
    });

    // Language change button
    btnLang.addEventListener('click', () => {
        const choice = prompt("Choose language: 1-English, 2-Tamil, 3-Malayalam", "1");
        if (choice === "1") currentLang = 'en-US';
        else if (choice === "2") currentLang = 'ta-IN';
        else if (choice === "3") currentLang = 'ml-IN';
        alert(`Language set to: ${currentLang}`);
    });

    chatWindow.innerHTML = '';
    getWelcomeMessage();
});
