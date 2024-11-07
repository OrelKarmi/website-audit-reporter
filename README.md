# Website Audit Reporter

The Website Audit Reporter leverages advanced Generative AI (GenAI) to perform in-depth analysis of websites. It generates comprehensive audit reports that cover various aspects such as how different stakeholders perceive the organization and whether the mission and goals are effectively communicated. This tool is designed to help non-profit organizations and stakeholders see and understand the performance and user experience of their websites, enabling them to identify and address issues to improve their website's effectiveness.

## Installation

```bash
# Clone the repository
git clone https://github.com/OrelKarmi/website-audit-reporter.git

# Navigate into the project directory
cd website-audit-reporter

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt

# Create a .env file from the example file
cp .env.example .env

# Set the URL in the main file and run the analysis
if __name__ == "__main__":
    url = "your url here"
    analyze_organization(url)
```

## Graphs

## Graphs

### Main Graph

The main graph provides an overview of the website's performance, highlighting key areas that need attention.

![Main Graph](images/main_graph.png)

### Researcher Graph

The researcher graph offers a more detailed analysis, focusing on specific elements and their impact.

![Researcher Graph](images/researcher_graph.png)


