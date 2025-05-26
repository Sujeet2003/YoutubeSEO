from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import streamlit as st
# from video_extraction import VideoExtraction

@st.cache_resource
def get_ollama_model():
    return ChatOllama(model="llava", temperature=0.7)

class Analysis:
    def __init__(self, ollama_llm):
        self.__ollama_llm = ollama_llm

    def __seo_response_schema(self):
        """
            Create a Structured Output for SEO Recommendations.
        """
        response_schema = [
            ResponseSchema(name="title", description="A list of title suggestion objects with 'rank', 'title' and 'reason' fields"),
            ResponseSchema(name="description", description="An SEO optimized video description between 400-500 words."),
            ResponseSchema(name="tags", description="A list of exactly 35 trending tags/hashtags."),
            ResponseSchema(name="timestamp", description="A list timestamp objects with 'time' and 'description' fields more the 5 timestamps of video.")   
        ]
        return StructuredOutputParser.from_response_schemas(response_schema)
    
    def seo_analysis(self, video_url: str, meta_data: dict, language: str='English'):
        """
            Runs a SEO Analysis using agents.
        """
        platform = meta_data.get('platform', 'Youtube')
        title = meta_data.get('title', '')
        transcript = meta_data.get('transcript', '')
        duration = meta_data.get('duration', 0)
        duration_in_minutes = duration // 60
        num_of_timestamps = max(6, min(duration_in_minutes // 5, 60))
        
        template1 = PromptTemplate(
            template="""
        You are a video content analyst specialized in understanding {platform} videos, their structure, and audience appeal.

        Analyze the {platform} video at {video_url} with the title: '{title}'.

        Based on the following details:
        - Transcript (if available): {transcript}
        - Description: {description}

        Provide your analysis **in a clear, structured format** in {language} language.

        ### Analysis Report

        **1. Video Summary**  
        - If transcript is available, generate the summary using it.  
        - If transcript is not available, generate summary from metadata.

        **2. Main Topics Covered (Minimum 5, up to 30):**  
        List them in bullet points.

        **3. Emotional Tone and Style:**  
        Describe how the content feels (e.g., motivational, educational, humorous, serious, technical).

        **4. Target Audience:**  
        Who is the video intended for? Include demographics and interests.

        **5. Content Structure and Flow:**  
        Explain how the content is organized from start to finish.

        ### Notes:
        - Your analysis should be in {language}.
        - If transcript is missing or unclear, rely on title and description.
        - Be concise yet complete in your analysis.
        """,
            input_variables=['platform', 'video_url', 'title', 'transcript', 'language', 'description']
        )

        analysis_chain = template1 | self.__ollama_llm
        analysis_response = analysis_chain.invoke({'platform': platform, 'video_url': video_url, 'title': title, 'transcript': transcript, 'description': meta_data['description'], 'language': language,})

        parser = self.__seo_response_schema()
        format_instructions = parser.get_format_instructions()

        # template2 = PromptTemplate(
        #     template="""
        #     You are an SEO specialist focusing on optimizing {platform} content for maximum discovery and engagement.

        #     Based on the analysis of a {platform} video titled "{title}":

        #     {analysis}

        #     Generate comprehensive SEO recommendations specifically for {platform} including:

        #     1. 5-7 alternative title suggestions ranked by SEO potential, each under 60 characters. Output format:
        #     "title": {{
        #         "0": {{"rank": 1, "title": "Alternative title 1"}},
        #         "1": {{"rank": 2, "title": "Alternative title 2"}},
        #         "2": {{"rank": 3, "title": "Alternative title 3"}}
        #     }}

        #     2. Exactly 35 trending tags or hashtags. Output format:
        #     "tags": {{
        #         "0": "tag1",
        #         "1": "tag2",
        #         "2": "tag3"
        #     }}

        #     3. A detailed and SEO-Optimized video description (500-1000 words) with:
        #         - A hook in the first 2-3 sentences
        #         - Value proposition
        #         - Key topics with keywords
        #         - Clear call-to-action
        #         - Paragraphs for readability

        #     4. Exactly {num_of_timestamps} timestamps, evenly distributed (duration: {duration} seconds). Output format:
        #     "timestamp": {{
        #         "0": {{"time": "00:00", "description": "Intro"}},
        #         "1": {{"time": "02:30", "description": "Key topic"}},
        #         "2": {{"time": "05:00", "description": "Outro"}}
        #     }}

        #     {format_instructions}

        #     Respond ONLY in VALID JSON.
        #     All content must be in {language}.
        #     """,
        #         input_variables=['platform', 'title', 'analysis', 'num_of_timestamps', 'duration', 'language'],
        #         partial_variables={'format_instructions': format_instructions}
        # )
        template2 = PromptTemplate(
            template="""
                You are an SEO specialist focusing on optimizing {platform} content for maximum discovery and engagement.

                Based on the detailed transcript analysis of a {platform} video titled "{title}", lasting approximately {duration} seconds:

                {analysis}

                Generate comprehensive SEO recommendations specifically for {platform} including:

                1. 7 alternative title suggestions ranked by SEO potential, each under 60 characters. Titles must be catchy, keyword-optimized, and diverse. 
                Output format:
                "title": {{
                    "0": {{"rank": 1, "title": "Alternative title 1"}},
                    "1": {{"rank": 2, "title": "Alternative title 2"}},
                    "2": {{"rank": 3, "title": "Alternative title 3"}},
                    "3": {{"rank": 4, "title": "Alternative title 4"}},
                    "4": {{"rank": 5, "title": "Alternative title 5"}},
                    "5": {{"rank": 6, "title": "Alternative title 6"}},
                    "6": {{"rank": 7, "title": "Alternative title 7"}}
                }}

                2. Exactly 35 trending tags or hashtags relevant to the video content.
                Output format:
                "tags": {{
                    "0": "tag1",
                    "1": "tag2",
                    "2": "tag3",
                    ...
                    "34": "tag35"
                }}

                3. A detailed and SEO-Optimized video description (500–1000 words) with:
                    - A hook in the first 2–3 sentences
                    - Clear value proposition
                    - Key discussion points and topics with proper keywords
                    - A strong call-to-action (CTA)
                    - Paragraphs for readability

                4. Generate {num_of_timestamps} **evenly distributed and content-aware timestamps** across the full video duration (≈{duration} seconds). Analyze the full transcript to identify major sections, topic shifts, and natural transitions.
                Output format:
                "timestamp": {{
                    "0": {{"time": "00:00", "description": "Intro"}},
                    "1": {{"time": "HH:MM", "description": "Next Key Topic"}},
                    ...
                    "{{last}}": {{"time": "HH:MM", "description": "Conclusion"}}
                }}

                {format_instructions}

                Respond ONLY in VALID JSON format.
                All content must be in {language}.
            """,
            input_variables=['platform', 'title', 'analysis', 'num_of_timestamps', 'duration', 'language'],
            partial_variables={'format_instructions': format_instructions}
        )

        recommendation_chain = template2 | self.__ollama_llm
        response = recommendation_chain.invoke({'platform': platform, 'title': title, 'analysis': str(analysis_response), 'num_of_timestamps': num_of_timestamps, 'duration': duration, 'language': language})

        try:
            return parser.parse(response.content)
        except Exception as e:
            print("Raw response:\n", response.content)
            raise ValueError(f"Error parsing response: {e}")



# v = VideoExtraction()
# url = "https://youtu.be/RYqJ5w-GrfM?si=dX9m85-ULKZ9X2Pf"

# platform = v.get_platform(url=url)
# if platform:
#     video_id = v.get_video_id(url=url)
#     if video_id is not None:
#         meta_data = v.get_meta_data(video_id=video_id)
#         # print(meta_data)
#     else:
#         print("Video Id is not valid, try again with correct youtube URL!")
# else:
#     print(f"Oops, seems like you have given url of other platform, please provide Youtube URL!")

# ollama_model = get_ollama_model()
# analysis = Analysis(ollama_llm=ollama_model)
# if meta_data:
#     result = analysis.seo_analysis(url, meta_data)
#     for key, value in result.items():
#         print(key, value)
#     print("Result type:", type(result))