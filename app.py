
# © 2025 Keumbok Sanghoe. All Rights Reserved.
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="냉장고 비우는 셰프",
    page_icon="🧑‍🍳"
)

# --- API 키 설정 ---
# 이 부분은 Streamlit의 Secrets 관리 기능을 사용하는 것이 가장 안전합니다.
# https://docs.streamlit.io/library/advanced-features/secrets-management
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("API 키를 설정해주세요. Streamlit의 'Secrets'에 GEMINI_API_KEY를 등록해야 합니다.")
    st.stop()

# --- 모델 초기화 ---
text_model = genai.GenerativeModel('gemini-1.5-flash')
image_generation_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')

# --- 앱 제목 아이디어 ---
# st.title("🧑‍🍳 냉장고 비우는 셰프")
# st.title("🍳 오늘의 재료, 내일의 요리")
# st.title("🤔 뭐 해먹지? AI에게 물어보세요")


# --- 메인 앱 UI 구성 ---
st.title("🧑‍🍳 냉장고 비우는 셰프")
st.write("집에 있는 재료를 알려주시면, AI 셰프가 멋진 요리를 추천해 드립니다.")

ingredients_input = st.text_area(
    "가지고 있는 재료를 쉼표(,)로 구분해서 모두 입력해주세요.",
    placeholder="예: 돼지고기, 오래된 김치, 두부, 양파, 대파"
)

if st.button("요리 추천받기! 🍽️"):
    if ingredients_input:
        # --- 1. 텍스트 레시피 생성 ---
        with st.spinner("AI 셰프가 레시피를 구상하는 중... 🍳"):
            # 이전 단계에서 최종 수정한 지시문을 여기에 그대로 사용합니다.
            prompt = f"""
            당신은 레시피 생성 AI입니다. 사용자가 입력한 재료를 기반으로, 두 가지의 서로 다른 레시피를 생성해주세요.

            **매우 중요한 규칙:**
            - 어떠한 서론이나 마무리 멘트도 없이, 즉시 첫 번째 레시피로 시작해야 합니다.
            - 두 레시피는 오직 '---'만 있는 한 줄로 구분해야 합니다.
            - 각 레시피는 아래의 형식을 정확히 따라야 합니다.

            **[요리 이름]**
            (여기에 요리 이름)

            **[준비할 재료]**
            - **입력한 재료:** {ingredients_input}
            - **추가 재료:** (여기에 추가로 필요한 재료)

            **[조리법]**
            1. (조리법 1)
            2. (조리법 2)
            3. (조리법 3)
            """
            try:
                response = text_model.generate_content(prompt)
                full_recipe_text = response.text
            except Exception as e:
                st.error(f"레시피 생성 중 오류가 발생했습니다: {e}")
                st.stop()

        st.markdown("---")
        st.subheader("✨ AI 셰프의 추천 요리 ✨")
        
        # --- 2. 결과 파싱 및 개별 레시피 표시 ---
        recipes = full_recipe_text.split("\n---\n")
        
        for recipe_text in recipes:
            recipe_text = recipe_text.strip()
            if not recipe_text:
                continue

            # 이미지 생성을 위해 요리 이름 추출
            dish_name = "요리" # 기본값
            try:
                lines = recipe_text.split('\n')
                for i, line in enumerate(lines):
                    if "[요리 이름]" in line and i + 1 < len(lines):
                        dish_name = lines[i+1].strip()
                        break
            except Exception:
                pass

            # --- 3. 요리 이미지 생성 및 표시 ---
            with st.spinner(f"'{dish_name}'의 이미지를 만드는 중... 🎨"):
                try:
                    # 이미지 생성을 위한 프롬프트
                    image_prompt = f"A delicious looking, realistic photo of '{dish_name}'. Plated beautifully on a clean, simple background. If a photo is difficult, a high-quality, appetizing illustration is also good."
                    
                    img_response = image_generation_model.generate_content(
                        image_prompt,
                        generation_config={'responseModalities': ['IMAGE']}
                    )
                    
                    # Base64 데이터를 이미지로 변환
                    img_data_b64 = img_response.candidates[0].content.parts[0].inline_data.data
                    img_bytes = base64.b64decode(img_data_b64)
                    img = Image.open(io.BytesIO(img_bytes))
                    
                    st.image(img, caption=f"AI가 생성한 '{dish_name}' 이미지", use_column_width=True)
                except Exception:
                    # 이미지 생성 실패 시, 사용자에게 오류 메시지를 보여주지 않고 그냥 넘어갑니다.
                    pass

            # 요청하신 '한 틀' 안에 레시피 내용을 표시
            with st.container(border=True):
                st.markdown(recipe_text)
            
            st.write("") # 레시피 간 간격

        # --- 4. 전체 내용 복사 기능 ---
        st.markdown("---")
        st.subheader("📋 전체 레시피 복사하기")
        st.code(full_recipe_text, language="text")
        st.info("위 박스 오른쪽 상단의 아이콘을 누르면 추천된 모든 레시피가 복사됩니다.")

    else:
        st.warning("먼저 재료를 입력해주세요!")
