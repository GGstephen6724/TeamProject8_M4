from mcp.server.fastmcp import FastMCP
import json
from pathlib import Path


# Create MCP server
mcp = FastMCP("Job Search Tools")


# Location of our job database
DATABASE = Path(__file__).with_name(
    "jobs.json"
)


# ------------------------------------------------
# JOB SEARCH TOOL
# ------------------------------------------------

@mcp.tool()
def search_jobs(
    keywords: str = "",
    location: str = "",
    remote: bool = False,
    employment_type: str = "",
    minimum_salary: float = 0,
    skills: str = ""
) -> str:

    """
    Search the prototype job database using
    the user's job preferences.

    keywords:
        Job title or general search terms.

    location:
        Location such as Remote or Fort Myers.

    remote:
        If true, only return remote jobs.

    employment_type:
        Part-time or Full-time.

    minimum_salary:
        Minimum acceptable hourly salary.

    skills:
        Comma-separated skills such as Python, SQL.
    """


    # ------------------------------------------------
    # LOAD DATABASE
    # ------------------------------------------------

    try:

        with DATABASE.open(
            "r",
            encoding="utf-8"
        ) as file:

            jobs = json.load(file)

    except FileNotFoundError:

        return "ERROR: jobs.json was not found."

    except json.JSONDecodeError:

        return "ERROR: jobs.json contains invalid JSON."


    # ------------------------------------------------
    # NORMALIZE INPUT
    # ------------------------------------------------

    keywords = keywords.lower().strip()

    location = location.lower().strip()

    employment_type = (
        employment_type
        .lower()
        .strip()
    )


    requested_skills = [

        skill.strip().lower()

        for skill in skills.split(",")

        if skill.strip()
    ]


    matches = []


    # ------------------------------------------------
    # SEARCH JOBS
    # ------------------------------------------------

    for job in jobs:

        searchable_text = (
            job["title"]
            + " "
            + job["company"]
            + " "
            + " ".join(job["skills"])
        ).lower()


        # Keyword filter

        # Keyword filter
        if keywords:
            keyword_terms = [
                term.strip().lower()
                for term in keywords.split()
                if term.strip()
            ]

            # Expand common job-search terms to related titles.
            keyword_aliases = {
                "developer": ["developer", "programmer", "engineer"],
                "development": [
                    "development", "developer", "programmer",
                    "programming", "software engineer",
                ],
                "software": ["software", "programmer"],
                "web": ["web", "frontend", "front-end", "website"],
                "programming": ["programming", "programmer", "developer"],
            }

            expanded_terms = []
            for term in keyword_terms:
                expanded_terms.extend(keyword_aliases.get(term, [term]))

            if not any(
                term in searchable_text
                for term in expanded_terms
            ):
                continue



        # Location filter
        if location:

            if location not in job["location"].lower():

                continue


        # Remote filter
        if remote:

            if not job["remote"]:

                continue


        # Employment type filter
        if employment_type:

            if (
                job["employment_type"].lower()
                != employment_type
            ):

                continue


        # Salary filter
        if job["salary_min"] < minimum_salary:

            continue


        # Skills filter
        if requested_skills:

            job_skills = [

                skill.lower()

                for skill in job["skills"]
            ]


            skill_match = any(

                requested in job_skill

                for requested in requested_skills

                for job_skill in job_skills
            )


            if not skill_match:

                continue


        matches.append(job)


    # ------------------------------------------------
    # RETURN RESULTS
    # ------------------------------------------------

    if not matches:

        return (
            "No jobs matched the provided criteria."
        )


    return json.dumps(
        matches,
        indent=2
    )


# ------------------------------------------------
# START MCP SERVER
# ------------------------------------------------


MEMORY_FILE = Path(__file__).with_name("memory.json")

ALLOWED_PREFERENCES = {
    "keywords",
    "location",
    "remote",
    "employment_type",
    "minimum_salary",
    "skills",
}


def load_memory():
    if not MEMORY_FILE.exists():
        return {}

    try:
        with MEMORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_memory(data):
    with MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


@mcp.tool()
def get_saved_preferences() -> str:
    """Retrieve saved job-search preferences."""
    return json.dumps(load_memory(), indent=2)


@mcp.tool()
def save_preference(key: str, value: str) -> str:
    """Save a job preference only when the user explicitly asks."""
    key = key.strip().lower()

    if key not in ALLOWED_PREFERENCES:
        return "ERROR: Unsupported preference key."

    value = value.strip()

    if key == "remote":
        if value.lower() not in {"true", "false"}:
            return "ERROR: remote must be true or false."
        value = value.lower() == "true"

    elif key == "minimum_salary":
        try:
            value = float(value)
            if value < 0:
                return "ERROR: minimum_salary cannot be negative."
        except ValueError:
            return "ERROR: minimum_salary must be a number."

    preferences = load_memory()
    preferences[key] = value

    try:
        save_memory(preferences)
    except OSError:
        return "ERROR: Could not save preferences."

    return f"Saved preference '{key}'."


@mcp.tool()
def clear_saved_preferences() -> str:
    """Clear all saved job-search preferences."""
    try:
        save_memory({})
    except OSError:
        return "ERROR: Could not clear saved preferences."

    return "All saved job-search preferences have been cleared."


if __name__ == "__main__":

    mcp.run()
