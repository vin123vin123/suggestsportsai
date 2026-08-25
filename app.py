import streamlit as st
import time
import requests
from PIL import Image
from io import BytesIO

# Set up browser viewport parameters
st.set_page_config(page_title="Sports AI Sprite Sheet Generator", page_icon="🏅", layout="wide")

st.title("🏅 Sports AI Sprite Sheet Generator")
st.markdown("Generate full animation loops and structured sprite sheet grids using specialized AI models.")

# Sidebar Configuration for Security Tokens
st.sidebar.header("🔑 Authentication Setup")
raw_api_token = st.sidebar.text_input("Replicate API Token", type="password", value="")

# Clean trailing line breaks, spaces or hidden tabs
api_token = raw_api_token.strip()

if not api_token:
    st.sidebar.warning("Please insert your Replicate API Token to start generating.")
else:
    st.sidebar.success("API Token applied successfully!")

# Split Canvas Grid
col1, col2 = st.columns(2)

with col1:
    st.header("🎨 Sprite Configuration")
    sport = st.selectbox("Select Sport Type", ["Football", "Basketball", "Skateboarding", "Tennis", "Baseball", "Running"])
    style = st.selectbox("Art Style Preset", ["8-Bit Retro Pixel Art", "16-Bit Side-scroller Arcade", "3D Low-Poly Render", "Vector Game Asset"])
    pose = st.selectbox("Initial Action Pose Loop", ["Front View (PixelartFSS)", "Back View (PixelartBSS)", "Left View (PixelartLSS)", "Right View (PixelartRSS)"])
    custom_prompt = st.text_area("Custom Modifiers (Optional)", placeholder="e.g., wearing neon green shorts, flaming shoes, cyber helmet...")
    
    with st.expander("⚙️ Advanced AI Hyperparameters"):
        steps = st.slider("Inference Steps (Quality)", min_value=20, max_value=50, value=45, step=5)
        guidance = st.slider("Guidance Scale (Prompt Adherence)", min_value=5.0, max_value=15.0, value=10.0, step=0.5)

    generate_btn = st.button("✨ Craft Sprite Sheet", type="primary", disabled=not api_token)

with col2:
    st.header("🕹️ Generation Canvas")
    if generate_btn and api_token:
        # Extract the specialized model token trigger based on selection (FSS, BSS, LSS, RSS)
        trigger_token = "PixelartLSS"
        if "Front" in pose: trigger_token = "PixelartFSS"
        elif "Back" in pose: trigger_token = "PixelartBSS"
        elif "Right" in pose: trigger_token = "PixelartRSS"

        # Build clean prompt matching the cjwbw/sd_pixelart_spritesheet_generator blueprint requirements
        full_prompt = f"{trigger_token}, {sport.lower()} player character sprite sheet animation grid, {style.lower()}, white background, {custom_prompt}"
        
        with st.spinner("⚡ Connecting directly via HTTP API... Baking your sprite grid frames..."):
            try:
                headers = {
                    "Authorization": f"Token {api_token}",
                    "Content-Type": "application/json"
                }
                
                # 1. Trigger the Generation Request Payload
                
payload = {
    "input": {
        "prompt": full_prompt,
        "negative_prompt": "blurry, smooth photo, photo realism, distorted borders, text, watermark, bad hands",
        "num_outputs": 1,
        "guidance_scale": guidance,
        "num_inference_steps": steps,
        "width": 512,
        "height": 512
    }
}

# The clean URL gateway that routes directly through Replicate's model slug pipeline
model_slug = "cjwbw/sd_pixelart_spritesheet_generator"
init_res = requests.post(
    f"https://replicate.com{model_slug}/predictions", 
    headers=headers, 
    json=payload
)

                
                if init_res.status_code == 401:
                    st.error("❌ Replicate rejected your token. Please double check that you copied the correct API Key from your Replicate dashboard settings tab!")
                elif init_res.status_code != 201:
                    st.error(f"❌ Server error ({init_res.status_code}): {init_res.text}")
                else:
                    prediction_data = init_res.json()
                    prediction_id = prediction_data["id"]
                    
                    # 2. Dynamic Status Polling Loop
                    status = "starting"
                    image_url = None
                    
                    while status in ["starting", "processing"]:
                        time.sleep(3) # Wait 3 seconds between polls
                        status_res = requests.get(f"https://replicate.com/{prediction_id}", headers=headers)
                        status_data = status_res.json()
                        status = status_data.get("status", "failed")
                        
                        if status == "succeeded":
                            # Pull output asset url
                            output = status_data.get("output")
                            image_url = output[0] if isinstance(output, list) else output
                            break
                        elif status == "failed":
                            st.error("AI engine failed to draw this layout combination.")
                            break
                    
                    # 3. Render Output Image directly on Canvas
                    if image_url:
                        st.success("🎉 Sprite Sheet Generated Successfully!")
                        img_response = requests.get(image_url)
                        img = Image.open(BytesIO(img_response.content))
                        st.image(img, caption=f"Generated Asset Pack Grid", use_container_width=True)
                        
                        # Download Button
                        buf = BytesIO()
                        img.save(buf, format="PNG")
                        st.download_button(label="💾 Download Full Sprite Sheet Asset", data=buf.getvalue(), file_name=f"sports_sprite_{sport.lower()}.png", mime="image/png")
                    else:
                        st.error("Could not extract image output URL from the server layout response.")
                        
            except Exception as e:
                st.error(f"Failed to query Replicate infrastructure: {str(e)}")
    else:
        st.info("Configure your athlete options on the left dashboard configuration deck and click generate to observe your animated asset outputs grid.")
