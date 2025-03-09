![LivygoLogo2](https://github.com/user-attachments/assets/41ab90ca-ad91-43f6-968c-accd3fef7047)

# Livygo Project started!

Livygo is an application to let you customize... literally everything while keeping Duolingo gamification factors. This Project also being coded *completely* using DeepSeek R1 and voiced using AI TTS, while keeping its open arms to those who want to volunteer at multiple areas. ( Course Creation, Voice Recording, etc ). This is nothing much really when you devote yourself in using [Anki](https://apps.ankiweb.net/).

# Development Log : March 1 2025

1. Add a Typo/Spelling Yellow Feedback on Question Page when user mistype or misspell something.
2. Ungodly amount of time fixing how Practice Circle and Focursed Circle interacts with the concept of Relearn Pool and New Words Pool. Thank God it's finally able to enter back to Question Page like before and Relearn Pool actually do something.
3. Fixed different information fetch and gap between `mainnightly.html` and `question.html`.
4. Fix Progress Bar on Circle's Dropdown and Question Page.
5. Toggleables `praclimit` `pracrepetition` added, it's pretty quirky at the moment as I suspected the issue came from the interaction between `codePaser.js` and `question.html`.
6. Redirection back to Main Page if there is no longer any questions to show, this is because of currently lacks of (toggleable) Dynamic `questionsPerLesson` and available questions.

# Development Log : February 21 2025

1. Adding on Question Page's Cutscenes customizability to allow user to create their own cutscene for their own Course. It's pretty broken, tried to fix it up couple days later included the situation where Questions don't appear at all.
2. Change the font to Poppins using Google Font API.
3. Flag Button is freaking broken.
4. Fix the disappearance of Circle's Dropdown.
5. Where's the space for Livy? Although I still haven't learn After Effects to animate Livy *yet*.

## Todo Lists and Features (Planned)

- [ ] **Create a Official Course Pathway**

  - [ ]  Spanish (EN)
    - [ ] VOCABULARY
    - [ ] GRAMMAR
  - [ ]  Japanese (EN)
    - [ ] VOCABULARY
    - [ ] GRAMMAR 
  - [ ]  English (CN)
  - [ ]  Malay (CN)

- [ ] Finish UI Decorations
- [ ] Write a more completed Guidebooks
- [ ] Hookup AI TTS Voices on Courses
- [ ] Adaptability of Community Courses
- [ ] Polish the Logo
- [ ] Possible Flashcard Mode and Anki Import (Erm, I guess?)
- [ ] Livy on Main Page
- [ ] Alpha Web Launch (not so soon)
- [ ] Android/IOS Version

## Current AI Tools Used

- [DeepSeek R1](https://www.deepseek.com/) by DeepSeek
- [GPT o3-mini and 4o](https://chatgpt.com/) by OpenAI (Served as Alternative for DeepSeek)
- [GPT SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) by RVC-Boss

## Disclaimer 

Yes I know. Some people hate AI tools with a passion especially when they are using a language-teaching application. The concerns like mispronunciation and low quality teaching content are legitimate and I am NOT going to deny that. Despite massive usage of AI in this project, I open my doors to those who want to help this project voluntarily or pull requests. And also, I did not ask for your opinions on using AI instead of real programmer and your argument of "AI replacing human's jobs". Sure I should have code myself or another person to do code, and sure it could probably replace some jobs. But this only limited to repetitive jobs and even then it still need human supervision.

This topic have been discussed for who-knows-how-many times, and if you just don't like how grey is Deepseek or AI in general, just don't use this and move on to better alternative like Lingodeer or Anki.

## License

This project use `CC-BY-NC-SA 4.0` license. Which mean you are allowed to use this for NON-COMMERCIAL purposes and code included this project using the SAME license as this project. Under this license, you are allowed to share and adapt, whether you modify or alter given you have credited to this project.
