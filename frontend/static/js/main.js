// ELEMENTS
const nonRagBtn = document.getElementById("nonRagBtn");
const ragBtn = document.getElementById("ragBtn");
const queryInput = document.getElementById("queryInput");
const fileUploadContainer = document.getElementById("fileUploadContainer");
const fileInput = document.getElementById("fileInput");
const submitBtn = document.getElementById("submitBtn");
const loader = document.getElementById("loader");
const resultBox = document.getElementById("resultBox");
const resultText = document.getElementById("resultText");

let mode = "non-rag";


// MODE SWITCH
nonRagBtn.onclick = () => {
    mode = "non-rag";
    nonRagBtn.classList.add("bg-blue-600");
    ragBtn.classList.remove("bg-blue-600");
    fileUploadContainer.classList.add("hidden");
};

ragBtn.onclick = () => {
    mode = "rag";
    ragBtn.classList.add("bg-blue-600");
    nonRagBtn.classList.remove("bg-blue-600");
    fileUploadContainer.classList.remove("hidden");
};


// MARKDOWN RENDER
function renderMarkdown(text) {
    return marked.parse(text);   // using CDN
}


// FORMAT CLEAN RESPONSE (NO TRASH JSON)
 function formatResponse(data) {
    if (data.status !== "success") {
        return `❌ **Error:** ${data.error || data.metadata?.error}`;
    }

    let answer = data.final_answer || "";
    let summary = data.summary || data.writer_agent_output?.summary || "";
    let sections = data.sections || data.writer_agent_output?.sections || [];
    let citations = data.citations || data.writer_agent_output?.citations || [];
    let sources = data.sources || [];

    let md = "";

    // Summary
    if (summary) {
        md += `## 📝 Summary\n${summary}\n\n`;
    }

    // Final answer
    if (answer) {
        md += `## 🧠 Final Answer\n${answer}\n\n`;
    }

    // Sections
    if (sections.length) {
        md += `## 📚 Sections\n`;
        sections.forEach(sec => {
            md += `### ${sec.heading}\n${sec.content}\n\n`;
        });
    }

    // Citations
    if (citations.length) {
        md += `## 🔗 Citations\n`;
        citations.forEach(c => {
            md += `- **${c.chunk_id}** — ${c.excerpt}\n`;
        });
    }

    // Sources
    if (sources.length) {
        md += `## 📄 Sources\n`;
        sources.forEach(s => {
            md += `- ${s.text_excerpt}\n`;
        });
    }

    return md || "No content returned.";
}


 // SUBMIT HANDLER
 submitBtn.onclick = async () => {
    const query = queryInput.value.trim();
    if (!query) {
        alert("Enter a query first.");
        return;
    }

    loader.classList.remove("hidden");
    resultBox.classList.add("hidden");

    try {
        let response;

        if (mode === "non-rag") {
            response = await fetch("http://127.0.0.1:8000/api/non-rag/run/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query })
            });

        } else {
            const file = fileInput.files[0];
            if (!file) {
                alert("Please upload a document for RAG mode.");
                loader.classList.add("hidden");
                return;
            }

            const form = new FormData();
            form.append("file", file);
            form.append("query", query);

            response = await fetch("http://127.0.0.1:8000/api/rag/run/", {
                method: "POST",
                body: form
            });
        }

        const data = await response.json();
        const md = formatResponse(data);

        resultText.innerHTML = renderMarkdown(md);
        resultBox.classList.remove("hidden");

    } catch (err) {
        resultText.innerHTML = `❌ Error: ${err.message}`;
        resultBox.classList.remove("hidden");

    } finally {
        loader.classList.add("hidden");
    }
};
