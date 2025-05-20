from utils.video_extraction import VideoExtraction
from utils.analysis import Analysis, get_ollama_model
import streamlit as st
import os



LANGUAGES = ['English', 'Hindi', 'French', 'German', 'Spanish', 'Japanese', 'Russian', 'Arabic', 'Korean']

st.set_page_config(page_title="Youtube Video SEO Optimizer", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        h1 {
            text-align: center; 
        }
        
        # centered to the sidebar image
        .e1q5ojhd0 {
            display: flex;
            justify-content: center;    
        }
        
        selectbox {
            cursor: pointer;    
        }
        
        # Input URL Submit button
        div.stButton > button:first-child {
            background-color: #ff4b4b;
            color: white;
            padding: 0.75em 2em;
            font-size: 18px;
            font-weight: bold;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        div.stButton > button:first-child:hover {
            background-color: #e63e3e;
        }
#         .main-title {
#             font-size: 2.5rem;
#             color: #1E88E5;
#             margin-bottom: 1rem;    
#         }
#         .section-title {
#             font-size: 1.5rem;
#             color: #0D47A1;
#             margin-top: 1rem;    
#         }
#         .tag-pill {
#             background-color: #E3F2FD;
#             color: #1565C0;
#             padding: 5px 10px;
#             border-radius: 15px;
#             margin: 2px;
#             display: inline-block;    
#         }
#         .timestamp-card {
#             background-color: #2196F3;
#             padding: 10px;
#             border-radius: 5px;
#             margin-bottom: 5px;
#             color: #FFFFFF;  
#         }
#         .timestamp-card b {
#             color: #FF5252;
#             font-weight: bold;    
#         }
#         .stButton>button {
#             background-color: #1E88E5;
#             color: white;    
#         }
    </style>
""", unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.image("images/image-1.jpeg")
    st.title("API Configuration")
    openai_api_key = st.text_input("Open API Key", type="password", key="openai key")
    if openai_api_key:
        os.environ['OPENAI_API_KEY'] = openai_api_key
    
    st.divider()
    st.subheader("Language Settings")
    selected_language = st.selectbox("Select Language", LANGUAGES, index=0)

    st.subheader("Model Settings")
    model_options = st.selectbox(
        "Select AI Engine",
        ['OpenAI GPT-4', 'HuggingFace Model', 'Local Model'],
        index=2,
        help="Select any model with after entering appropriate API Key"   
    )

    st.divider()
    st.subheader("About")
    st.write('''
        This tool uses AI to generate Youtube SEO Recommendations for better user engagement.
    ''')

    st.divider()
    st.caption("Created with GenAI (LLMs), Langchain and Streamlit")


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
    st.session_state.meta_data = None

if 'video_url' not in st.session_state:
    st.session_state.video_url = None

if submit_button:
    if video_url:
        st.session_state.video_url = video_url
        try:
            video_extraction = VideoExtraction()
            ollama_model = get_ollama_model()
            analysis = Analysis(ollama_llm=ollama_model)
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

            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Video Details")
                if st.session_state.meta_data:
                    platform = st.session_state.meta_data.get('platform', 'Unknown')
                    title = st.session_state.meta_data['title']
                    st.markdown(platform)
                    st.markdown(title)
                # else:
                #     st.warning("Video metadata could not be retrieved.")
        except:
            raise