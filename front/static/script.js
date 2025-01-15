document.addEventListener("DOMContentLoaded", () => {
    const imageSection = document.getElementById("image-section");
    const preprocessSection = document.getElementById("preprocess-section");
    const textSection = document.getElementById("text-section");
    const fullTextSection = document.getElementById("fulltext-section");
    const syntaxSection = document.getElementById("syntax-section");
    const grammarSection = document.getElementById("grammar-section");
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
        alert("Please retake the image!");
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
                console.log(data.text)

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

                console.log(full_text)
                // Modifiable text box
                const fullTextBox = document.createElement("textarea");
                fullTextBox.value = full_text;  // Pre-fill with extracted text
                fullTextSection.appendChild(fullTextBox);



                // Append the textContainer to the lines-images div
                textSection.appendChild(textContainer);

                // Show the text extraction section
                preprocessSection.style.display = "none";
                linesImagesDiv.style.display = "none";
                // textSection.style.display = "block";
                extractionSection.style.display = "block"
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
