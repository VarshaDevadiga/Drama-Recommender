document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
        document.querySelector(".intro").classList.add("fade-out"); // Smooth fade-out
        setTimeout(() => {
            document.querySelector(".intro").style.display = "none";
            document.querySelector(".container").classList.remove("hidden");
        }, 1000);
    }, 3000);
});

// Handle Search Button Click
document.getElementById("searchBtn").addEventListener("click", function () {
    const query = document.getElementById("searchInput").value.trim();
    if (!query) {
        alert("Please enter a search term!");
        return;
    }

   // fetch(`http://127.0.0.1:5000/recommend?title=${encodeURIComponent(query)}`)
      fetch(`/recommend?title=${encodeURIComponent(query)}`)

        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = "";

            if (data.error) {
                resultsDiv.innerHTML = `<p>${data.error}</p>`;
                return;
            }

            data.recommendations.forEach(drama => {
                const card = document.createElement("div");
                card.classList.add("drama-card");

                let imageUrl = drama.image_url ? drama.image_url : "default-drama.jpg"; // Default image if missing

                card.innerHTML = `
                    <img src="${imageUrl}" alt="${drama.title}">
                    <h3>${drama.title}</h3>
                    <p>⭐ Rating: ${drama.rating}</p>
                `;

                resultsDiv.appendChild(card);
            });
        })
        .catch(error => {
            console.error("Error fetching recommendations:", error);
            document.getElementById("results").innerHTML = "<p>Something went wrong!</p>";
        });
});
