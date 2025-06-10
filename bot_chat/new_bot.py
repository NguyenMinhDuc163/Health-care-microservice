# save as app.py
import streamlit as st
import json
import re
from difflib import SequenceMatcher
import random

# Configure page
st.set_page_config(
    page_title="COVID-19 Healthcare Assistant",
    page_icon="🦠",
    layout="wide"
)


# Load knowledge base
@st.cache_data
def load_knowledge_base():
    try:
        # Load all knowledge bases
        knowledge_bases = {}
        
        # Load COVID-19 knowledge base
        with open('data/covid.json', 'r', encoding='utf-8') as f:
            covid_kb = json.load(f)
            knowledge_bases["covid19"] = covid_kb["covid19_knowledge_base"]
            
        # Load Cold knowledge base
        with open('data/cold.json', 'r', encoding='utf-8') as f:
            cold_kb = json.load(f)
            knowledge_bases["cold"] = cold_kb
            
        # Load Allergy knowledge base
        with open('data/allergy.json', 'r', encoding='utf-8') as f:
            allergy_kb = json.load(f)
            knowledge_bases["allergy"] = allergy_kb
            
        # Load Flu knowledge base
        with open('data/flu.json', 'r', encoding='utf-8') as f:
            flu_kb = json.load(f)
            knowledge_bases["flu"] = flu_kb
            
        return knowledge_bases
    except FileNotFoundError as e:
        st.error(f"⚠️ Không tìm thấy file knowledge base: {str(e)}")
        return None
    except json.JSONDecodeError:
        st.error("⚠️ Lỗi đọc file JSON. Vui lòng kiểm tra cú pháp file.")
        return None


# Similarity function for fuzzy matching
def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# Check for emergency keywords
def is_emergency(text):
    emergency_keywords = [
        "khó thở nghiêm trọng", "đau ngực", "lú lẫn", "môi xanh",
        "mất ý thức", "cấp cứu", "nguy kịch", "nghiêm trọng"
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in emergency_keywords)


# COVID-19 symptom analysis
def analyze_covid_symptoms(text):
    symptoms = {
        "sốt": ["sốt", "nóng người", "ớn lạnh"],
        "ho": ["ho", "ho khan", "ho có đờm"],
        "đau họng": ["đau họng", "rát họng", "khó nuốt"],
        "khó thở": ["khó thở", "thở khó", "ngạt thở"],
        "mệt mỏi": ["mệt", "mệt mỏi", "kiệt sức"],
        "đau đầu": ["đau đầu", "nhức đầu"],
        "mất vị giác": ["mất vị", "không cảm nhận vị"],
        "mất khứu giác": ["mất mùi", "không ngửi được"]
    }

    detected_symptoms = []
    text_lower = text.lower()

    for symptom, keywords in symptoms.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_symptoms.append(symptom)

    return detected_symptoms


# Risk assessment based on symptoms
def assess_covid_risk(symptoms):
    if not symptoms:
        return "thấp", 0.2

    high_risk_symptoms = ["khó thở", "đau ngực", "sốt cao"]
    medium_risk_symptoms = ["sốt", "ho", "đau họng"]

    risk_score = 0
    for symptom in symptoms:
        if any(hrs in symptom for hrs in high_risk_symptoms):
            risk_score += 0.4
        elif any(mrs in symptom for mrs in medium_risk_symptoms):
            risk_score += 0.2
        else:
            risk_score += 0.1

    if risk_score >= 0.6:
        return "cao", min(risk_score, 0.95)
    elif risk_score >= 0.3:
        return "trung bình", risk_score
    else:
        return "thấp", risk_score


def format_allergy_info(info, specific_symptom=None):
    if isinstance(info, dict):
        if 'common_symptoms' in info:
            formatted = ""
            if specific_symptom:
                # Tách triệu chứng thành các từ riêng lẻ
                symptom_words = specific_symptom.lower().split()
                found_system = None
                found_symptoms = []
                related_symptoms = []

                # Tìm kiếm trong các hệ thống
                for system in info['common_symptoms']:
                    for symptom in system['symptoms']:
                        symptom_lower = symptom.lower()
                        # Kiểm tra xem có từ khóa nào trong triệu chứng cụ thể khớp với triệu chứng trong hệ thống không
                        if any(word in symptom_lower for word in symptom_words):
                            found_system = system
                            found_symptoms.append(symptom)
                        elif any(word in symptom_lower for word in symptom_words):
                            related_symptoms.append(symptom)

                if found_system:
                    formatted += f"**Triệu chứng '{specific_symptom}' có thể liên quan đến hệ thống {found_system['system']}:**\n\n"
                    
                    # Thêm thông tin về triệu chứng chính
                    formatted += "**Triệu chứng chính:**\n"
                    for symptom in found_symptoms:
                        formatted += f"- {symptom}\n"
                    formatted += "\n"

                    # Thêm thông tin về các triệu chứng liên quan
                    if related_symptoms:
                        formatted += "**Các triệu chứng liên quan có thể gặp:**\n"
                        for symptom in related_symptoms:
                            formatted += f"- {symptom}\n"
                        formatted += "\n"

                    # Thêm thông tin về các triệu chứng khác của hệ thống
                    formatted += f"**Các triệu chứng khác của hệ thống {found_system['system']}:**\n"
                    for symptom in found_system['symptoms']:
                        if symptom not in found_symptoms and symptom not in related_symptoms:
                            formatted += f"- {symptom}\n"
                    formatted += "\n"

                    # Thêm thông tin về điều trị nếu có
                    if 'approaches' in info.get('treatment', {}):
                        formatted += "**Các phương pháp điều trị có thể áp dụng:**\n"
                        for approach in info['treatment']['approaches']:
                            formatted += f"- {approach['method']}: {approach['description']}\n"
                else:
                    formatted = f"Không tìm thấy thông tin cụ thể về triệu chứng '{specific_symptom}'. "
                    formatted += "Dưới đây là các triệu chứng dị ứng phổ biến:\n\n"
                    for system in info['common_symptoms']:
                        formatted += f"**{system['system']}:**\n"
                        for symptom in system['symptoms']:
                            formatted += f"- {symptom}\n"
                        formatted += "\n"
            else:
                formatted = "**Triệu chứng dị ứng theo hệ thống:**\n\n"
                for system in info['common_symptoms']:
                    formatted += f"**{system['system']}:**\n"
                    for symptom in system['symptoms']:
                        formatted += f"- {symptom}\n"
                    formatted += "\n"
            
            if 'note' in info:
                formatted += f"*Lưu ý: {info['note']}*\n"
            return formatted
    return str(info)

def format_flu_info(info):
    if isinstance(info, dict):
        formatted = ""
        if 'common_symptoms' in info:
            formatted += "**Triệu chứng phổ biến:**\n"
            for symptom in info['common_symptoms']:
                formatted += f"- {symptom}\n"
            formatted += "\n"
        if 'less_common_symptoms' in info:
            formatted += "**Triệu chứng ít gặp hơn:**\n"
            for symptom in info['less_common_symptoms']:
                formatted += f"- {symptom}\n"
            formatted += "\n"
        if 'duration' in info:
            formatted += f"**Thời gian bệnh:** {info['duration']}\n\n"
        if 'distinction_from_common_cold' in info:
            formatted += f"**Phân biệt với cảm lạnh:** {info['distinction_from_common_cold']}\n"
        return formatted
    return str(info)

def format_cold_info(info):
    if isinstance(info, dict):
        formatted = ""
        if 'definition' in info:
            formatted += f"{info['definition']}\n\n"
        if 'symptoms' in info:
            formatted += "**Triệu chứng:**\n"
            for symptom in info['symptoms']:
                formatted += f"- {symptom}\n"
            formatted += "\n"
        if 'treatment' in info:
            formatted += "**Điều trị:**\n"
            for treatment in info['treatment']:
                formatted += f"- {treatment}\n"
        return formatted
    return str(info)

def format_covid_info(info):
    if isinstance(info, dict):
        formatted = ""
        if 'question' in info and 'answer' in info:
            formatted += f"{info['answer']}\n"
        return formatted
    return str(info)

# Find best matching answer from knowledge base
def find_best_answer(user_input, kb):
    if not kb:
        return None, None, []

    best_match = None
    best_score = 0
    matched_disease = None
    detected_symptoms = []

    # Kiểm tra xem có phải câu hỏi về triệu chứng cụ thể không
    symptom_keywords = ["bị", "có", "triệu chứng", "dấu hiệu", "biểu hiện", "đau", "ngứa", "sưng", "nổi", "mẩn", "lạnh", "sốt", "ho"]
    specific_symptom = None
    
    # Tìm từ khóa triệu chứng trong câu hỏi
    for keyword in symptom_keywords:
        if keyword in user_input.lower():
            # Tách từ sau từ khóa để lấy triệu chứng
            parts = user_input.lower().split(keyword)
            if len(parts) > 1:
                # Lấy phần còn lại của câu làm triệu chứng
                specific_symptom = parts[1].strip()
                # Loại bỏ các từ không cần thiết
                specific_symptom = specific_symptom.replace("là gì", "").replace("?", "").strip()
                break

    # Tìm kiếm trong tất cả các knowledge base
    disease_scores = {}
    disease_matches = {}
    disease_symptoms = {}

    # COVID-19
    if "covid19" in kb:
        covid_score = 0
        covid_match = None
        covid_symptoms = []
        
        covid_categories = kb["covid19"]["categories"]
        for category_key, category in covid_categories.items():
            for item in category["data"]:
                # Check intent matching
                for intent in category.get("intent", []):
                    if intent.lower() in user_input.lower():
                        score = similarity(user_input, intent)
                        if score > covid_score:
                            covid_score = score
                            covid_match = item

                # Check question similarity
                question_score = similarity(user_input, item["question"])
                if question_score > covid_score:
                    covid_score = question_score
                    covid_match = item

                # Check keywords
                for keyword in item.get("keywords", []):
                    if keyword.lower() in user_input.lower():
                        keyword_score = similarity(user_input, keyword) * 0.8
                        if keyword_score > covid_score:
                            covid_score = keyword_score
                            covid_match = item

        # Analyze COVID-19 symptoms
        symptoms = analyze_covid_symptoms(user_input)
        if symptoms:
            covid_symptoms = symptoms
            covid_score += 0.2  # Tăng điểm nếu phát hiện triệu chứng

        disease_scores["covid19"] = covid_score
        disease_matches["covid19"] = covid_match
        disease_symptoms["covid19"] = covid_symptoms

    # Cold
    if "cold" in kb:
        cold_score = 0
        cold_match = None
        cold_symptoms = []
        
        for intent_type, intents in kb["cold"]["chatbot_intents"].items():
            for intent in intents:
                if intent.lower() in user_input.lower():
                    for category_key, category in kb["cold"]["categories"].items():
                        if intent_type in category_key:
                            response = {
                                "question": f"Thông tin về {intent_type} của bệnh cảm lạnh",
                                "answer": format_cold_info(category)
                            }
                            score = similarity(user_input, intent)
                            if score > cold_score:
                                cold_score = score
                                cold_match = response

        # Analyze cold symptoms
        cold_symptom_list = ["sổ mũi", "nghẹt mũi", "đau họng", "ho", "hắt hơi", "đau đầu nhẹ", "sốt nhẹ", "lạnh", "ớn lạnh"]
        for symptom in cold_symptom_list:
            if symptom in user_input.lower():
                cold_symptoms.append(symptom)
                cold_score += 0.2  # Tăng điểm nếu phát hiện triệu chứng

        disease_scores["cold"] = cold_score
        disease_matches["cold"] = cold_match
        disease_symptoms["cold"] = cold_symptoms

    # Flu
    if "flu" in kb:
        flu_score = 0
        flu_match = None
        flu_symptoms = []
        
        for topic in kb["flu"]["topics"]:
            # Check topic name
            topic_score = similarity(user_input, topic["name"])
            if topic_score > flu_score:
                flu_score = topic_score
                flu_match = {
                    "question": topic["name"],
                    "answer": format_flu_info(topic["information"])
                }

            # Check information content
            if isinstance(topic["information"], dict):
                for key, value in topic["information"].items():
                    if isinstance(value, str):
                        content_score = similarity(user_input, value)
                        if content_score > flu_score:
                            flu_score = content_score
                            flu_match = {
                                "question": topic["name"],
                                "answer": format_flu_info(topic["information"])
                            }

        # Analyze flu symptoms
        flu_symptom_list = ["sốt cao", "ớn lạnh", "đau cơ", "mệt mỏi", "ho", "đau họng", "đau đầu", "sổ mũi", "lạnh"]
        for symptom in flu_symptom_list:
            if symptom in user_input.lower():
                flu_symptoms.append(symptom)
                flu_score += 0.2  # Tăng điểm nếu phát hiện triệu chứng

        disease_scores["flu"] = flu_score
        disease_matches["flu"] = flu_match
        disease_symptoms["flu"] = flu_symptoms

    # Allergy
    if "allergy" in kb:
        allergy_score = 0
        allergy_match = None
        allergy_symptoms = []
        
        for topic in kb["allergy"]["topics"]:
            # Check topic name
            topic_score = similarity(user_input, topic["name"])
            if topic_score > allergy_score:
                allergy_score = topic_score
                allergy_match = {
                    "question": topic["name"],
                    "answer": format_allergy_info(topic["information"], specific_symptom)
                }

            # Check information content
            if isinstance(topic["information"], dict):
                for key, value in topic["information"].items():
                    if isinstance(value, str):
                        content_score = similarity(user_input, value)
                        if content_score > allergy_score:
                            allergy_score = content_score
                            allergy_match = {
                                "question": topic["name"],
                                "answer": format_allergy_info(topic["information"], specific_symptom)
                            }

        # Analyze allergy symptoms
        allergy_symptom_list = ["hắt hơi", "ngứa mũi", "chảy nước mũi", "ngứa mắt", "phát ban", "nổi mề đay", "ngứa da", "ngứa", "mẩn ngứa", "nổi mụn nước", "bong tróc da", "chàm"]
        for symptom in allergy_symptom_list:
            if symptom in user_input.lower():
                allergy_symptoms.append(symptom)
                allergy_score += 0.2  # Tăng điểm nếu phát hiện triệu chứng

        disease_scores["allergy"] = allergy_score
        disease_matches["allergy"] = allergy_match
        disease_symptoms["allergy"] = allergy_symptoms

    # Tìm bệnh có điểm cao nhất
    best_disease = max(disease_scores.items(), key=lambda x: x[1])
    if best_disease[1] > 0.3:  # Chỉ trả về kết quả nếu điểm số đủ cao
        return disease_matches[best_disease[0]], best_disease[0], disease_symptoms[best_disease[0]]
    
    return None, None, []


# Generate COVID-19 specific recommendations
def generate_covid_recommendations(symptoms, risk_level):
    base_recommendations = [
        "🏠 Cách ly tại nhà ít nhất 5 ngày",
        "😷 Đeo khẩu trang khi tiếp xúc với người khác",
        "🚰 Uống nhiều nước, nghỉ ngơi đầy đủ",
        "🌡️ Theo dõi thân nhiệt thường xuyên"
    ]

    if risk_level == "cao":
        base_recommendations.extend([
            "🏥 Liên hệ bác sĩ ngay lập tức",
            "📞 Gọi hotline COVID-19: 19009095",
            "⚠️ Đến bệnh viện nếu khó thở tăng"
        ])
    elif risk_level == "trung bình":
        base_recommendations.extend([
            "📞 Liên hệ trạm y tế địa phương",
            "🧪 Xem xét làm xét nghiệm COVID-19"
        ])

    return base_recommendations


# Main UI
def main():
    st.title("🏥 Hệ thống Tư vấn Sức khỏe AI")
    st.markdown("💬 **Hỏi đáp thông tin về các bệnh thường gặp với AI**")

    # Load knowledge base
    kb = load_knowledge_base()
    if not kb:
        st.stop()

    # Sidebar with quick info
    with st.sidebar:
        st.header("📋 Thông tin nhanh")
        st.markdown("""
        **Hotline khẩn cấp:**
        - 🚨 Cấp cứu: **115**
        - 📞 COVID-19: **19009095**
        - 🏥 Bộ Y tế: **19003228**

        **Triệu chứng cần cấp cứu:**
        - Khó thở nghiêm trọng
        - Đau ngực dai dẳng
        - Môi xanh tím
        - Lú lẫn, mất ý thức
        - Sốc phản vệ (dị ứng)
        - Sốt cao kéo dài
        """)

        st.markdown("---")
        st.markdown("**Phòng ngừa cơ bản:**")
        st.markdown("- 😷 Đeo khẩu trang khi cần")
        st.markdown("- 🧼 Rửa tay thường xuyên")
        st.markdown("- 📏 Giữ khoảng cách an toàn")
        st.markdown("- 💉 Tiêm vắc xin đầy đủ")
        st.markdown("- 🏠 Giữ ấm cơ thể")
        st.markdown("- 🥗 Ăn uống đầy đủ dinh dưỡng")
        st.markdown("- 🌿 Tránh các tác nhân gây dị ứng")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        # Add welcome message
        welcome_msg = "Xin chào! Tôi là trợ lý sức khỏe AI. Tôi có thể giúp bạn tìm hiểu thông tin về COVID-19, cảm lạnh, cúm, dị ứng và các vấn đề sức khỏe khác. Bạn muốn hỏi gì?"
        st.session_state.chat_history.append(("AI", welcome_msg))

    # Clear chat button
    if st.button("🗑️ Xóa cuộc trò chuyện"):
        # Xóa lịch sử chat
        st.session_state.chat_history = []
        # Thêm lại tin nhắn chào mừng
        welcome_msg = "Xin chào! Tôi là trợ lý sức khỏe AI. Tôi có thể giúp bạn tìm hiểu thông tin về COVID-19, cảm lạnh, cúm, dị ứng và các vấn đề sức khỏe khác. Bạn muốn hỏi gì?"
        st.session_state.chat_history.append(("AI", welcome_msg))
        # Xóa input của người dùng
        st.session_state.user_input = ""
        # Làm mới trang
        st.rerun()

    # Chat input
    user_input = st.text_input("💭 Bạn muốn hỏi gì về sức khỏe?", key="user_input")

    # Process user input
    if user_input:
        # Add user message to chat
        st.session_state.chat_history.append(("User", user_input))

        # Check for emergency
        if is_emergency(user_input):
            emergency_response = "⚠️ **CẢNH BÁO KHẨN CẤP!**\n\nVui lòng gọi ngay số cấp cứu 115 hoặc đến bệnh viện gần nhất nếu bạn đang gặp các triệu chứng nghiêm trọng như khó thở, đau ngực, môi xanh tím, hoặc mất ý thức."
            st.session_state.chat_history.append(("AI", emergency_response))
        else:
            # Find answer from knowledge base
            answer, matched_disease, detected_symptoms = find_best_answer(user_input, kb)

            if answer:
                response = f"**📋 {answer['question']}**\n\n{answer['answer']}"

                # Add disease-specific analysis if symptoms detected
                if detected_symptoms:
                    if matched_disease == "covid19":
                        risk_level, confidence = assess_covid_risk(detected_symptoms)
                        response += f"\n\n**🔍 Phân tích triệu chứng COVID-19:**"
                        response += f"\n- Triệu chứng phát hiện: {', '.join(detected_symptoms)}"
                        response += f"\n- Mức độ nguy cơ: **{risk_level}** ({int(confidence * 100)}%)"

                        # Add COVID-19 recommendations
                        recommendations = generate_covid_recommendations(detected_symptoms, risk_level)
                        response += f"\n\n**💊 Khuyến nghị cho COVID-19:**"
                        for rec in recommendations:
                            response += f"\n{rec}"
                    elif matched_disease == "cold":
                        response += f"\n\n**🔍 Phân tích triệu chứng cảm lạnh:**"
                        response += f"\n- Triệu chứng phát hiện: {', '.join(detected_symptoms)}"
                        response += f"\n- Khuyến nghị: Nghỉ ngơi, uống nhiều nước, giữ ấm cơ thể"
                    elif matched_disease == "flu":
                        response += f"\n\n**🔍 Phân tích triệu chứng cúm:**"
                        response += f"\n- Triệu chứng phát hiện: {', '.join(detected_symptoms)}"
                        response += f"\n- Khuyến nghị: Nghỉ ngơi, uống nhiều nước, dùng thuốc hạ sốt nếu cần"
                    elif matched_disease == "allergy":
                        response += f"\n\n**🔍 Phân tích triệu chứng dị ứng:**"
                        response += f"\n- Triệu chứng phát hiện: {', '.join(detected_symptoms)}"
                        response += f"\n- Khuyến nghị: Tránh tiếp xúc với tác nhân gây dị ứng, dùng thuốc kháng histamine nếu cần"

                # Add disclaimer
                response += f"\n\n⚠️ Lưu ý: Thông tin tôi cung cấp chỉ mang tính chất tham khảo. Để được chẩn đoán và điều trị chính xác, bạn cần tham khảo ý kiến bác sĩ hoặc cơ sở y tế có thẩm quyền."

            else:
                # Fallback response
                response = "Xin lỗi, tôi chưa có đủ thông tin để trả lời câu hỏi của bạn. Vui lòng thử hỏi lại theo cách khác hoặc liên hệ với bác sĩ để được tư vấn chi tiết hơn."

            st.session_state.chat_history.append(("AI", response))

    # Display chat history
    st.markdown("### 💬 Cuộc trò chuyện")
    chat_container = st.container()

    with chat_container:
        for i, (speaker, message) in enumerate(st.session_state.chat_history):
            if speaker == "User":
                st.markdown(
                    f"""
                    <div style="text-align: right; margin: 10px 0;">
                        <div style="display: inline-block; background-color: #007bff; color: white; 
                                    padding: 10px 15px; border-radius: 15px 15px 5px 15px; max-width: 70%;">
                            <strong>👤 Bạn:</strong> {message}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="text-align: left; margin: 10px 0;">
                        <div style="display: inline-block; background-color: #f8f9fa; color: black; 
                                    padding: 10px 15px; border-radius: 15px 15px 15px 5px; max-width: 70%;
                                    border-left: 4px solid #28a745;">
                            <strong>🤖 AI:</strong><br>{message}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Quick action buttons
    st.markdown("### 🚀 Câu hỏi gợi ý")
    col1, col2, col3, col4 = st.columns(4)

    quick_questions = [
        "Triệu chứng cúm là gì?",
        "Cách phòng ngừa dị ứng?",
        "Điều trị cảm lạnh tại nhà?",
        "Dấu hiệu sốc phản vệ?"
    ]

    cols = [col1, col2, col3, col4]
    for i, question in enumerate(quick_questions):
        if cols[i].button(question, key=f"quick_{i}"):
            st.session_state.chat_history.append(("User", question))
            st.rerun()


if __name__ == "__main__":
    main()