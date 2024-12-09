// Typing effect for chatbot header and description
window.onload = function() {
    typeText("chatbot-header", "UAEFragBot", 60); // Typing effect for header
    typeText("chatbot-description", "Ask me anything about UAE perfumes!", 60); // Typing effect for description
};

// Function to simulate typing effect
function typeText(elementId, text, speed) {
    let i = 0;
    let element = document.getElementById(elementId);
    element.innerHTML = ""; // Clear text before starting typing effect
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}

// Show loading indicator and dots animation
document.querySelector("form").addEventListener("submit", function (event) {
    const userInput = document.getElementById("user_input");
    const loadingIndicator = document.getElementById("loading-indicator");

    // Clear the input field immediately


    // Show loading indicator
    loadingIndicator.style.display = "block";

    // Simulate dot animation
    let dots = "";
    const dotsElement = document.getElementById("dots");
    const interval = setInterval(() => {
        dots = dots.length < 3 ? dots + "." : "";
        dotsElement.textContent = dots;
    }, 500);

    // Allow the loading indicator to stay visible until the server processes the response
    setTimeout(() => {
        userInput.value = ""; // Clear the input field after submission
    }, 50); // Short delay to ensure the message is sent
});

