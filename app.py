from utils.video_extraction import VideoExtraction
from utils.analysis import Analysis
from utils.model_handler import get_ollama_model
import streamlit as st
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from utils.model_handler import HuggingFaceModel
load_dotenv()


api_token = None
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
            display: none;    
        }
            
        .e1lln2w82 {
            width: none;    
        }
               
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
    st.session_state.meta_data = None

if 'video_url' not in st.session_state:
    st.session_state.video_url = None

tab1, tab2 = st.tabs(['Video Info', 'SEO Recommendations'])

with tab1:
    if submit_button:
        if video_url:
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

                st.subheader("Video Informations")
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

                    st.write(f"""<p style="margin: 10px 0; font-size: 20px;"><strong>Title:</strong> <br> {title}</p>""", unsafe_allow_html=True)

                    st.write(f"""<p style="margin: 10px 0; font-size: 20px;"><strong>Creator: </strong> {author}</p>""", unsafe_allow_html=True)

                    st.write(f"""<p style="margin: 10px 0; font-size: 20px;"><strong>Duration: </strong> {duration} minute(s)</p>""", unsafe_allow_html=True)

                    st.write(f"""<p style="margin: 10px 0; font-size: 20px;"><strong>Views: </strong> {views}</p>""", unsafe_allow_html=True)

                    st.write(f"""<p style="margin: 10px 0; font-size: 20px;"><strong>Description:</strong> <br>  {description}</p>""", unsafe_allow_html=True)

                    # st.write(f"""<p style="margin: 10px 0; font-size: 20px;"><strong>Transcript: </strong><br> <p style="font-size: 16px;">{transcript[:500]}...</p> </p>""", unsafe_allow_html=True)

                    st.markdown(f"""
                    <p style="margin: 10px 0; font-size: 20px;"><strong>Transcript:</strong></p>
                    <p style="font-size: 16px;">{transcript[:500]}...</p>
                    """, unsafe_allow_html=True)

                    with st.expander("Read more"):
                        st.markdown(f"<p style='font-size: 16px;'>{transcript}</p>", unsafe_allow_html=True)
                    
                    st.image(thumbnail_url, width=600)
                else:
                    st.warning("Video metadata could not be retrieved.")
                                
            except:
                st.warning(f"Oops, some error occurred, try again...")

with tab2:
    st.header("SEO Recommendations")
    if st.session_state.meta_data:
        if st.button("Generate SEO Recommendations"):
            with st.spinner("Analyzing video and generating recommendations..."):
                try:
                    # ollama_model = get_ollama_model()
                    analysis = Analysis(llm=st.session_state.llm, is_local_model=is_local_model)
                    result = analysis.seo_analysis(video_url=st.session_state.video_url, meta_data=st.session_state.meta_data, language=selected_language)
                    st.session_state.analysis_result = result
                    st.session_state.analysis_complete = True
                except Exception as e:
                    st.error(f"Error generating recommendations: {e}")

    else:
        st.info("Please enter a valid video URL in the 'Video Info' tab first.")

    if st.session_state.analysis_complete and st.session_state.analysis_result:
        st.subheader("SEO Suggestions")
        st.write(st.session_state.analysis_result)