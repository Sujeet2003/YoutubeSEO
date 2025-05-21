from utils.video_extraction import VideoExtraction
from utils.analysis import Analysis, get_ollama_model
import streamlit as st
import os



LANGUAGES = ['English', 'Hindi']

st.set_page_config(page_title="Youtube Video SEO Optimizer", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style> 
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
    st.image("images/image-1.jpeg")
    st.title("API Configuration")
    openai_api_key = st.text_input("Open API Key", type="password", key="openai key")
    if openai_api_key:
        os.environ['OPENAI_API_KEY'] = openai_api_key
    
    st.divider()
    st.subheader("Language Settings")
    selected_language = st.selectbox("Select Language", LANGUAGES, index=0)

    st.subheader("Model Settings")
    selected_model = st.selectbox(
        "Select AI Engine",
        ['Local Model', 'HuggingFace Model'],
        index=1,
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
                    ollama_model = get_ollama_model()
                    analysis = Analysis(ollama_llm=ollama_model)
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