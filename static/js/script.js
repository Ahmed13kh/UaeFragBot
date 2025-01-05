document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("chat-form");
    const chatHistory = document.querySelector(".chat-history");
    const userInput = document.getElementById("user_input");

    // Suggestions list data
    const suggestions = [
        "What are the most popular perfume brands?",
        "Can you tell me about perfumeX?",
        "What are the top-rated perfumes from designerX?",
        "I need a long-lasting summer perfume with fresh notes for men.",
        "Give me a woody perfume with strong sillage for women.",
        "Can you explain what sillage means in perfumes?"
    ];

    // Create suggestions container
    const suggestionsContainer = document.createElement("ul");
    suggestionsContainer.classList.add("suggestions-list");

    // Populate suggestions
    suggestions.forEach((suggestion) => {
        const listItem = document.createElement("li");
        listItem.textContent = suggestion;

       // Populate input field and hide suggestions on click
        listItem.addEventListener("mousedown", (e) => {
            e.preventDefault(); // Prevent blur from firing
            userInput.value = suggestion;
            suggestionsContainer.style.display = "none"; // Hide the list after selection
        });
        suggestionsContainer.appendChild(listItem);
    });

    // Add the suggestions container to the DOM
    document.body.appendChild(suggestionsContainer);

    // Adjust suggestions position dynamically
    const adjustPosition = () => {
        const rect = userInput.getBoundingClientRect();
        suggestionsContainer.style.position = "absolute";
        suggestionsContainer.style.top = `${rect.bottom + window.scrollY}px`; // Below the input
        suggestionsContainer.style.left = `${rect.left + window.scrollX}px`; // Align with the input
        suggestionsContainer.style.width = `${rect.width}px`; // Match input width
    };

    // Show suggestions on click
    userInput.addEventListener("click", () => {
        adjustPosition(); // Adjust position dynamically
        suggestionsContainer.style.display = "block"; // Show suggestions
    });

    // Hide suggestions on blur (delay for click)
    userInput.addEventListener("blur", () => {
        setTimeout(() => {
            suggestionsContainer.style.display = "none";
        }, 100);
    });

    // Recalculate position on window resize or scroll
    window.addEventListener("resize", adjustPosition);
    window.addEventListener("scroll", adjustPosition);

    // Extract JSON data from script tags
    const perfumeDataElement = document.getElementById("perfume-data");
    const fragranceNotesElement = document.getElementById("fragrance-notes");
    const perfumeData = JSON.parse(perfumeDataElement.textContent);
    const fragranceNotes = JSON.parse(fragranceNotesElement.textContent);

    // Populate perfume names dropdown
    const perfumeNamesDropdown = document.getElementById("perfume-names");
    perfumeData.forEach(perfume => {
        const option = document.createElement("option");
        option.value = perfume.name;
        option.textContent = perfume.name.charAt(0).toUpperCase() + perfume.name.slice(1);
        perfumeNamesDropdown.appendChild(option);
    });

    // Populate designers and notes
    const designers = [...new Set(perfumeData.map(perfume => perfume.designer.charAt(0).toUpperCase() + perfume.designer.slice(1)))];
    document.getElementById("designers").textContent = designers.join(", ");

    const notes = fragranceNotes.map(note => note.charAt(0).toUpperCase() + note.slice(1)).join(", ");
    document.getElementById("notes").textContent = notes;

    // Add event listener to perfume dropdown
    perfumeNamesDropdown.addEventListener("change", function () {
        if (this.value) {
            userInput.value = `Give me details about ${this.value}`;
        }
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        if (!userInput.value.trim()) {
            alert("Please type a question!");
            return;
        }

        const formData = new FormData(form);

        // Display user's message immediately
        const userDiv = document.createElement("div");
        userDiv.className = "chat-box";
        userDiv.innerHTML = `<p><strong>You:</strong> ${userInput.value}</p>`;
        chatHistory.appendChild(userDiv);

        // Clear the input field
        userInput.value = "";

        // Reset dropdown to default
        perfumeNamesDropdown.value = "";

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

        // Simulate bot typing delay
        setTimeout(() => {
            fetch("/chat", {
                method: "POST",
                body: formData,
            })
                .then(response => response.json())
                .then(data => {
                    // Remove typing indicator
                    chatHistory.removeChild(typingDiv);

                    // Add bot's response
                    const botDiv = document.createElement("div");
                    botDiv.className = "chat-box";

                    if (data.structured) {
                        if (Array.isArray(data.structured)) {
                            botDiv.innerHTML = `<p><strong>FragBot:</strong> Here are some suggestions:</p>`;
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
                                    <h4>Reviews</h4>
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
                })
                .catch(error => {
                    console.error("Error:", error);
                    chatHistory.removeChild(typingDiv);

                    const errorDiv = document.createElement("div");
                    errorDiv.className = "chat-box";
                    errorDiv.innerHTML = `<p><strong>FragBot:</strong> An error occurred. Please try again later.</p>`;
                    chatHistory.appendChild(errorDiv);
                });
        }, 1500); // Simulate typing delay of 1.5 seconds
    });
});