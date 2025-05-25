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
        minutes = duration // 60
        num_of_timestamps = min(15, max(5, minutes // 2)) if minutes > 0 else 5
        
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
        #         You are an SEO specialist focusing on optimizing {platform} content for maximum discovery and engagement.

        #         Based on the analysis of a {platform} video titles '{title}': 

        #         {analysis}

        #         Generate comprehensive SEO recommendations specially for {platform} including:
        #         1. 5-7 alternative titles suggestions ranked by SEO potential each under 60 characters for youtube appropriate length for {platform}. The output should be structured in JSON like:
        #         Atleast minimum of 5 List of titles like:
        #         'title': {{
        #             0:{{
        #                 "rank":1
        #                 "title":"Pink Lips Full Video Song | Sunny Leone | Hate Story 2 | Meet Bros Anjjan Feat Khushboo Grewal"
        #             }}
        #             1:{{
        #                 "rank":2
        #                 "title":"Sunny Leone's Sensual Dance in Pink Lips"
        #             }}
        #             2:{{
        #                 "rank":3
        #                 "title":"Hate Story 2 Soundtrack: Pink Lips Full Video Song"
        #             }}
        #             3:{{
        #                 "rank":4
        #                 "title":"Meet Bros Anjjan & Sunny Leone Collaboration - Pink Lips"
        #             }}
        #             4:{{
        #                 "rank":5
        #                 "title":"Pink Lips Song: Love, Longing & Romance"
        #             }}
        #         }}
        #         2. Exactly 35 trending tags/hashtags related to video content, ranked by potential traffic and relevance. For {platform}, optimize the tags according to platform best practices. Few Examples of tags and hashtags are as:
        #         'tags': {{
        #             0: "Pink Lips Song"
        #             1: "Sunny Leone"
        #             2: "Meet Bros Anjjan"
        #             3: "Khushboo Grewal"
        #             4: "Hate Story 2"
        #             5: "Bollywood music video"
        #             6: "love song"
        #             7: "romantic song"
        #             8: "dance"
        #         }}
        #         3. Detailed and SEO-Optimized video description (400-500 words) that includes:
        #             - An engaging hook in the first 2-3 sentences that entices viewers
        #             - A clear value proposition explaining what viewer will gain
        #             - Key topics covered with strategic keywords placement
        #             - A strong call-to-action appropriate for {platform}
        #             - Proper formatting with paragraph breaks for readability
        #         4. Exactly {num_of_timestamps} timestamps with descriptive labels evenly distributed throughout the video (duration: {duration} seconds). The output should look like:
        #         Give atleast 5 timestamp as minimum number (maximum you can go as much you want after analysing the full transcript from where you can give more timestamps) which should be like:
        #         'timestamp': {{
        #             0:{{
        #                 "time":"00:00"
        #                 "description":"Introduction of the song and its performers"
        #             }}
        #             1:{{
        #                 "time":"02:19"
        #                 "description":"Main content of the music video with Sunny Leone's dance performance"
        #             }}
        #             2:{{
        #                 "time":"05:20"
        #                 "description":"Lyrics and storytelling in the song"
        #             }}
        #             3:{{
        #                 "time":"08:42"
        #                 "description":"Climax of the song and its performers"
        #             }}
        #         }}

        #         {format_instructions}

        #         All content should be in {language} language.
        #     """, input_variables=['platform', 'title', 'analysis', 'num_of_timestamps', 'duration', 'language'],
        #     partial_variables={'format_instructions': format_instructions}
        # )

        template2 = PromptTemplate(
            template="""
            You are an SEO specialist focusing on optimizing {platform} content for maximum discovery and engagement.

            Based on the analysis of a {platform} video titled "{title}":

            {analysis}

            Generate comprehensive SEO recommendations specifically for {platform} including:

            1. 5-7 alternative title suggestions ranked by SEO potential, each under 60 characters. Output format:
            "title": {{
                "0": {{"rank": 1, "title": "Alternative title 1"}},
                "1": {{"rank": 2, "title": "Alternative title 2"}},
                "2": {{"rank": 3, "title": "Alternative title 3"}}
            }}

            2. Exactly 35 trending tags or hashtags. Output format:
            "tags": {{
                "0": "tag1",
                "1": "tag2",
                "2": "tag3"
            }}

            3. A detailed and SEO-Optimized video description (500-1000 words) with:
                - A hook in the first 2-3 sentences
                - Value proposition
                - Key topics with keywords
                - Clear call-to-action
                - Paragraphs for readability

            4. Exactly {num_of_timestamps} timestamps, evenly distributed (duration: {duration} seconds). Output format:
            "timestamp": {{
                "0": {{"time": "00:00", "description": "Intro"}},
                "1": {{"time": "02:30", "description": "Key topic"}},
                "2": {{"time": "05:00", "description": "Outro"}}
            }}

            {format_instructions}

            Respond ONLY in VALID JSON.
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