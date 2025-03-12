![LivygoLogo2](https://github.com/user-attachments/assets/41ab90ca-ad91-43f6-968c-accd3fef7047)

# Livygo Project started!

Livygo is an application to let you customize... literally everything while keeping Duolingo gamification factors. This Project also being coded *completely* using DeepSeek R1 and voiced using AI TTS, while keeping its gate wide open to those who want to create their own courses ( Community Courses ) or improve the codebase. This is nothing much really when you have [Anki](https://apps.ankiweb.net/) and [Lingonaut Project](https://www.reddit.com/r/Lingonaut/).

# Development Log : March 12 2025

Kinda rush update for this one. Anyway here's the list of feature updates.

1. Changing Circle and Lesson `code` from 4-number (1001,2345,1203-3) to 3-3 combination (0001001,002345,001203-3). This will allows you guy to expand even more Sections for lessons.
2. Introducing Guidebooks system where you can write your own guide on specific Circle or around the range of Circles using `guide_structure.json`
   - To differentiate each individual Guidebooks or Guidebooks Categories, I introduce `guidcode` that work similar to normal `code` except no naming limitations, just syntax.
   - Guidebooks text content use Markdown textfile with most basic syntax supported (Headings, Blockquotes, Code).
3. Subcourses are now working properly. Basically in this update you will see Spanish (ES-en) split into two parts, General and Vocabulary.
   - I mean, technically it is just a many-in-one solution for those who like to categorise stuff.
   - As for current it is limited to 3 Subcourses, General, Vocabulary and Grammar. The title and UI are still fixed, I will add a function where it could dynamically reacts to user's title and number of Subcourses.
5. Main Page UI Touchup. I got :skull: when I'm working with transition animation on that slide-in slide-out Guidebooks Page and Back Navigation.
6. Useless functions removed for `mainnightly.html`. Still, there are 1000 lines worth of code in 1 file compared to March 10 thank to that Guidebooks system.

Demonstration Video


https://github.com/user-attachments/assets/95e2d2ab-074d-4bc5-8bfa-874a84cb56eb


# Development Log : March 10 2025

This is a very huge update this time. As I able to make a breakthrough in addition of features. Due to how big this update is, I will only cover major feature update here.

1. Add Type 3 and Type 4 questions, Type 3 is listening words questions and Type 4 is listening sentence questions. Both types can be answer either by Selection/Word Blocks or Type Answers input.
2. Add JP-en course. Of course it's just a small course for now.
3. Optimize how Relearn Pools works in Focused Circle or Practice Circle.
4. Add the file `pathway_structure.json`. This file allows user to split Circles into sections and putting all those Question Type files in respective sections. This will allow easier management on creating files compared to former bracket.
5. Due to updates above, the folder hierachy is also changed with the addition of `courses` folder. All Question Type and `lesson_progress.json` are moved to the `courses/[lang]/...` folder.
6. Types now can be *optional* with the `enabledQuestionTypes` at `pathway_structure.json`. That mean for future courses like ASL and Chemistry Principles, Type 3 and Type 4 can be opt out completely while using other types.

There are still flaws within this update. For example in Type 3 Questions, you can click numerous answer and jump several questions. I also forgot to set the textbox at Type 3 and Type 4 `autocomplete="off"` before pushing, which caused the textbox to have answer you typed before. I want to make a reversed version of Type 1 ( with a Toggleables or somewhat ) where you got hinted with a foreign words and choose correct translation. Well in overall, I kinda happy with how it have turned out.

Here's the demo video to demonstrate this update.


https://github.com/user-attachments/assets/84fabad4-d8a5-4c9e-a515-3420df7950bf



Former changelog have been archived in Pastebin. [Take a look](https://pastebin.com/XfFGw8cw) if you are interested in development progress.

## Running Locally

`git clone` this repository, and make sure you have Python 3 in order to run this web. In Command Prompt, type the following command.

```
python -m http.server 7500
```

After that, go to your web browser and enter `http://localhost:7500/mainnightly.html`.

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
  - [ ]  American Sign Language
  - [ ]  Chemistry Principles (NON-LANGUAGE)

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
- [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) by RVC Project Team

## Disclaimer 

Yes I know. Some people hate AI tools with a passion especially when they are using a language-teaching application. The concerns like mispronunciation and low quality teaching content are legitimate and I am NOT going to deny that. Despite massive usage of AI in this project, I open my doors to those who want to help this project voluntarily or pull requests. And also, I did not ask for your opinions on using AI instead of real programmer and your argument of "AI replacing human's jobs".

This topic have been discussed for who-knows-how-many times, and if you just don't like how grey is Deepseek or AI in general, just don't use this and move on to better alternatives.

## License

This project use `CC-BY-NC-SA 4.0` license. Which mean you are allowed to use this for NON-COMMERCIAL purposes and code included this project using the SAME license as this project. Under this license, you are allowed to share and adapt, whether you modify or alter given you have credited to this project.
