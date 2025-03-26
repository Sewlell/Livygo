
![LivygoLogo3Transpa](https://github.com/user-attachments/assets/86fe7b58-60ed-4a0e-9f40-aa7af14e3edc)

# Livygo Project

Livygo is an application to let you customize... literally everything while keeping Duolingo gamification factors. This Project also being coded *completely* using DeepSeek R1 and voiced using AI TTS, while keeping its gate wide open to those who want to create their own courses ( Community Courses ) or improve the codebase. This is nothing much really when you have [Anki](https://apps.ankiweb.net/) and [Lingonaut Project](https://www.reddit.com/r/Lingonaut/).

# Development Log : March 26 2025

1. Introducing Question Type 5, a drag-and-drop one-to-many-subquestions question. Basically you got Word Blocks and you drag it to the respective blanks space. You can also type your answer in Type Answer mode.
2. Add Relearn Pool/New Words indicator. This is for future further development of question shuffle algorithm. It will show up either Green or Yellow on top left corner of your browser. For the time being, it's limiting to only Type 1 and Type 2.
3. Revamp the question shuffle algorithm completely from being randomized to randomize according to Question Types Ratio and New Question Ratio.
4. Adding default profile. This is just a decoration for Offline Mode and you could change whatever profile you want in `profile.json` and `/images/`. Obviously this will be different once it is online.

There are still minor issue within this update. As I suspect that the `relearnpool` and `practicecirc` in `lesson_progress.json` toggle simply do not work. Setting `relearnpool` off doesn't turn off the utilization of Relearn Pool and setting the `practicecirc` to `true` doesn't actually forcefully disable New Words Pool from being utilized. Also multiple settings that are unused ( Allowed Variants in that OCR settings for example ) should have remove from this update but I forgot. Eh, I will fix this after couple of more updates.

Next update would be focusing on course questions. This gonna be a hell of a workload to work with so wish me luck.

![Screenshot (42)](https://github.com/user-attachments/assets/25e90b01-8622-4a91-a979-18512069e635)

# Development Log : March 15 2025

##  The repository license have now changed from `CC-BY-NC-SA 4.0` to `GPL v3.0` to better approaching open source community. This also means now you can use this code for commercial purpose prior credited.

This is a much smaller update as I have difficulty figuring up new Question Type. In spite of that, it have arrive and working OK now.

1. License Change as mentioned above.
2. Introducing Question Type 6, Type 6c to be precise for Japanese Kanji ( it will rename to 6a once I merge it with Hanzi and Hanja ). This is a character-stroke recognition question that only appear in Handwrite Circle (`handwritecirc` in `lesson_progress.json`). Basically what you do is write on a canvas and the code will check whether it is in correct order or not.
   - The process of develop this have throw me out. I originally want to utilize [KanjiVG](https://github.com/KanjiVG/kanjivg) to do some kind of SVG-stroke check, however it ended up a catastrophe with the entire expected stroke inverted, and that the code have no clue how to deal with `startPoint` and `endPoint`.
   - Even when I change the way the codebase to recognize stroke using 6-points circle measure. It works surprisingly OK, but it might have issue expanding to much more specific stroke. (`CURVE` is stated in the code but I have no idea what is the stroke for the code to recognize `CURVE` without getting `LEFT_FALLING` or `RIGHT_FALLING`)
   - OCR Validation is not available to make it more local-available.
3. Remove clutter in `question.html`. Also met the same fate as last update's `mainnightly.html`.

Yup, that's it. Just three. The next step would be Type 5 ( many-subquestion phrase/grammar/vocabulary question ) and Type 1a 1b ( Split `translation` and `word` for either answer or question ).

Go to the 4th Circle in JP-en General course if you want to try Type 6 questions.

Demonstration Video



https://github.com/user-attachments/assets/3e419fbb-7b9d-463b-be33-f36dffa3eb5c




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
- [x] Polish the Logo
- [ ] Possible Flashcard Mode and Anki Import (Erm, I guess?)
- [ ] Livy on Main Page
- [ ] Alpha Web Launch (not so soon)
- [ ] Android/IOS Version

## Current AI Tools Used

- [DeepSeek R1](https://www.deepseek.com/) by DeepSeek
- [GPT o3-mini and 4o](https://chatgpt.com/) by OpenAI (Served as Alternative for DeepSeek)
- [GPT SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) by RVC-Boss
- [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) by RVC Project Team

## Code Credits

- [WanaKana](https://github.com/WaniKani/WanaKana) by WaniKani

## Disclaimer 

Well, if you are here to blame my blatant usage of LLMs or AI, sure go on. I do not *code* my own code.

This doesn't mean I am illiterate with code syntax and content however. In regards to literacy, there are real vulnerabilities when you entrust LLM on cybersecurity/API stuff, especially when YOU simply *vibe coding* and never ever understand even a slightest of their code. Even though it delivers, you as a developer is putting yourself in a great risk of getting DDoS attack once you put yourself publicly. Not like you should avoid entrust LLM for anything, but remember I hold the responsibility to my Internet accounts, and I do not endorse any idea to allow my code to attack my networking for the slightest.

Hence, this repository will be ENTIRELY local-based and offline-available. Stuffs like Profile and Shop will be set using a default JSON which you can edit whatever you like. ( Although it's decorative with no real purposes offline ). I still planned to launch an online version of the application ( with some alteration of the code ) but backend development is a field that I have never enter before. 

## License

This Project use `GNU GPL v3` as its license. This license allows you to distribute freely and use for COMMERCIAL PURPOSES given you as the user have credit this repository. Modifications of this repository should have the SAME LICENSE as this repository.
