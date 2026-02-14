<h1 align="center">Workout Plan Generator</h1>
<p align="center">
  A Python + Flask app that Generates personalized workout plans using NLP and machine learning.
Users can describe there goals in plain English (e.g. "Can you make me a 4-day beginner workout plan. 
But I can't work out on Tuesdays), and the program will parse their input and build a full workout program.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Educational-green" />
</p>

## Table of Contents

- [Security](#security)
- [Background](#background)
- [Features](#features)
- [Demo Video](#demo-video)
- [Install](#install)
- [Usage](#usage)
- [API](#api)
- [Contributing](#contributing)
- [License](#license)


## Security
This application runs locally and does not require users to upload personal data to external services. Any user inputs (e.g., fitness goals, workout preferences) are processed on-device. The project is intended for educational and personal-use. This application should not be used as a substitute for professional medical or fitness advice.

## Background
Personalized workout planning is often locked behind paid apps, rigid templates, or generic “one-size-fits-all” routines that don’t adapt well to individual goals, experience levels, or available equipment. Many beginners struggle to design effective training splits, while more experienced lifters want flexible programs that can evolve with their progress. This project explores a local, customizable workout generator that uses structured exercise data and simple logic to create tailored workout plans based on user preferences such as goals, experience level, available equipment, and time constraints. The goal is to provide an accessible, hackable baseline for building and experimenting with personalized fitness planning tools while keeping user data local and under the user’s control.


## Features

- **NLP-Powered Parsing** - User text is classified into difficulty, splits, days, and muscle groups.
- **Difficulty-Aware Plans** - Choose from 'beginner', 'intermediate', or 'advanced' for appropriate programming
- **Customizable** - Users can tweak workout exercises to get desired workouts.
- **Local Exercise Database** - Pulled via API and cached for speed.

## Demo Video
https://github.com/user-attachments/assets/bfcf4efb-8bf0-45a9-b35d-4946511e9ea9

## Install
```bash
git clone https://github.com/yourname/workout-plan-generator.git  
cd workout-plan-generator
pip install -r requirements.txt
```

## Usage
**Run with Docker**
```bash
docker build -t workout-generator .
docker run -p 8000:8000 workout-generator
```

**Run Locally**
```bash
pip install -r requirements.txt
flask run --host=0.0.0.0 --port=8000
```

## API

#### `Workout Planner`
**Location:** `src/workout_planner.py`

**Description:**  
Generates a personalized workout plan based on parsed user preferences and constraints.

**Constructor:**
```python
Workout(user_input)
```
#### `Parsing Input`
**Location:** `src/parse_user_input.py`

**Description:**  
Parses natural language user input to extract goals, availability, difficulty level, and workout preferences.

**Constructor:**
```python
ParseInput(user_input)
```


## Contributing

Contributions are welcome!
1. Fork the repo
2. Create a feature branch
3. Submit a PR with a clear description

## License
[MIT © Richard McRichface.](./LICENSE)
