from utils.video_extraction import VideoExtraction
from utils.analysis import Analysis
from utils.model_handler import get_ollama_model
import streamlit as st
import os
from huggingface_hub import InferenceClient
from utils.model_handler import HuggingFaceModel
from utils.config import HUGGINGFACE_API_KEY


api_token = HUGGINGFACE_API_KEY
model = None
is_local_model = False

if "llm" not in st.session_state:
    st.session_state.llm = None


st.set_page_config(page_title="Youtube Video SEO Optimizer", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style> 
        div[data-baseweb="select"] > div {
            cursor: pointer;
        }
            
        svg {
            display: None;    
        }
            
        [data-baseweb="tab-list"] {
            justify-content: space-around !important;
        }
            
        .e1lln2w82 {
            width: none;    
        }
            
        .info-block {
            margin: 15px 0;
            padding: 10px 15px;
            border-radius: 10px;
            background-color: #f8f9fa;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .info-title {
            font-size: 20px;
            font-weight: 600;
            color: #6c63ff;
            margin-bottom: 5px;
        }
        .info-content {
            font-size: 18px;
            color: #000 !important;
        }
        .transcript-title {
            font-size: 20px;
            font-weight: 600;
            color: #ff6b6b;
            margin-top: 25px;
        }
        .transcript-snippet {
            font-size: 16px;
            color: #fff;
            margin-bottom: 15px;
        }
        
        /* Style paragraphs inside markdown */
                
        .description-content {
            color: black !important;    
        }

        /* Buttons Style */
        .erovr380 {
            width: 100% !important;
        }
        .e1mlolmg0 {
            display: flex;
            justify-content: center;
        }

        /* Heading */
        h1 {
            text-align: center; 
        }
        
        /* Sidebar image section centered */
        .e1q5ojhd0 {
            display: flex;
            justify-content: center;    
        }
        
        /* Youtube URL submit button setup */
        .st-emotion-cache-ovf5rk {
            width: 200px;    
        }
            
        /* Youtube Icon for platform */
        .platform {
            background: red;
            color: #fff !important;
            width: 130px;
            text-align: center;
            border-radius: 10px;    
        }
        
    </style>
""", unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.subheader("Model Settings")
    selected_model = st.selectbox(
        "Select AI Engine",
        ['Local Model', 'HuggingFace Model'],
        index=1,
        help="Select any model with after entering appropriate API Key"   
    )

    model = selected_model

    if model != "Local Model":
        st.title("API Configuration")
        api_key = st.text_input("API Key", type="password", key="API Key")
        submit_api_key = st.button("Submit API Key")
        if submit_api_key:
            if api_key:
                os.environ['HUGGING_FACE_TOKEN'] = api_key
                api_token = api_key
            else:
                api_token = os.environ['HUGGING_FACE_TOKEN']
    
    st.divider()
    st.subheader("Language Settings")
    LANGUAGES = ['English', 'Hindi']
    selected_language = st.selectbox("Select Language", LANGUAGES, index=0)

    st.divider()
    st.subheader("About")
    st.write('''
        This tool uses AI to generate Youtube SEO Recommendations for better user engagement.
    ''')

    st.divider()
    st.caption("Created with GenAI (LLMs), Langchain and Streamlit")

# Invoking the appropriate models
if model == 'Local Model':
    st.session_state.llm = get_ollama_model()
    is_local_model = True
else:
    if api_token:
        client = InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.3", token=api_token)
        st.session_state.llm = HuggingFaceModel(client)

# Main Content
st.title("Youtube SEO Optimizer")
st.write('''
    This tool uses AI to generate Youtube SEO Recommendations for better user engagement.
''')
video_url = st.text_input("Enter video URL here...", placeholder="https://www.youtube.com/watch?v=...")
submit_button = st.button("Enter")  

if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

if 'meta_data' not in st.session_state:
    st.session_state.meta_data = {}

if 'video_url' not in st.session_state:
    st.session_state.video_url = None

tab1, tab2 = st.tabs(['Video Info', 'SEO Recommendations'])

with tab1:
    if submit_button and video_url:
        st.session_state.video_url = video_url
        try:
            video_extraction = VideoExtraction()
            with st.spinner("Fetching video information..."):
                platform = video_extraction.get_platform(url=video_url)
                if platform:
                    video_id = video_extraction.get_video_id(url=video_url)
                    if video_id:
                        meta_data = video_extraction.get_meta_data(video_id=video_id)
                        if meta_data:
                            st.session_state.meta_data = meta_data
                        else:
                            st.warning("Could not extract video metadata.")
                    else:
                        st.warning("Oops, invalid Video ID. Try again!")
                else:
                    st.warning("Oops, invalid platform URL. Please use a YouTube URL.")
        except:
            st.warning(f"Oops, some error occurred, try again...")

    if st.session_state.meta_data:
        platform = st.session_state.meta_data.get('platform', 'Unknown')
        title = st.session_state.meta_data['title']
        description = st.session_state.meta_data.get('description')
        duration = st.session_state.meta_data.get('duration') // 60
        views = st.session_state.meta_data.get('views')
        author = st.session_state.meta_data.get('author')
        transcript = st.session_state.meta_data.get('transcript', "")
        thumbnail_url = st.session_state.meta_data.get('thumbnail_url')

        st.write(f"""<h4 class="platform">{platform}</h4>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-block">
            <div class="info-title">Title:</div>
            <div class="info-content">{title}</div>
        </div>
        """, unsafe_allow_html=True)

        # Creator
        st.markdown(f"""
        <div class="info-block">
            <div class="info-title">Creator:</div>
            <div class="info-content">{author}</div>
        </div>
        """, unsafe_allow_html=True)

        # Duration
        st.markdown(f"""
        <div class="info-block">
            <div class="info-title">Duration:</div>
            <div class="info-content">{duration} minute(s)</div>
        </div>
        """, unsafe_allow_html=True)

        # Views
        st.markdown(f"""
        <div class="info-block">
            <div class="info-title">Views:</div>
            <div class="info-content">{views}</div>
        </div>
        """, unsafe_allow_html=True)

        # Description
        st.markdown(f"""
        <div class="info-block">
            <div class="info-title">Description:</div>
            <div class="info-content description-content">{description}</div>
        </div>
        """, unsafe_allow_html=True)

        # Transcript snippet
        st.markdown(f"""
        <div class="transcript-title">Transcript:</div>
        <div class="transcript-snippet">{transcript[:500]}...</div>
        """, unsafe_allow_html=True)

        # Full transcript in expander
        with st.expander("Read more"):
            st.markdown(f"<div class='transcript-snippet'>{transcript}</div>", unsafe_allow_html=True)
        
        st.image(thumbnail_url, width=600)
    # else:
    #     st.warning("Video metadata could not be retrieved.")
                            

with tab2:
    # st.header("SEO Recommendations")
    st.markdown("""
        <style>
            /* Increase text size globally */
            .markdown-text-container {
                font-size: 18px !important;
            }

            /* Code block styles */
            .stMarkdown code {
                background-color: #c8e6c9 !important;
                color: blue !important;
                font-weight: 500 !important;
            }

            /* Subheader and heading styling */
            .stMarkdown h2, .stMarkdown h3, .stMarkdown h5 {
                color: #00796b !important;
                font-weight: bold !important;
            }

            /* === Tab content background === */
            div[data-baseweb="tab-panel"] {
                background-color: #00796b1f !important;  /* semi-transparent teal */
                padding: 20px !important;
                border-radius: 10px !important;
                margin-top: 10px !important;
            }

            /* Optional: Remove white background from default inner blocks */
            .stContainer {
                background-color: transparent !important;
            }
        </style>
    """, unsafe_allow_html=True)


    if st.session_state.meta_data:
        if st.button("Generate SEO Recommendations"):
            with st.spinner("Analyzing video and generating recommendations..."):
                try:
                    # ollama_model = get_ollama_model()
                    if not st.session_state.llm:
                        st.error(f"⚠️ Please enter API Key First")

                    analysis = Analysis(llm=st.session_state.llm, is_local_model=is_local_model)
                    result = analysis.seo_analysis(video_url=st.session_state.video_url, meta_data=st.session_state.meta_data, language=selected_language)
                    st.session_state.analysis_result = result
                    st.session_state.analysis_complete = True
                    # st.success("✅ SEO Recommendations generated successfully!")
                except Exception as e:
                    st.error(f"⚠️ Error generating recommendations: {e}")

    else:
        st.info("🔹 Please enter a valid video URL in the 'Video Info' tab first.")

    if st.session_state.analysis_complete and st.session_state.analysis_result:
        # st.subheader("SEO Suggestions")
        # st.write(st.session_state.analysis_result)
        if st.session_state.analysis_result:
            result = st.session_state.analysis_result

            title_tab, description_tab, tags_tab, timestamp_tab = st.tabs(['🏆 Titles', '📝 Description', '🔥 Tags/Hashtags', '⏱️ Timestamps'])

            with title_tab:
                st.subheader("🏆 Best Titles")
                for item in result['title'].values():
                    st.write(item['rank'], ": ", item['title'])

            with description_tab:
                st.subheader("📝 Description")
                st.markdown(f"\n{result['description']}\n")

            with tags_tab:
                st.subheader("🔥 Trending Tags / Hashtags")
                tags_data = result['tags']
                if isinstance(tags_data, dict):
                    hashtags = " ".join([f"`#{tag}`" for tag in tags_data.values()])
                elif isinstance(tags_data, list):
                    hashtags = " ".join([f"`#{tag}`" for tag in tags_data])
                else:
                    hashtags = ""
                st.markdown(hashtags)

            with timestamp_tab:
                st.subheader("⏱️ Video Chapters")
                for i, item in enumerate(result['timestamp'].values(), start=1):
                    st.markdown(f"`{item['time']}` — {item['description']}")
