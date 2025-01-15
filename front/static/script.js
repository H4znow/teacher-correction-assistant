document.addEventListener("DOMContentLoaded", () => {
    const imageSection = document.getElementById("image-section");
    const preprocessSection = document.getElementById("preprocess-section");
    const textSection = document.getElementById("text-section");
    const syntaxSection = document.getElementById("syntax-section");
    const grammarSection = document.getElementById("grammar-section");

    // Image quality buttons
    document.getElementById("quality-yes").addEventListener("click", () => {
        fetch("/check-image-quality", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ decision: "yes" })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "preprocessed") {
                document.getElementById("preprocessed-image").src = data.image;
                const linesList = document.getElementById("detected-lines");
                linesList.innerHTML = "";
                data.lines.forEach(line => {
                    const li = document.createElement("li");
                    li.textContent = line;
                    linesList.appendChild(li);
                });
                imageSection.style.display = "none";
                preprocessSection.style.display = "block";
            }
        });
    });

    document.getElementById("quality-no").addEventListener("click", () => {
        alert("Please retake the image!");
    });

    // Preprocessing buttons
    document.getElementById("preprocess-yes").addEventListener("click", () => {
        const lines = Array.from(document.getElementById("detected-lines").children).map(li => li.textContent);
        fetch("/check-preprocessing", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ decision: "yes", lines: lines })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "text_extracted") {
                document.getElementById("extracted-text").value = data.text;
                preprocessSection.style.display = "none";
                textSection.style.display = "block";
            }
        });
    });

    document.getElementById("preprocess-no").addEventListener("click", () => {
        alert("Please retake the image!");
    });

    // Syntax check button
    document.getElementById("syntax-check").addEventListener("click", () => {
        const text = document.getElementById("extracted-text").value;
        fetch("/check-syntax", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("syntax-original").textContent = data.original;
            document.getElementById("syntax-fixed").textContent = data.fixed;
            textSection.style.display = "none";
            syntaxSection.style.display = "block";
        });
    });

    // Grammar check button
    document.getElementById("grammar-check").addEventListener("click", () => {
        const text = document.getElementById("syntax-fixed").textContent;
        fetch("/check-grammar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("grammar-original").textContent = data.original;
            document.getElementById("grammar-fixed").textContent = data.fixed;
            syntaxSection.style.display = "none";
            grammarSection.style.display = "block";
        });
    });
});
