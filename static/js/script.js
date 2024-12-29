document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("chat-form");
    const chatHistory = document.querySelector(".chat-history");

    form.addEventListener("submit", function(event) {
        event.preventDefault();
        const userInput = document.getElementById("user_input");
        if (!userInput.value.trim()) {
            alert("Please type a question!");
            return;
        }

        const formData = new FormData(form);

        fetch("/chat", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            const userDiv = document.createElement("div");
            userDiv.className = "chat-box";
            userDiv.innerHTML = `<p><strong>You:</strong> ${userInput.value}</p>`;
            chatHistory.appendChild(userDiv);

            const botDiv = document.createElement("div");
            botDiv.className = "chat-box";
            if (data.structured) {
                if (Array.isArray(data.structured)) {
                    botDiv.innerHTML = `<p><strong>FragBot:</strong> Here are some suggestions:</p>`;
                    data.structured.forEach(perfume => {
                        botDiv.innerHTML += `
                            <div class="perfume-card">
                                <img src="${perfume.image}" alt="${perfume.name}" class="perfume-image">
                                <h3>${perfume.name}</h3>
                                <p><strong>Designer:</strong> ${perfume.designer}</p>
                                <p><strong>Top Notes:</strong> ${perfume.top_notes}</p>
                                <p><strong>Mid Notes:</strong> ${perfume.mid_notes}</p>
                                <p><strong>Base Notes:</strong> ${perfume.base_notes}</p>
                                <p><strong>Description:</strong> ${perfume.description}</p>
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
                            <img src="${data.structured.image}" alt="${data.structured.name}" class="perfume-image">
                            <h3>${data.structured.name}</h3>
                            <p><strong>Designer:</strong> ${data.structured.designer}</p>
                            <p><strong>Top Notes:</strong> ${data.structured.top_notes}</p>
                            <p><strong>Mid Notes:</strong> ${data.structured.mid_notes}</p>
                            <p><strong>Base Notes:</strong> ${data.structured.base_notes}</p>
                            <p><strong>Description:</strong> ${data.structured.description}</p>
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
            userInput.value = "";
            chatHistory.scrollTop = chatHistory.scrollHeight;
        })
        .catch(error => {
            console.error("Error:", error);
            const errorDiv = document.createElement("div");
            errorDiv.className = "chat-box";
            errorDiv.innerHTML = `<p><strong>FragBot:</strong> An error occurred. Please try again later.</p>`;
            chatHistory.appendChild(errorDiv);
        });
    });
});
