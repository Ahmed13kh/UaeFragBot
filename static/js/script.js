document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("chat-form");
    const chatHistory = document.querySelector(".chat-history");
    const userInput = document.getElementById("user_input");
    const container = document.querySelector(".container");
    const perfumeNamesDropdown = document.getElementById("perfume-names");

    // Suggestions list data
    const suggestions = [
        "What are the most popular perfume brands?",
        "Can you tell me about perfumeX?",
        "What are the top-rated perfumes from designerX?",
        "I need a long-lasting summer perfume with Lemon notes for men.",
        "Give me a woody perfume with strong sillage for women.",
        "Can you explain what sillage means in perfumes?"
    ];

    // wrapper for suggestions
    const suggestionsWrapper = document.createElement("div");
    suggestionsWrapper.classList.add("suggestions-wrapper");

    // Populate suggestions
    suggestions.forEach((suggestion) => {
        const suggestionField = document.createElement("div");
        suggestionField.classList.add("suggestion-field");
        suggestionField.textContent = suggestion;
        suggestionField.addEventListener("click", () => {
            userInput.value = suggestion;
        });
        suggestionsWrapper.appendChild(suggestionField);
    });
    container.appendChild(suggestionsWrapper);

    // Extract JSON data from script tags
    const perfumeDataElement = document.getElementById("perfume-data");
    const fragranceNotesElement = document.getElementById("fragrance-notes");
    const perfumeData = JSON.parse(perfumeDataElement.textContent);
    const fragranceNotes = JSON.parse(fragranceNotesElement.textContent);

    // Sort perfumes alphabetically
    perfumeData.sort((a, b) => a.name.localeCompare(b.name));

    // Function to populate the dropdown
    const populateDropdown = (filteredPerfumes) => {
        perfumeNamesDropdown.innerHTML = "";
        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = "--Select a perfume--";
        defaultOption.disabled = true;
        defaultOption.selected = true;
        perfumeNamesDropdown.appendChild(defaultOption);
        filteredPerfumes.forEach(perfume => {
            const option = document.createElement("option");
            option.value = perfume.name;
            option.textContent = perfume.name.charAt(0).toUpperCase() + perfume.name.slice(1);
            perfumeNamesDropdown.appendChild(option);
        });
    };
    populateDropdown(perfumeData);

    // Filter dropdown based on input
    userInput.addEventListener("input", () => {
        const inputValue = userInput.value.toLowerCase();
        const filteredPerfumes = inputValue
            ? perfumeData.filter(perfume => perfume.name.toLowerCase().includes(inputValue))
            : perfumeData;
        populateDropdown(filteredPerfumes);
    });

    // Handle dropdown selection
    perfumeNamesDropdown.addEventListener("change", function () {
        if (this.value) {
            userInput.value = `Give me details about ${this.value}`;
        }
    });

    // Populate designers and notes
    const designers = [...new Set(perfumeData.map(perfume => perfume.designer.charAt(0).toUpperCase() + perfume.designer.slice(1)))];
    document.getElementById("designers").textContent = designers.join(", ");
    const notes = fragranceNotes.map(note => note.charAt(0).toUpperCase() + note.slice(1)).join(", ");
    document.getElementById("notes").textContent = notes;
    form.addEventListener("submit", function (event) {
        event.preventDefault();

        if (!userInput.value.trim()) {
            alert("Please type a question!");
            return;
        }
        const formData = new FormData(form);

        // Display user's message
        const userDiv = document.createElement("div");
        userDiv.className = "chat-box";
        userDiv.innerHTML = `<p><strong>You:</strong> ${userInput.value}</p>`;
        chatHistory.appendChild(userDiv);
        userInput.value = "";

        // Add typing indicator
        const typingDiv = document.createElement("div");
        typingDiv.className = "chat-box typing-indicator";
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>`;
        chatHistory.appendChild(typingDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;

        fetch("/chat", {
            method: "POST",
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                const processResponse = () => {
                    chatHistory.removeChild(typingDiv);
                    populateDropdown(perfumeData);
                    const botDiv = document.createElement("div");
                    botDiv.className = "chat-box";

                    if (data.structured) {
                        if (Array.isArray(data.structured)) {
                            botDiv.innerHTML = `<p><strong>FragBot:</strong> Here are some recommendations:</p>`;
                            data.structured.forEach(perfume => {
                                botDiv.innerHTML += `
                                    <div class="perfume-card">
                                        <img src="${perfume.image}" alt="${perfume.name}" class="perfume-image" style="width: 150px; height: auto;">
                                        <h3>${perfume.name}</h3>
                                        <p><strong>Designer:</strong> ${perfume.designer}</p>
                                        <p><strong>Gender:</strong> ${perfume.gender}</p>
                                        <p><strong>Top Notes:</strong> ${perfume.top_notes}</p>
                                        <p><strong>Mid Notes:</strong> ${perfume.mid_notes}</p>
                                        <p><strong>Base Notes:</strong> ${perfume.base_notes}</p>
                                        <p><strong>Description:</strong> ${perfume.description}</p>
                                        <p><strong>Season:</strong> ${perfume.season}</p>
                                        <h4 style="font-size: larger;">Reviews</h4>
                                        <p><strong>Longevity:</strong> ${perfume.longevity}</p>
                                        <p><strong>Sillage:</strong> ${perfume.sillage}</p>
                                        <p><strong>Rating:</strong> ${perfume.rating}</p>
                                        <p><strong>Price Value:</strong> ${perfume.pricevalue}</p>
                                        <a href="${perfume.link}" target="_blank">View More</a>
                                    </div>`;
                            });
                        } else {
                            botDiv.innerHTML = `
                                <div class="perfume-card">
                                    <img src="${data.structured.image}" alt="${data.structured.name}" class="perfume-image" style="width: 150px; height: auto;">
                                    <h3>${data.structured.name}</h3>
                                    <p><strong>Designer:</strong> ${data.structured.designer}</p>
                                    <p><strong>Gender:</strong> ${data.structured.gender}</p>
                                    <p><strong>Top Notes:</strong> ${data.structured.top_notes}</p>
                                    <p><strong>Mid Notes:</strong> ${data.structured.mid_notes}</p>
                                    <p><strong>Base Notes:</strong> ${data.structured.base_notes}</p>
                                    <p><strong>Description:</strong> ${data.structured.description}</p>
                                    <p><strong>Season:</strong> ${data.structured.season}</p>
                                    <h4 style="font-size: larger;">Reviews</h4>
                                    <p><strong>Longevity:</strong> ${data.structured.longevity}</p>
                                    <p><strong>Sillage:</strong> ${data.structured.sillage}</p>
                                    <p><strong>Rating:</strong> ${data.structured.rating}</p>
                                    <p><strong>Price Value:</strong> ${data.structured.pricevalue}</p>
                                    <a href="${data.structured.link}" target="_blank">View More</a>
                                </div>`;
                        }
                    } else if (data.error) {
                        botDiv.innerHTML = `<p><strong>FragBot:</strong> ${data.error}</p>`;
                    } else {
                        botDiv.innerHTML = `<p><strong>FragBot:</strong> ${data.response}</p>`;
                    }
                    chatHistory.appendChild(botDiv);
                    chatHistory.scrollTop = chatHistory.scrollHeight;
                };
                if (data.structured) {
                    setTimeout(processResponse, 1500);
                } else {
                    processResponse();
                }
            })
            .catch(error => {
                console.error("Error:", error);
                chatHistory.removeChild(typingDiv);
                const errorDiv = document.createElement("div");
                errorDiv.className = "chat-box";
                errorDiv.innerHTML = `<p><strong>FragBot:</strong> An error occurred. Please try again later.</p>`;
                chatHistory.appendChild(errorDiv);
            });
    });
});