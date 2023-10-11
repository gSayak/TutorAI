from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from bardapi import Bard
import streamlit as st
from googletrans import Translator

def getNonTranscriptVideo(youtube_video):
    YouTube(youtube_video).streams\
          .filter(only_audio = True, file_extension= 'mp4') \
          .first() \
          .download(filename = 'ytaudio.mp4') \
    # pipe = pipeline("automatic-speech-recognition",
    #                 model="openai/whisper-large-v2")
    # audio_text = pipe(audio)

    return 1


def getTrasnscriptVideo(video_id):
    try:
        YouTubeTranscriptApi.get_transcript(video_id)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        result = ""
        for i in transcript:
            result += ' ' + i['text']
    except Exception as e:
        return 'fail', 'Could not extract transcript. Please try a different video.'
    return result


def getSummary(summary):
    pipe = pipeline("summarization", model="facebook/bart-large-cnn")
    summarized = pipe(summary, max_length=130, min_length=30)
    # if summarized and isinstance(summarized[0], dict) and 'summary_text' in summarized[0]:
    #     return summarized[0]['summary_text']
    # else:
    #     return "Summary not available"
    return summarized[0]['summary_text']





def generateCourse(transcript):
    secret_api_key = st.secrets["BARD_API_KEY"]
    headers = {
        "authorization": secret_api_key,
        "content-type": "application/json"
    }
    bard = Bard(token=headers['authorization'])
    prompt = f"Act like a teacher, now create a study course based on this transcript: {transcript}, include the 1. learning objectives, 2. the course outline and 3. the course content divided in it's respective sections along with 4. a few important questions"
    result = bard.get_answer(prompt)['content']

    return result

def askQuestions(transcript, question):
    pipe = pipeline("question-answering", model="deepset/roberta-base-squad2")
    # translator = Translator()
    # questionEn = translator.translate(question, dest='en').text
    result = pipe(question=question, context=transcript)
    return result['answer']

# print(getSummary(getTrasnscriptVideo("NiKtZgImdlY")))

def main():
    st.set_page_config(page_title="Tutor AI", page_icon="📖", layout = 'wide',)
    st.header("Tutor AI: Learn any topic from YouTube videos ")
    youtube_video = st.text_input("Enter a YouTube video link:")
    if youtube_video:
        st.video(youtube_video)
        video_id = youtube_video.split("=")[1]
        # st.write(f"You entered: {video_id}")
        transcript = getTrasnscriptVideo(video_id)
        with st.expander("Course Outline"):
            st.write(generateCourse(transcript))

        with st.expander("Course Summary"):
            st.write(getSummary(transcript))
        question = st.text_input("Ask a question about the video:")
        if question:
            with st.expander("Answer"):
                st.write(askQuestions(transcript, question))


if __name__ == "__main__":
    main()





