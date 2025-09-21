
# © 2025 Keumbok Sanghoe. All Rights Reserved.
import streamlit as st
import google.generativeai as genai
import os
import re
from PIL import Image
import io

# --- 기본 설정 ---
# Streamlit 페이지의 제목과 아이콘을 설정합니다.
st.set_page_config(page_title="오늘 뭐 먹지?", page_icon="🥗")

# --- API 키 설정 ---
# Streamlit의 Secrets 관리 기능을 사용하여 API 키를 안전하게 관리합니다.
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    # API 키 설정에 실패하면 사용자에게 오류 메시지를 보여주고 앱 실행을 중지합니다.
    st.error("API 키 설정에 실패했습니다. Streamlit Community Cloud의 Secrets에 GEMINI_API_KEY를 설정했는지 확인해주세요.")
    st.stop()
    
# --- AI 모델 설정 및 프롬프트 ---
# 텍스트 생성을 위한 모델과 이미지 생성을 위한 모델을 각각 설정합니다.
text_model = genai.GenerativeModel('gemini-1.5-flash')
image_model = genai.GenerativeModel('gemini-1.5-flash') # gemini-1.5-flash can also generate images

# AI에게 내릴 지시문(프롬프트)입니다. '치품송'에 대한 특별 규칙이 추가되었습니다.
prompt_template = """
당신은 '금복상회'의 수석 셰프로, 냉장고 속 재료로 만들 수 있는 요리를 추천하는 전문가입니다. 아래 규칙을 반드시 준수하여 답변해야 합니다.

### **'치품송' 특별 취급 규칙 (가장 중요!)**
만약 사용자가 입력한 재료에 '치품송'이 포함되어 있다면, 아래 규칙을 절대적으로 따라야 합니다. '치품송'은 새송이버섯 속에 치즈를 넣은 특별한 제품입니다.
1.  **조리법 제약:** '치품송'은 절대로 잘게 썰거나, 다지거나, 가닥가닥 찢으면 안 됩니다. 치즈가 모두 새어 나와 요리를 망치기 때문입니다.
2.  **허용되는 손질법:** '치품송'은 반드시 **통째로 사용**하거나, **길게 반으로 자르거나**, **0.5cm~1cm 두께로 동그랗게 써는** 방법만 사용해야 합니다.
3.  **추천 조리 방식:** 에어프라이어(5~7분)나 오븐을 사용하는 것이 가장 좋습니다. 예를 들어, '치품송을 동그랗게 썰어 올리브유와 후추를 뿌려 에어프라이어에 굽기'는 훌륭한 조리법입니다.
4.  **금지 조리 방식:** 전자레인지는 버섯이 제대로 익지 않고 치즈만 녹아버리므로 절대로 추천하지 마세요.
5.  위 규칙에 맞는 창의적인 레시피 2가지를 추천해주세요. (예: 치품송 꼬치구이, 치품송 스테이크, 치품송 샐러드 토핑 등)

### **일반 규칙**
1.  사용자가 입력한 재료 목록을 보고, 만들 수 있는 요리 2가지를 추천해주세요.
2.  각 요리는 아래 형식을 정확히 지켜서, 구분선(`---`)으로 나누어 답변해주세요.
3.  불필요한 인사나 서두 없이 바로 첫 번째 레시피부터 시작해주세요.

---
**요리 이름:** (여기에 요리 이름)
**총평:** (이 요리에 대한 1줄 요약 설명)
**입력한 재료:** (사용자가 입력한 재료 중 이 요리에 사용된 재료 목록)
**추가로 필요한 재료:** (남은 재료 외에 필요한 재료 목록, 없다면 '없음')
**간단한 레시피:**
1. (조리법 1)
2. (조리법 2)
3. (이하 생략)
"""

def generate_recipe_image(recipe_name):
    """요리 이름으로 이미지를 생성하는 함수"""
    try:
        # AI에게 요리 이미지를 생성하도록 요청합니다.
        image_prompt = f"A realistic and delicious photo of '{recipe_name}', minimalist style, bright background"
        response = image_model.generate_content(image_prompt, generation_config={"candidate_count": 1})
        
        # 응답에서 이미지 데이터를 가져옵니다.
        if response.parts:
            img_part = response.parts[0]
            if 'image' in img_part._resource.content_type:
                 # PIL Image 객체로 변환하여 반환합니다.
                img_bytes = img_part.inline_data.data
                return Image.open(io.BytesIO(img_bytes))
    except Exception as e:
        # 이미지 생성에 실패하면 콘솔에 오류를 출력하고 None을 반환합니다.
        print(f"이미지 생성 오류: {e}")
    return None

# --- 웹 앱 UI (화면) 구성 ---

st.title("🥗 오늘 뭐 먹지? (냉장고 비우기)")

st.write("냉장고에 있는 재료만으로, 금복상회 치품송 수석 셰프가 2가지 맛있는 요리를 추천해 드립니다!")

# 여러 줄의 재료를 입력받기 위해 text_area를 사용합니다.
ingredients_input = st.text_area("가지고 계신 재료를 쉼표(,)나 줄바꿈으로 구분해서 모두 입력해주세요.", placeholder="예: 치품송, 파프리카, 양파, 계란, 올리브유")

if st.button("나만의 레시피 추천받기! 🍽️"):
    if ingredients_input:
        with st.spinner("금복상회 수석 셰프가 레시피를 구상 중입니다... 🧑‍🍳"):
            # AI에게 보낼 최종 프롬프트를 완성합니다.
            full_prompt = prompt_template + "\n**입력 재료:** " + ingredients_input
            
            # AI 모델에게 요청을 보내고 응답을 받습니다.
            response = text_model.generate_content(full_prompt)
            
            # 응답 텍스트를 구분선('---')을 기준으로 나누어 각 레시피를 분리합니다.
            recipes = response.text.strip().split('---')
            
            # 복사할 전체 텍스트를 저장할 변수를 초기화합니다.
            full_recipe_text_for_copy = ""

            st.markdown("---")
            st.subheader("✨ AI 셰프의 추천 레시피 ✨")

            # 각 레시피를 순회하며 화면에 표시합니다.
            for recipe_str in recipes:
                if "요리 이름:" in recipe_str:
                    full_recipe_text_for_copy += recipe_str.strip() + "\n\n---\n\n"
                    # 정규표현식을 사용하여 요리 이름을 추출합니다.
                    match = re.search(r"요리 이름:\s*(.*)", recipe_str)
                    recipe_name = match.group(1).strip() if match else "요리"

                    # st.container()를 사용하여 각 레시피를 시각적으로 그룹화합니다.
                    with st.container(border=True):
                        # 요리 이름으로 이미지를 생성합니다.
                        recipe_image = generate_recipe_image(recipe_name)
                        if recipe_image:
                            # 이미지가 성공적으로 생성되면 화면에 표시합니다.
                            st.image(recipe_image, caption=f"AI가 생성한 '{recipe_name}' 이미지", use_column_width=True)
                        
                        # 레시피 텍스트를 화면에 표시합니다.
                        st.markdown(recipe_str.strip())
            
            # 전체 레시피를 복사할 수 있는 버튼을 추가합니다.
            if full_recipe_text_for_copy:
                st.code(full_recipe_text_for_copy, language=None)
                st.info("📋 위 텍스트 상자의 내용을 전체 복사하여 공유할 수 있습니다.")

    else:
        # 재료를 입력하지 않은 경우 경고 메시지를 표시합니다.
        st.warning("재료를 먼저 입력해주세요!")




