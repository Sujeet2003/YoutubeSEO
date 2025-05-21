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
        return StructuredOutputParser.from_response_schemas(response_schemas=response_schema)
    
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
        
        tempelate1 = PromptTemplate(
            template="""
                You are a video content analyst specialized in understanding {platform} videos, their structure and audience appeal.

                Analyze the {platform} video at {video_url} with title '{title}'.

                Provide a detailed analysis including:
                1. Give a summary for this given transcript in {language}. The transcript give as: {transcript}
                2. The main topics which are likely covered in this video (at least 5)
                3. Emotional tone and style of the video
                4. Target audience demographics and interests
                5. Content structure and flow

                Your analysis should be in {language} language.
                Make reasonable assumptions based on the available infromation.
            """, input_variables=['platform', 'video_url', 'title', 'transcript', 'language']   
        )

        analysis_chain = tempelate1 | self.__ollama_llm
        analysis_response = analysis_chain.invoke({'platform': platform, 'video_url': video_url, 'title': title, 'transcript': transcript, 'language': language})

        parser = self.__seo_response_schema()
        format_instructions = parser.get_format_instructions()

        template2 = PromptTemplate(
            template="""
                You are an SEO specialist focusing on optimizing {platform} content for maximum discovery and engagement.

                Based on the analysis of a {platform} video titles '{title}': 

                {analysis}

                Generate comprehensive SEO recommendations specially for {platform} including:
                1. 5-7 alternative titles suggesations ranked by SEO potential each under 60 characters for youtube appropriate length for {platform}
                2. Exactly 35 trending tags/hashtags related to video content, ranked by potential traffic and relevance. For {platform}, optimize the tags according to platform best practices.
                3. Detailed and SEO-Optimized video description (400-500 words) that includes:
                    - An engaging hook in the first 2-3 sentences that entices viewers
                    - A clear value proposition explaining what viewer will gain
                    - Key topics covered with strategic keywords placement
                    - A strong call-to-action appropriate for {platform}
                    - Proper formatting with paragraph breaks for readability
                4. Exactly {num_of_timestamps} timestamps with descriptive labels evenly distributed throughout the video (duration: {duration} seconds)

                The output should be shtructured in JSON as example:
                'title': {{
                    List of titles
                }},
                'tags': {{
                    List of 35 tags/hashtags
                }},
                'description': {{
                    Description for this video
                }},
                'timestamp': {{
                    Timestamp should be like:
                    00:48: introduction
                    49:120: main content
                }}

                {format_instructions}

                All content should be in {language} language.
            """, input_variables=['platform', 'title', 'analysis', 'num_of_timestamps', 'duration', 'language'],
            partial_variables={'format_instructions': format_instructions}
        )

        recommendation_chain = template2 | self.__ollama_llm
        response = recommendation_chain.invoke({'platform': platform, 'title': title, 'analysis': analysis_response, 'num_of_timestamps': num_of_timestamps, 'duration': duration, 'language': language})

        return parser.parse(response.content)


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