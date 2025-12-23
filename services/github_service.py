import requests

def fetch_public_repos(username):
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    response.raise_for_status()

    repos = []
    for repo in response.json():
        repos.append({
            "url": repo["html_url"],
            "language": repo["language"] or "Unknown"
        })
    return repos
