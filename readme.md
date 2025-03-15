# QuranASL - Translating the Quran into ASL using Artificial Intelligence

**QuranASL** aims to empower the deaf community by providing them access to the Quran in American Sign Language (ASL) through AI-generated hand gestures. Imagine the reward from Allah of enabling deaf people to understand the Quran in a language they visually comprehend, rather than simply reading the translation in English. This initiative seeks to bridge the gap by conveying the Quran’s meaning through ASL while maintaining its sacredness and beauty.

---

## Project Overview

Many people may not fully feel the power of the Quran when reading it in English alone. Similarly, deaf individuals may miss the depth of the Quran in their primary language, ASL. QuranASL offers a potential solution where each surah is presented in animated ASL hand gestures, along with Arabic and English translations displayed beneath the video.

To address the challenge of missing facial expressions in ASL, we propose using vibrations on the phone to convey tonality, which would reflect the rhythm and emphasis found in the Quranic recitation. This approach can provide a fuller, more immersive experience for the users, especially those who are partially deaf and may also be able to hear parts of the recitation.

---

## Key Features

1. **Hand Gestures Database**: 
   - Extract ASL word data from existing ASL video databases and use it to generate hand gestures for each Quranic word.
   - If a direct ASL translation does not exist for a word or phrase, it will be broken down into smaller, translatable parts.
   - Non-translatable names will be rendered in ASL through finger-spelling.

2. **AI Integration**: 
   - Utilize Google’s Hand Landmark Detection AI to convert ASL videos into computerized hand gestures.
   - Match every word and phrase in the Quran to a corresponding ASL video using AI-driven matching.

3. **App Experience**:
   - Create an app where each surah is accompanied by fluid, animated ASL gestures, with both Arabic and English translations shown beneath the video.
   - Vibrations will be used to represent tonality, enhancing the expressiveness of the signs.

4. **Collaboration with Deaf Community**:
   - Once the app is developed, feedback will be gathered from the deaf community to refine the translations, making the experience more accurate and inclusive.

---

## Project Phases

### Phase 1: Understanding the Problem
- **Objective**: Investigate the challenges and requirements for translating the Quran into ASL using AI.
- **Output**: Familiarize with the ASL video data and Quranic translation datasets.

### Phase 2: Data Collection and Matching
- **Objective**: 
  - Extract ASL word data from video databases.
  - Extract Quranic word data and prepare a corresponding text file.
  - Use AI to match each Quranic word/phrase to an ASL word or break it down to a set of words.
  - **End Goal**: Create a JSON file containing every surah and its respective ayah, each mapped to the ASL video URL(s).

- **Resources**:
  - **ASL Databases**:
    - [Sign ASL](https://www.signasl.org/)
    - [WLASL Dataset on Kaggle](https://www.kaggle.com/datasets/risangbaskoro/wlasl-processed?resource=download)
    - [Microsoft ASL Dataset](https://www.microsoft.com/en-us/download/details.aspx?id=100121)
  
  - **Quran Databases**:
    - [En-Qurancom JSON Translation](https://github.com/hablullah/data-quran/blob/master/word-translation/en-qurancom.json)
    - [Quran Dataset on Kaggle](https://www.kaggle.com/datasets/imrankhan197/the-quran-dataset)
    - [SearchTruth Quran Words](https://www.searchtruth.com/words.php)

### Phase 3: AI Integration
- **Objective**: 
  - Leverage Google AI to convert the matched Quranic words into hand gestures.
  - Train the model for better accuracy in gesture production.

### Phase 4: App/Website Development
- **Objective**: 
  - Develop the mobile app or website that features every surah with animated ASL hand gestures.
  - Include Arabic and English translations beneath each gesture for a complete learning experience.

### Phase 5: Community Feedback and Refinement
- **Objective**: 
  - Involve the deaf community in testing the app and provide feedback for improvements.
  - Refine the ASL translations to ensure accuracy and user satisfaction.

---

## Limitations

### Facial Expressions in ASL
Facial expressions in ASL carry important grammatical information, but they are often underrepresented in video-based translations. While it’s possible to use ASL without facial expressions, it may come across as "monotone" or "lacking inflection." Some ASL users, for various reasons, omit facial expressions but compensate by using hand movements to convey tonal information. This can be a challenge but is not insurmountable.

To address this, we plan to use phone vibrations in sync with the Quranic recitation to represent the tonal variations, offering an alternative way to convey meaning.

---

## How to Contribute

We encourage contributions to help us improve and expand the project. Whether you're a developer, data scientist, or part of the deaf community, your feedback and contributions are invaluable. Here's how you can contribute:

1. **Fork the Repository**: Clone the repo and start contributing to the codebase.
2. **Help with Data Collection**: Assist in gathering ASL video datasets or Quranic translation datasets.
3. **Test the App**: Help test the app once the ASL hand gesture animations are ready.
4. **Provide Feedback**: Deaf users can offer valuable feedback on the accuracy of translations and gestures.

## License

This project is licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.

You are free to:
- Copy, modify, distribute, and perform the work, even for commercial purposes.

As long as you:
- **Give appropriate credit** to the original creators by providing proper attribution.

For more information, see the full license details here: [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

## Contact

For any inquiries, please contact me at [abdullah.naim@duke.edu].
