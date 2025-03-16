import requests

url = "https://api.resemble.ai/v1/projects/{project_id}/clips"
headers = {
    "Authorization": "Bearer P5Sv5CDTc1EQnnWt9T7gFwtt",
    "Content-Type": "application/json",
}
data = {
    "text": "Hello, this is a cool voiceover.",
    "voice": "obama",  # Example voice
    "emotion": "happy",  # You can specify emotion here
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    audio_url = response.json().get("audio_url")
    print(f"Audio URL: {audio_url}")
else:
    print(f"Error: {response.status_code}")