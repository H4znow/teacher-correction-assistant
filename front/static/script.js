document.addEventListener("DOMContentLoaded", () => {
    const imageSection = document.getElementById("image-section");
    const preprocessSection = document.getElementById("preprocess-section");
    const textSection = document.getElementById("text-section");
    const fullTextSection = document.getElementById("fulltext-section");
    const checkSection = document.getElementById("check-section");
    const linesImagesDiv = document.getElementById("lines-images");
    const extractionSection = document.getElementById("extraction-section");

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
                linesImagesDiv.innerHTML = "";  // Clear any previous images
                data.lines.forEach(lineImagePath => {
                    const img = document.createElement("img");
                    img.src = lineImagePath;
                    img.alt = "Detected line image";
                    linesImagesDiv.appendChild(img);
                });
                imageSection.style.display = "none";
                preprocessSection.style.display = "block";
            }
        });
    });

    document.getElementById("quality-no").addEventListener("click", () => {
        if (window.confirm("Do you want to retake the image?")) {
            // User pressed "Yes"
            location.reload(); // Reload page or update the UI as necessary
        }
    });

    document.getElementById("try-again").addEventListener("click", () => {
        if (window.confirm("Do you want to retake the image?")) {
            // User pressed "Yes"
            location.reload(); // Reload page or update the UI as necessary
        }
    });

    // Preprocessing buttons
    document.getElementById("preprocess-yes").addEventListener("click", () => {
        // Get all cropped images for the lines
        const lineImages = Array.from(linesImagesDiv.getElementsByTagName("img")).map(img => img.src);

        // Call the server to extract text from these images
        fetch("/extract-text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ lines: lineImages, decision: "yes" }) // Send the image paths
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "text_extracted") {
                // Create a container for displaying images and extracted text
                const textContainer = document.createElement("div");
                textContainer.style.display = "flex";
                textContainer.style.flexDirection = "row";
                textContainer.style.gap = "20px";
                let full_text = ""

                // Loop through the extracted text and the corresponding line images
                data.text.forEach((text, index) => {
                    const column = document.createElement("div");
                    column.style.display = "flex";
                    column.style.flexDirection = "column";
                    column.style.alignItems = "center";

                    // Original image
                    const originalImage = document.createElement("img");
                    originalImage.src = lineImages[index];
                    originalImage.alt = "Original line image";
                    column.appendChild(originalImage);

                    // Modifiable text box
                    const textBox = document.createElement("textarea");
                    textBox.value = text;  // Pre-fill with extracted text
                    column.appendChild(textBox);

                    textContainer.appendChild(column);
                    full_text += " " + text;
                });

                // Modifiable text box
                const fullTextBox = document.createElement("textarea");
                fullTextBox.value = full_text;  // Pre-fill with extracted text
                fullTextSection.appendChild(fullTextBox);

                // Append the textContainer to the lines-images div
                textSection.appendChild(textContainer);

                // Show the text extraction section
                preprocessSection.style.display = "none";
                linesImagesDiv.style.display = "none";
                extractionSection.style.display = "block"
            }
        });
    });

    document.getElementById("preprocess-no").addEventListener("click", () => {
        if (window.confirm("Do you want to retake the image?")) {
            // User pressed "Yes"
            location.reload(); // Reload page or update the UI as necessary
        }
    });

    // Syntax and Grammar check button
    document.getElementById("syntax-check").addEventListener("click", () => {
        const fullText = document.getElementById("fulltext-section").querySelector("textarea").value;

        // First, perform the syntax check
        fetch("/check-syntax", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: fullText })
        })
        .then(response => response.json())
        .then(data => {
            const syntaxFixed = data.fixed;

            // Then, perform the grammar check on the syntax-fixed version
            fetch("/check-grammar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: syntaxFixed })
            })
            .then(response => response.json())
            .then(data => {
                const grammarFixed = data.fixed;

                // Show both the syntax and grammar fixed versions
                document.getElementById("check-original").textContent = fullText;
                document.getElementById("check-syntax-fixed").textContent = syntaxFixed;
                document.getElementById("check-grammar-fixed").textContent = grammarFixed;

                // Show the combined check section
                extractionSection.style.display = "none";
                checkSection.style.display = "block";
            });
        });
    });
});
