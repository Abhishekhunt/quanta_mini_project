document.getElementById("analysisForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    fetch("/analyze", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                document.getElementById("result").innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
            } else {
                document.getElementById("result").innerHTML = `
                    <p>${data.message}</p>
                    <a href="${data.file}" download>Download Results</a>
                `;
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            document.getElementById("result").innerHTML = `<p style="color: red;">An error occurred. Please try again.</p>`;
        });
});
