import streamlit as st
import google.generativeai as genai
import os
import re
from PIL import Image
import io

# --- 기본 설정 ---
st.set_page_config(page_title="오늘 뭐 먹지?", page_icon="🥗")

# --- API 키 설정 ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API 키 설정에 실패했습니다. Streamlit Community Cloud의 Secrets에 GEMINI_API_KEY를 설정했는지 확인해주세요.")
    st.stop()
    
# --- AI 모델 설정 및 프롬프트 ---
# [수정 1] 이전에 여기에 오타가 있었습니다. 아래처럼 수정해주세요.
text_model = genai.GenerativeModel('gemini-1.5-flash')
image_model = genai.GenerativeModel('gemini-1.5-flash')

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
        image_prompt = f"A realistic and delicious photo of '{recipe_name}', minimalist style, bright background"
        response = image_model.generate_content(image_prompt, generation_config={"candidate_count": 1})
        
        if response.parts:
            img_part = response.parts[0]
            if 'image' in img_part._resource.content_type:
                img_bytes = img_part.inline_data.data
                return Image.open(io.BytesIO(img_bytes))
    except Exception as e:
        print(f"이미지 생성 오류: {e}")
    return None

# --- 웹 앱 UI (화면) 구성 ---

# [수정 2] 기존의 st.image(...) 한 줄을 지우고, 아래의 코드로 완전히 교체합니다.
# -------------------------------------------------------------------------

# 1. 판매 페이지(스마트스토어) 주소를 여기에 정확하게 입력하세요.
smart_store_url = "https://smartstore.naver.com/chipumsong"

# 2. GitHub에 있는 이미지 주소입니다.
image_url = "https://raw.githubusercontent.com/shinsun4866-droid/cheepoom/main/choopoom.jpg" 

# 3. st.markdown과 HTML을 사용하여 클릭 가능한 이미지를 만듭니다.
# <a> 태그(링크)로 <img> 태그(이미지)를 감싸서 링크를 만듭니다.
# target="_blank"는 새 탭에서 링크가 열리도록 합니다.
st.markdown(f"""
<a href="{smart_store_url}" target="_blank" title="치품송 구매 페이지로 이동">
    <img src="{image_url}" alt="치품송 구매하러 가기" style="width: 100%; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
</a>
""", unsafe_allow_html=True)
st.caption("▲ 금복상회 치품송 공식 스토어")


# 메인 제목과 부제목은 그대로 유지합니다.
st.title("🥗 오늘 뭐 먹지?")
st.markdown("<h4>🌱 있는 재료로 뚝딱!</h4>", unsafe_allow_html=True)
st.markdown("---")


st.write("금복상회 치품송이 제안하는 제로웨이스트 쿠킹앱입니다. 냉장고에 남은 재료를 입력하면 오늘의 한 끼를 추천,추가재료와 조리법을 알려 드립니다!")
ingredients_input = st.text_area("가지고 계신 재료를 쉼표(,)나 줄바꿈으로 구분해서 모두 입력해주세요. 레시피는 권장 예시이며, 개인 기호 재료에 상태에 따라 조절 하시기바랍니다.", placeholder="예: 치품송, 파프리카, 양파, 계란, 올리브유")

if st.button("추천 레시피 받기 🍽️"):
    if ingredients_input:
        with st.spinner("금복상회 수석 셰프가 레시피를 구상 중입니다... 🧑‍🍳"):
            full_prompt = prompt_template + "\n**입력 재료:** " + ingredients_input
            response = text_model.generate_content(full_prompt)
            recipes = response.text.strip().split('---')
            full_recipe_text_for_copy = ""

            st.markdown("---")
            st.subheader("✨ 수석 셰프 추천요리 ✨")

            for recipe_str in recipes:
                if "요리 이름:" in recipe_str:
                    clean_recipe_str = recipe_str.strip()
                    full_recipe_text_for_copy += clean_recipe_str + "\n\n---\n\n"
                    match = re.search(r"요리 이름:\s*(.*)", clean_recipe_str)
                    recipe_name = match.group(1).strip() if match else "요리"

                    with st.container(border=True):
                        recipe_image = generate_recipe_image(recipe_name)
                        if recipe_image:
                            st.image(recipe_image, caption=f"AI가 생성한 '{recipe_name}' 이미지", use_column_width=True)
                        st.markdown(clean_recipe_str)
            
            if full_recipe_text_for_copy:
                st.markdown("---")
                st.info("📋 아래 상자 안의 텍스트를 복사해서 공유하세요!")
                st.code(full_recipe_text_for_copy.strip(), language=None)

    else:
        st.warning("재료를 먼저 입력해주세요!")


