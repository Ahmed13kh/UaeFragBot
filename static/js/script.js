window.onload = function () {
    typeText("chatbot-header", "UAEFragBot", 60);
    typeText("chatbot-description", "Ask me anything about UAE perfumes!", 60);
};

function typeText(elementId, text, speed) {
    let i = 0;
    let element = document.getElementById(elementId);
    element.innerHTML = "";

    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }

    type();
}

document.querySelector("form").addEventListener("submit", function () {
    const loadingIndicator = document.getElementById("loading-indicator");
    loadingIndicator.style.display = "block";

    let dots = "";
    const dotsElement = document.getElementById("dots");
    const interval = setInterval(() => {
        dots = dots.length < 3 ? dots + "." : "";
        dotsElement.textContent = dots;
    }, 500);

    setTimeout(() => {
        loadingIndicator.style.display = "none";
    }, 5000);
});

document.addEventListener("DOMContentLoaded", () => {
    const scrollDownBtn = document.getElementById("scroll-down-btn");
    const chatHistory = document.querySelector(".chat-history");

    // Scroll to the bottom of chat history
    scrollDownBtn.addEventListener("click", () => {
        chatHistory.scrollTo({
            top: chatHistory.scrollHeight,
            behavior: "smooth",
        });
    });

    // Show or hide the scroll-down button based on scroll position
    chatHistory.addEventListener("scroll", () => {
        if (chatHistory.scrollTop < chatHistory.scrollHeight - chatHistory.clientHeight - 50) {
            scrollDownBtn.style.display = "block";
        } else {
            scrollDownBtn.style.display = "none";
        }
    });

    // Initially hide the button
    scrollDownBtn.style.display = "none";
});




