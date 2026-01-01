
![LivygoLogo3Transpa](https://github.com/user-attachments/assets/86fe7b58-60ed-4a0e-9f40-aa7af14e3edc)

# Livygo Project

Livygo is a Duolingo-ish like application where you can learn things by gamifying things. Yep, pretty straightforward. **Also This project is made completely using AI tools.** 'though you can fork this up and make some human adjustment if you wanted. *Livy* don't care. All I cared about is to ctrl+c and ctrl+v codes.

... Just joking. This is nothing much really when you have [Anki](https://apps.ankiweb.net/) and [Lingonaut Project](https://www.reddit.com/r/Lingonaut/) in your pocket.

## Disclaimer 

Well, if you are here to blame my blatant usage of LLMs or AI, sure go on. Livy do not *code* Livy's code in this repository.

This doesn't mean I am illiterate with the code content however. In regards to code literacy, there are real vulnerabilities when you entrust LLM on cybersecurity/API stuff too much, especially when YOU simply *vibe coding* and never take a second to understand even a slightest of their code. Even though it may delivers, as a developer you are putting yourself in a great risk of getting DDoS attack. I did not mean you should avoid using LLM for this exact purpose, you SHOULD take a whole table of salt with it. Remember, I hold the responsibility to all my accounts on the Internet, and I will NOT endorse any idea to allow my code to attack my networking for the slightest.

Seriously, Livy also don't want to recommend those who have zero coding knowledge to do what Livy exactly be doing. You will ended up spending more time just trying to find a typo somewhere in the code. Also it will be a catastrophe to add new features if you DON'T plan things properly in prior. You should let AI help you and not you help AI.

# Development Log : January 1 2026

Happy new year! It's been a little while since the last update of this project. I have been working on other things IRL these few months and haven't really take my focus on this project. Anyway here's the update :

1. You can now experience Livygo through this Github Pages website ( https://sewlell.github.io/Livygo/mainnightly.html ). To implement this, minor adjustment have made in the code so that it can run either on Github Pages host or locally.
2. Updated lessons for both JP-en and ES-en. For some reason I haven't updated it in the past few months so I do it now. You can try Type 1 to Type 6 questions in JP-en and Type 1 to Type 4 in ES-en.
3. A debug button where you click it, it will reset your Relearn Pools question to none. It will be more specific in the future like resetting the course chosen by user. 

Yep, that's it. It is a small update, but I promise next update will be the large one that involved UI updates and massive source code organization. Please look forward to the next update.

# Development Log : June 14 2025

Alright I am back. During this 3 months, I have been laying off this project to focus on something else in my personal life, and will probably return to focus after a couple weeks. I am actually *kinda* failed to reach the goal I have set in March partially due to me procrastinating this project. But welp, this supposed to just be a fun project so it is fine, I can add stuff when I have some brilliant idea or something anytime. And no, I didn't wish to abandon this project anytime soon even though it might be in a hiatus.

Anyway off from this personal update, in this Livygo update :

1. Fix the unresponsive state when try to enter a lesson. I have aware of this and then forgot to give this repo an update when I fix it.
2. Add New Course page is added, although for now it is just a decoration, but in that page it show courses that I planned to create in the future.
3. Revamp Japanese for English speakers course into much complete sample course. This is not supposed to be a "from-scratch-to-fluency" course.
4. You can now access to the `editor` folder to open up a GUI to edit course (Circles, Pathway Structure, Lessons). There will be some settings missing like the inability to toggle `allowUnlimitedPracticePool` and the inability to create Type 6 questions through it,
5. Spanish for English speakers course's Guidebooks have edited although it is incomplete.
6. Fix Distractors only focusing on current Circle issue.

![Screenshot (143)](https://github.com/user-attachments/assets/e23602d9-9d90-43ae-88e8-03807f17690a)


# Development Log : March 26 2025

1. Introducing Question Type 5, a drag-and-drop one-to-many-subquestions question. Basically you got Word Blocks and you drag it to the respective blanks space. You can also type your answer in Type Answer mode.
2. Add Relearn Pool/New Words indicator. This is for future further development of question shuffle algorithm. It will show up either Green or Yellow on top left corner of your browser. For the time being, it's limiting to only Type 1 and Type 2.
3. Revamp the question shuffle algorithm completely from being randomized to randomize according to Question Types Ratio and New Question Ratio.
4. Adding default profile. This is just a decoration for Offline Mode and you could change whatever profile you want in `profile.json` and `/images/`. Obviously this will be different once it is online.

There are still minor issue within this update. As I suspect that the `relearnpool` and `practicecirc` in `lesson_progress.json` toggle simply do not work. Setting `relearnpool` off doesn't turn off the utilization of Relearn Pool and setting the `practicecirc` to `true` doesn't actually forcefully disable New Words Pool from being utilized. Also multiple settings that are unused ( Allowed Variants in that OCR settings for example ) should have remove from this update but I forgot. Eh, I will fix this after couple of more updates.

Next update would be focusing on course questions. This gonna be a hell of a workload to work with so wish me luck.

![Screenshot (42)](https://github.com/user-attachments/assets/25e90b01-8622-4a91-a979-18512069e635)



Former changelog have been archived in Pastebin. [Take a look](https://pastebin.com/XfFGw8cw) if you are interested in development progress.

## Running Locally

`git clone` this repository, and make sure you have Python 3 in order to run this web. In Command Prompt, type the following command.

```
python -m http.server 7500
```

After that, go to your web browser and enter `http://localhost:7500/mainnightly.html`.

If you wish to open the Editor GUI, enter this command in Terminal/Command Prompt (which you open it in the `editor` folder)

```
python courseeditor.py
```

## Todo Lists and Features (Planned)

- [ ] **Create a Official Course Pathway**

  - [ ]  Spanish (EN)
    - [ ] VOCABULARY
    - [ ] GRAMMAR
  - [x]  Japanese (EN)
    - [x] GENERAL
  - [ ]  English (CN)
  - [ ]  Malay (CN)
  - [ ]  American Sign Language
  - [ ]  Chemistry Principles (NON-LANGUAGE)

- [ ] Finish UI Decorations
- [ ] Write a more completed Guidebooks
- [ ] Hookup AI TTS Voices on Courses
- [x] Adaptability of Community Courses
- [x] Polish the Logo
- [ ] Possible Flashcard Mode and Anki Import (Erm, I guess?)
- [ ] Livy on Main Page
- [ ] Alpha Web Launch (not so soon)
- [ ] Android/IOS Version

## Current AI Tools Used

- [DeepSeek R1](https://www.deepseek.com/) by DeepSeek
- [Gemini 2.5 Pro](https://aistudio.google.com) by Google
- [GPT o3-mini and 4o](https://chatgpt.com/) by OpenAI (Served as Alternative for DeepSeek)
- GPT 5 and 5.2

- [GPT SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) by RVC-Boss
- [Fish Speech S1 and S1 mini](https://github.com/fishaudio/fish-speech) by Fish Audio
- [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) by RVC Project Team
- ... and a lot of open-source TTS like [XTTS v2](https://huggingface.co/coqui/XTTS-v2) and [Chatterbox](https://github.com/resemble-ai/chatterbox).

## Code Credits

- [WanaKana](https://github.com/WaniKani/WanaKana) by WaniKani

## License

This Project use `GNU GPL v3` as its license. This license allows you to distribute freely and use for COMMERCIAL PURPOSES given you as the user have credit this repository. Modifications of this repository should have the SAME LICENSE as this repository.