# Persona-Driven Document Intelligence System

👉 **[View Full Approach Explanation](approach_explanation.md)**

# How to Run the Persona-Driven Document Intelligence System

This project is fully containerized using Docker — all dependencies and models are included. No Python setup or internet is needed during runtime.

---

## 1. Prerequisites

Install Docker Desktop for your operating system:

👉 [Download Docker](https://www.docker.com/get-started)

Ensure Docker is running before proceeding.

---

## 2. Prepare Your Project Directory

Clone the repository and navigate to the challenge directory:

```bash
git clone https://github.com/LokeshN1/doc-intelligence-challenge1b.git
````

---

## 3. Prepare the `input/` Folder

Structure your input like this:

```
input/
├── document1.pdf
├── document2.pdf
├── ...
└── config.json
```

* Place **3 to 10 PDF files** directly inside the `input/` folder.
* Include **exactly one** `config.json` file with the format:

```json
{
  "persona": "Example Persona Name",
  "job_to_be_done": "The specific job/task description the persona needs done."
}
```

> ⚠️ Important:
>
> * Do **not** use subfolders inside `input/`.
> * Do **not** include multiple or missing `config.json` files.

---

## 4. Build the Docker Image

Open a terminal inside the project root (where `Dockerfile` is located) and run:

```bash
docker build --platform linux/amd64 -t mysolutionname:challenge .
```

* First build may take a few minutes.
* Subsequent builds will be faster (because of Docker cache).

---

## 5. Run the System

### Option A: Using the script

```bash
bash run.sh  # powershell
```

### Option B: Manually using Docker

#### On **Windows PowerShell**:

```powershell
docker run --rm -v "%cd%/input:/app/input" -v "%cd%/output:/app/output" --network none mysolutionname:challenge
```

#### On **Linux/macOS terminal**:

```bash
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none mysolutionname:challenge
```


Results will be saved to: `output/analysis_result.json`

---

## 6. View the Output

After the run completes, check:

```text
output/analysis_result.json
```

---

## 7. Additional Notes

* **One test case per run:** Ensure only one batch of PDFs and one `config.json` per run.
* **Multiple test cases:** Re-run the container with different `input/` folders.
* **After code changes:** Rebuild the Docker image.
* **No internet required:** Model and dependencies are built into the image.

---

## Troubleshooting

* Check that `input/` has valid PDFs and a correct `config.json`.
* Ensure Docker Desktop is running.
* Check terminal logs for errors.

---

## 📌 Quick Command Summary

```bash

# Build the Docker image

docker build -t persona-doc-intelligence .

# Run the system
bash run.sh
# or
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" persona-doc-intelligence

# View output in 
output/analysis_result.json
```


