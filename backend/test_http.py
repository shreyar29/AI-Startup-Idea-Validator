import urllib.request
import urllib.parse
import json
import sys

def main():
    idea = "An AI platform for autonomous drones that deliver medical supplies to remote areas."
    url = f"http://localhost:8000/search?query={urllib.parse.quote(idea)}"
    print(f"Fetching {url}...")
    try:
        req = urllib.request.Request(url, headers={'X-Request-ID': 'test-12345'})
        with urllib.request.urlopen(req) as response:
            data = response.read()
            print("Status Code:", response.getcode())
            print("Response Length:", len(data))
    except urllib.error.HTTPError as e:
        print("HTTP Error:", e.code)
        print("Response:", e.read())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
