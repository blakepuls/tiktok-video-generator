# Tiktok-Video-Generator

Tiktok-Video-Generator is a Python project that utilizes the OpenAI API to generate a narrative, which is then processed through Google Cloud Platform (GCP) Speech for text-to-speech and subtitle creation. The generated story is overlaid onto a randomly selected video at a random time point, creating a video output. The video is then automatically uploaded to TikTok.

Check out some of the generated videos [here](https://www.tiktok.com/@ai_story_generator).

## Prerequisites

- Python 3.5 or higher.
- Valid API keys for OpenAI.
- Valid credentials for Google Cloud Platform (GCP) Speech.

## Installation

```
git clone https://github.com/yourusername/Tiktok-Video-Generator.git
cd Tiktok-Video-Generator
pip install -r requirements.txt
```

## Configuration

### GCP Service Account

Create a service account for your project and add into the root directory as `service_account.json`

### Environment Variables

Create a `.env` file in the root directory:

```
IMAGEMAGIC_PATH = 'C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe'
OPENAI_API_KEY = '<your_openai_api_key>'
```

### Adding Background Footage

Add .mp3 files to the `/footage` folder.

### Browser Cookies for TikTok

Export your browser cookies for TikTok and create a `cookies.txt` file in the root directory.

### Output Directory

Final videos are exported to the `/videos` directory.

## Usage

```
python ./src/main.py
```

To generate a story around a specific topic:

```
python ./src/main.py --topic "Lost in the woods"
```

## License

This project uses the following license: [MIT License](https://opensource.org/licenses/MIT).
