import streamlit as st
import replicate
import os
import requests
from PIL import Image
from io import BytesIO

# Set up browser viewport parameters
st.set_page_config(page_title="Sports AI Sprite Sheet Generator", page_icon="🏅", layout="wide")

st.title("🏅 Sports AI Sprite Sheet Generator")
st.markdown("Generate full animation loops and structured sprite sheet grids using specialized AI models.")

# Sidebar Configuration for Security Tokens
st.sidebar.header("🔑 Authentication Setup")
api_token = st.sidebar.text_input("Replicate API Token", type="password", value=os.environ.get("REPLICATE_API_TOKEN", ""))

if not api_token:
    st.sidebar.warning("Please insert your Replicate API Token to start generating.")
else:
    os.environ["REPLICATE_API_TOKEN"] = api_token.strip()
    st.sidebar.success("API Token applied successfully!")

# Split Canvas Grid
col1, col2 = st.columns([1, 2])

with col1:
    st.header("🎨 Sprite Configuration")
    sport = st.selectbox("Select Sport Type", ["Football (Soccer)", "Basketball", "Skateboarding", "Tennis", "Baseball", "Running"])
    style = st.selectbox("Art Style Preset", ["8-Bit Retro Pixel Art", "16-Bit Side-scroller Arcade", "3D Low-Poly Render", "Vector Game Asset"])
    pose = st.selectbox("Initial Action Pose Loop", ["Idle / Standing", "Sprinting / Running", "Mid-Air Jump / Trick", "Action Strike / Kick"])
    custom_prompt = st.text_area("Custom Modifiers (Optional)", placeholder="e.g., wearing neon green shorts, flaming shoes, cyber helmet...")
    
    with st.expander("⚙️ Advanced AI Hyperparameters"):
        steps = st.slider("Inference Steps (Quality)", min_value=20, max_value=50, value=40, step=5)
        guidance = st.slider("Guidance Scale (Prompt Adherence)", min_value=5.0, max_value=15.0, value=10.0, step=0.5)

    generate_btn = st.button("✨ Craft Sprite Sheet", type="primary", disabled=not api_token)

with col2:
    st.header("🕹️ Generation Canvas")
    if generate_btn and api_token:
        # Optimization modifier strings targeting spritesheets
        style_keyword = "16-bit retro pixel art game sprite sheet character design, animation loop grid sequence" if "Pixel" in style or "Arcade" in style else "3d low poly video game asset sheet, isolated individual animation frame tiles"
        full_prompt = f"PixelartLSS, {sport.split(' ')[0].lower()} player executing {pose.split(' ')[0].lower()} movements, {style_keyword}, clean solid white background, game asset pack, {custom_prompt}"
        
        with st.spinner("⚡ AI engine is baking your sprite grid frames... (takes ~15 seconds)"):
            try:
                # Queries the dedicated multi-frame array generator model configuration
                output = replicate.run(
                    "cjwbw/sd_pixelart_spritesheet_generator:03e288270e5b93b235b18169d2678839b66500117e2b46b7f620389e1a96c002",
                    input={
                        "prompt": full_prompt,
                        "negative_prompt": "blurry, smooth photo, realistic texture, distorted borders, text, watermark, background gradient, shadows",
                        "num_outputs": 1,
                        "guidance_scale": guidance,
                        "num_inference_steps": steps
                    }
                )
                image_url = output[0] if isinstance(output, list) else output
                
                if image_url:
                    st.success("🎉 Sprite Sheet Generated Successfully!")
                    # Secure bytes rendering conversion directly on local RAM
                    response = requests.get(image_url)
                    img = Image.open(BytesIO(response.content))
                    st.image(img, caption=f"Generated Asset: {style} - {sport}", use_column_width=True)
                    
                    # Convert to downloadable output binary streams
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    st.download_button(label="💾 Download Full Sprite Sheet Asset", data=byte_im, file_name=f"sports_sprite_{sport.lower().split(' ')[0]}.png", mime="image/png")
                else:
                    st.error("AI engine returned an empty output configuration grid.")
            except Exception as e:
                st.error(f"Failed to query Replicate infrastructure: {str(e)}")
    else:
        st.info("Configure your athlete options on the left dashboard configuration deck and click generate to observe your animated asset asset outputs grid.")
